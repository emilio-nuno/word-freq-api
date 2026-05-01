from functools import singledispatch
import logging
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Iterable, Literal, Protocol, TypeAlias, Self, cast

from fastapi import Depends, FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pypika import Order
from pypika import Query as PikaQuery
from pypika import Table
from pypika import functions as fn

from src import constants
from src.db import build_executor, execute
from src.settings import Settings, get_settings

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

PosTag: TypeAlias = Literal[
    "Adjective", "Adposition", "Verb", "Noun", "Adverb", "Conjunction"
]


# TODO: Replace launch.json with container
# TODO: Add if TYPE_CHECKING checks to files for types only used for hints
# TODO: Make private functions that should remain private
app = FastAPI()


class CommonParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    start_year: int = Field(
        ge=constants.RAW_DATA_START_YEAR,
        le=constants.RAW_DATA_END_YEAR,
        default=constants.PROCESSED_DATA_START_YEAR,
    )
    end_year: int = Field(
        ge=constants.RAW_DATA_START_YEAR,
        le=constants.RAW_DATA_END_YEAR,
        default=constants.PROCESSED_DATA_END_YEAR,
    )

    @model_validator(mode="after")
    def check_year_order(self) -> Self:
        if self.start_year > self.end_year:
            raise ValueError(
                f"start_year ({self.start_year}) must be <= end_year ({self.end_year})"
            )
        return self


# TODO: Rename
class SearchParams(CommonParams):
    pos_tag: PosTag | None = None


# FastAPI only accepts one Pydantic model as query parameter
class TopWordsParams(SearchParams):
    word_limit: int = Field(
        ge=constants.TOP_WORDS_MIN_LIMIT,
        le=constants.TOP_WORDS_MAX_LIMIT,
        default=constants.TOP_WORDS_DEFAULT_LIMIT,
    )


class WordFreqParams(SearchParams):
    word: str


@dataclass(frozen=True)
class WordEntry:
    ngram: str
    count: int


@dataclass(frozen=True)
class FrequencyResponse:
    words: list[WordEntry]


EndpointSerializer: TypeAlias = WordEntry | FrequencyResponse
EndpointParams: TypeAlias = TopWordsParams | WordFreqParams


@dataclass(frozen=True)
class DateRange:
    start_year: int
    end_year: int


@dataclass(frozen=True)
class TableContext:
    pre_table: Table
    raw_table: Table


@dataclass(frozen=True)
class QueryContext:
    table_context: TableContext
    date_range: DateRange


def build_words_response(rows: Iterable[tuple[str, int]]) -> FrequencyResponse:
    return FrequencyResponse(words=[WordEntry(entry[0], entry[1]) for entry in rows])


def build_preprocessed_query(preprocessed_table: Table, word_number: int) -> str:
    return (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .orderby(preprocessed_table.match_count, order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def build_unprocessed_query(
    raw_table: Table, word_number: int, date_range: DateRange
) -> str:
    return (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count))
        .where(raw_table.year.between(date_range.start_year, date_range.end_year))
        .groupby(raw_table.ngram)
        .orderby(fn.Sum(raw_table.match_count), order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def build_preprocessed_word_query(table: Table, word: str) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, table.match_count)
        .where(table.ngram == word)
        .get_sql()
    )


def build_unprocessed_word_query(table: Table, word: str, date_range: DateRange) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, fn.Sum(table.match_count))
        .where(
            table.year.between(date_range.start_year, date_range.end_year) & table.ngram
            == word
        )
        .groupby(table.ngram)
        .orderby(fn.Sum(table.match_count), order=Order.desc)
        .get_sql()
    )


def build_single_response(row: tuple[str, int]) -> WordEntry:

    return WordEntry(
        row[0],
        row[1],
    )


def is_within_preprocessed_range(date_range: DateRange) -> bool:
    return (
        date_range.start_year >= constants.PROCESSED_DATA_START_YEAR
        and date_range.end_year <= constants.PROCESSED_DATA_END_YEAR
    )


# TODO: Use sqlglot to translate between duckdb and bigquery
# TODO: Rename

