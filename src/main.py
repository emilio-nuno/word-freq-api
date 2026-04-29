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
class DateRangeParams:
    start_year: int
    end_year: int


def build_words_response(rows: Iterable[tuple[str, int]]) -> FrequencyResponse:
    return FrequencyResponse(words=[WordEntry(entry[0], entry[1]) for entry in rows])


def _build_preprocessed_query(table: Table, word_number: int) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, table.match_count)
        .orderby(table.match_count, order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def _build_unprocessed_query(
    table: Table, word_number: int, date_range: DateRangeParams
) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, fn.Sum(table.match_count))
        .where(table.year.between(date_range.start_year, date_range.end_year))
        .groupby(table.ngram)
        .orderby(fn.Sum(table.match_count), order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def _build_preprocessed_word_query(table: Table, word: str) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, table.match_count)
        .where(table.ngram == word)
        .get_sql()
    )


def _build_unprocessed_word_query(
    table: Table, word: str, date_range: DateRangeParams
) -> str:
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


def _is_within_preprocessed_range(date_range: DateRangeParams) -> bool:
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
    def __call__(self, date_range: DateRangeParams) -> str: ...


class ResponseFn(Protocol):
    def __call__(self, rows: list[tuple[str, int]]) -> EndpointSerializer: ...


def _run_query(
    date_range: DateRangeParams,
    settings: Settings,
    preprocessed_fn: PreprocessedFn,
    unprocessed_fn: UnprocessedFn,
    response_fn: ResponseFn,
) -> EndpointSerializer:
    sql = (
        preprocessed_fn()
        if _is_within_preprocessed_range(date_range)
        else unprocessed_fn(date_range)
    )
    logger.info("Executing query: %s", sql)
    executor = build_executor(sql, settings)
    return response_fn(execute(executor))


@singledispatch
def process_request(params: object, settings: Settings) -> EndpointSerializer:
    raise NotImplementedError(f"No handler for {type(params)}")


@process_request.register
def _(params: TopWordsParams, settings: Settings) -> FrequencyResponse:
    dr = DateRangeParams(params.start_year, params.end_year)
    pre_table = Table(constants.PREPROCESSED_TABLE_NAME)
    raw_table = Table(constants.UNPROCESSED_TABLE_NAME)
    return cast(
        FrequencyResponse,
        _run_query(
            dr,
            settings,
            preprocessed_fn=lambda: _build_preprocessed_query(
                pre_table, params.word_limit
            ),
            unprocessed_fn=lambda date_range: _build_unprocessed_query(
                raw_table, params.word_limit, date_range
            ),
            response_fn=build_words_response,
        ),
    )


@process_request.register
def _(params: WordFreqParams, settings: Settings) -> WordEntry:
    dr = DateRangeParams(params.start_year, params.end_year)
    pre_table = Table(constants.PREPROCESSED_TABLE_NAME)
    raw_table = Table(constants.UNPROCESSED_TABLE_NAME)
    return cast(
        WordEntry,
        _run_query(
            dr,
            settings,
            preprocessed_fn=lambda: _build_preprocessed_word_query(
                pre_table, params.word
            ),
            unprocessed_fn=lambda date_range: _build_unprocessed_word_query(
                raw_table, params.word, date_range
            ),
            response_fn=lambda rows: build_single_response(rows[0]),
        ),
    )


@app.get("/top-words")
async def get_top_words(
    params: Annotated[TopWordsParams, Query()],
    settings: SettingsDep,
) -> FrequencyResponse:
    response = cast(FrequencyResponse, process_request(params, settings))
    logger.info("Response: %s", asdict(response))
    return response


@app.get("/word-freq")
async def get_word_freq(
    params: Annotated[WordFreqParams, Query()],
    settings: SettingsDep,
) -> WordEntry:
    response = cast(WordEntry, process_request(params, settings))
    logger.info("Response: %s", asdict(response))
    return response