SettingsDep = Annotated[Settings, Depends(get_settings)]


# TODO: 2000-2019 works well, but 20005-2006 does not, for example.
# TODO: Create a list of words to exclude from the word list
# TODO: Apply pos_tag filter using POS_TAG_MAP
# TODO: This is not quite async
# TODO: Create custom typealias for list[tuple[str, int]], perhaps WordEntry could work? But that is only a serializer


class PreprocessedFn(Protocol):
    def __call__(self) -> str: ...


class UnprocessedFn(Protocol):
    def __call__(self) -> str: ...


class ResponseFn(Protocol):
    def __call__(self, rows: list[tuple[str, int]]) -> EndpointSerializer: ...


class ExecuteFn(Protocol):
    def __call__(self, sql: str) -> list[tuple[str, int]]: ...


def prepare_request_processing(
    params_obj: CommonParams,
    settings: Settings,
    pre_tab_name: str = constants.PREPROCESSED_TABLE_NAME,
    raw_tab_name: str = constants.UNPROCESSED_TABLE_NAME,
) -> EndpointSerializer:
    tab_ctx = TableContext(pre_table=Table(pre_tab_name), raw_table=Table(raw_tab_name))
    date_range = DateRange(params_obj.start_year, params_obj.end_year)
    query_ctx = QueryContext(tab_ctx, date_range)
    return process_request(params_obj, settings, query_ctx)


def run_query(
    date_range: DateRange,
    preprocessed_fn: PreprocessedFn,
    unprocessed_fn: UnprocessedFn,
    response_fn: ResponseFn,
    execute_fn: ExecuteFn,
) -> EndpointSerializer:
    sql = (
        preprocessed_fn()
        if is_within_preprocessed_range(date_range)
        else unprocessed_fn()
    )
    logger.info("Executing query: %s", sql)
    # executor = build_executor(sql, settings)
    return response_fn(execute_fn(sql))


@singledispatch
def process_request(
    params: object, settings: Settings, query_ctx: QueryContext
) -> EndpointSerializer:
    raise NotImplementedError(f"No handler for {type(params)}")


@process_request.register
def _(
    params: TopWordsParams, settings: Settings, query_ctx: QueryContext
) -> FrequencyResponse:
    # TODO: These could be defaults arguments
    return cast(
        FrequencyResponse,
        run_query(
            query_ctx.date_range,
            preprocessed_fn=lambda: build_preprocessed_query(
                query_ctx.table_context.pre_table, params.word_limit
            ),
            unprocessed_fn=lambda: build_unprocessed_query(
                query_ctx.table_context.raw_table,
                params.word_limit,
                query_ctx.date_range,
            ),
            execute_fn=lambda sql: execute(build_executor(sql, settings)),
            response_fn=build_words_response,
        ),
    )


@process_request.register
def _(params: WordFreqParams, settings: Settings, query_ctx: QueryContext) -> WordEntry:
    return cast(
        WordEntry,
        run_query(
            query_ctx.date_range,
            preprocessed_fn=lambda: build_preprocessed_word_query(
                query_ctx.table_context.pre_table, params.word
            ),
            unprocessed_fn=lambda: build_unprocessed_word_query(
                query_ctx.table_context.raw_table, params.word, query_ctx.date_range
            ),
            execute_fn=lambda sql: execute(build_executor(sql, settings)),
            response_fn=lambda rows: build_single_response(rows[0]),
        ),
    )


@app.get("/top-words")
async def get_top_words(
    params: Annotated[TopWordsParams, Query()],
    settings: SettingsDep,
) -> FrequencyResponse:
    response = cast(FrequencyResponse, prepare_request_processing(params, settings))
    logger.info("Response: %s", asdict(response))
    return response


@app.get("/word-freq")
async def get_word_freq(
    params: Annotated[WordFreqParams, Query()],
    settings: SettingsDep,
) -> WordEntry:
    response = cast(WordEntry, prepare_request_processing(params, settings))
    logger.info("Response: %s", asdict(response))
    return response
