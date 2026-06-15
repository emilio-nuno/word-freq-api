from enum import Enum
from functools import partial, singledispatch
import logging
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Callable, Final, Iterable, Protocol, TypeAlias, Self, cast

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pypika import Order
from pypika import Query as PikaQuery
from pypika import Table
from pypika import functions as fn
from opentelemetry import trace
from opentelemetry.instrumentation.auto_instrumentation import initialize

initialize()

from fastapi import Depends, FastAPI, Query

from src import constants
from src.db import build_executor, execute
from src.settings import Settings, get_settings


tracer = trace.get_tracer(__name__)

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


@dataclass(frozen=True)
class DateRange:
    start_year: int
    end_year: int


PREPROCESSED_TABLE: Final = Table(
    constants.PREPROCESSED_TABLE_NAME, schema=constants.DB_NAME
)
PREPROCESSED_DATE_RANGE: Final = DateRange(
    constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
)
RAW_TABLE: Final = Table(constants.UNPROCESSED_TABLE_NAME, schema=constants.DB_NAME)


class PosTag(str, Enum):
    ADJECTIVE = "Adjective"
    ADPOSITION = "Adposition"
    VERB = "Verb"
    NOUN = "Noun"
    ADVERB = "Adverb"
    CONJUNCTION = "Conjunction"


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
                f"start_year ({self.start_year}) must be < end_year ({self.end_year})"
            )
        return self


# TODO: May not be needed
class SearchParams(CommonParams):
    pos_tag: PosTag | None = None


# FastAPI only accepts one Pydantic model as query parameter
# TODO: Remove
class TopWordsParams(SearchParams):
    word_limit: int = Field(
        ge=constants.TOP_WORDS_MIN_LIMIT,
        le=constants.TOP_WORDS_MAX_LIMIT,
        default=constants.TOP_WORDS_DEFAULT_LIMIT,
    )


class WordFreqParams(SearchParams):
    word: str


class WordInfo(BaseModel):
    name: str
    tag: PosTag


class WordsFreqParams(CommonParams):
    words: Annotated[
        list[
            Annotated[
                str,
                Field(pattern=constants.ENGLISH_REGEX, examples=["word", "word_NOUN"]),
            ]
        ],
        Field(min_length=1),
    ]


@dataclass(frozen=True)
class WordEntry:
    ngram: str
    count: int


@dataclass(frozen=True)
class FrequencyResponse:
    words: list[WordEntry]


# TODO: Could this be done in an easier way?
EndpointSerializer: TypeAlias = WordEntry | FrequencyResponse
# TODO: Could probably just reference CommonParams ancestor
EndpointParams: TypeAlias = TopWordsParams | WordFreqParams | WordsFreqParams
# TODO: Create a list of words to exclude from the word list
# TODO: This is not quite async
# TODO: Create custom typealias for list[tuple[str, int]], perhaps WordEntry could work? But that is only a serializer


class SqlFn(Protocol):
    def __call__(self) -> str: ...


class ResponseFn(Protocol):
    def __call__(self, rows: list[tuple[str, int]]) -> EndpointSerializer: ...


class ExecuteFn(Protocol):
    def __call__(self, sql: str) -> list[tuple[str, int]]: ...


@dataclass(frozen=True)
class QueryBuilderSet:
    top_n: Callable[[int], str]
    word: Callable[[str], str]
    words: Callable[[list[str]], str]


def preprocessed_builders() -> QueryBuilderSet:
    return QueryBuilderSet(
        top_n=build_preprocessed_query,
        word=build_preprocessed_word_query,
        words=build_preprocessed_words_query,
    )


def unprocessed_builders(date_range: DateRange) -> QueryBuilderSet:
    return QueryBuilderSet(
        top_n=partial(build_unprocessed_query, date_range=date_range),
        word=partial(build_unprocessed_word_query, date_range=date_range),
        words=partial(build_unprocessed_words_query, date_range=date_range),
    )


def mixed_builders(date_range: DateRange) -> QueryBuilderSet:
    return QueryBuilderSet(
        top_n=partial(build_mixed_query, date_range=date_range),
        word=partial(build_mixed_word_query, date_range=date_range),
        words=partial(build_mixed_words_query, date_range=date_range),
    )


def get_query_builder(
    query_date_range: DateRange,
    processed_date_range: DateRange = PREPROCESSED_DATE_RANGE,
) -> QueryBuilderSet:

    current_span = trace.get_current_span()

    if is_processed_range(query_date_range, processed_date_range):
        current_span.set_attribute("range_type", "processed")
        return preprocessed_builders()

    elif is_mixed_range(query_date_range, processed_date_range):
        current_span.set_attribute("range_type", "mixed")
        return mixed_builders(query_date_range)

    elif is_unprocessed_range(query_date_range, processed_date_range):
        current_span.set_attribute("range_type", "unprocessed")
        return unprocessed_builders(query_date_range)

    else:
        raise ValueError(
            f"No query builder strategy recognized for date range {query_date_range} "
            f"against processed range {processed_date_range}"
        )


def build_words_response(rows: Iterable[tuple[str, int]]) -> FrequencyResponse:
    return FrequencyResponse(words=[WordEntry(entry[0], entry[1]) for entry in rows])


def build_preprocessed_query(
    word_number: int, preprocessed_table: Table = PREPROCESSED_TABLE
) -> str:
    current_span = trace.get_current_span()

    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {preprocessed_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{preprocessed_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .orderby(preprocessed_table.match_count, order=Order.desc)
        .limit(word_number)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_unprocessed_query(
    word_number: int, date_range: DateRange, unprocessed_table: Table = RAW_TABLE
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {unprocessed_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{unprocessed_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(unprocessed_table)
        .select(unprocessed_table.ngram, fn.Sum(unprocessed_table.match_count))
        .where(
            unprocessed_table.year.between(date_range.start_year, date_range.end_year)
        )
        .groupby(unprocessed_table.ngram)
        .orderby(fn.Sum(unprocessed_table.match_count), order=Order.desc)
        .limit(word_number)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_mixed_query(
    word_number: int,
    date_range: DateRange,
    preprocessed_table: Table = PREPROCESSED_TABLE,
    raw_table: Table = RAW_TABLE,
    preprocessed_date_range: DateRange = DateRange(
        constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
    ),
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT SELECT {raw_table.get_table_name()} SELECT {preprocessed_table.get_table_name()}",
    )
    raw = (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count).as_("match_count"))
        .where(raw_table.year.between(date_range.start_year, date_range.end_year))
        .where(
            raw_table.year.between(
                preprocessed_date_range.start_year, preprocessed_date_range.end_year
            ).negate()
        )
        .groupby(raw_table.ngram)
    )
    preprocessed = PikaQuery.from_(preprocessed_table).select(
        preprocessed_table.ngram, preprocessed_table.match_count
    )

    sub = raw.union_all(preprocessed).as_("combined")
    query = (
        PikaQuery.from_(sub)
        .select(sub.ngram, fn.Sum(sub.match_count))
        .groupby(sub.ngram)
        .orderby(fn.Sum(sub.match_count), order=Order.desc)
        .limit(word_number)
        .get_sql()
    )
    current_span.set_attribute("db.query.text", query)
    return query


def build_preprocessed_word_query(
    word: str, preprocessed_table: Table = PREPROCESSED_TABLE
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {preprocessed_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{preprocessed_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .where(preprocessed_table.ngram == word)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_unprocessed_word_query(
    word: str, date_range: DateRange, raw_table: Table = RAW_TABLE
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {raw_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{raw_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count))
        .where(
            raw_table.year.between(date_range.start_year, date_range.end_year)
            & (raw_table.ngram == word)
        )
        .groupby(raw_table.ngram)
        .orderby(fn.Sum(raw_table.match_count), order=Order.desc)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_mixed_word_query(
    word: str,
    date_range: DateRange,
    preprocessed_table: Table = PREPROCESSED_TABLE,
    raw_table: Table = RAW_TABLE,
    preprocessed_date_range: DateRange = DateRange(
        constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
    ),
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT SELECT {raw_table.get_table_name()} SELECT {preprocessed_table.get_table_name()}",
    )
    raw = (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count).as_("match_count"))
        .where(raw_table.year.between(date_range.start_year, date_range.end_year))
        .where(
            raw_table.year.between(
                preprocessed_date_range.start_year, preprocessed_date_range.end_year
            ).negate()
        )
        .where(raw_table.ngram == word)
        .groupby(raw_table.ngram)
    )
    preprocessed = (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .where(preprocessed_table.ngram == word)
    )
    sub = raw.union_all(preprocessed).as_("combined")
    query = (
        PikaQuery.from_(sub)
        .select(sub.ngram, fn.Sum(sub.match_count))
        .groupby(sub.ngram)
        .get_sql()
    )
    current_span.set_attribute("db.query.text", query)
    return query


def build_preprocessed_words_query(
    words: list[str], preprocessed_table: Table = PREPROCESSED_TABLE
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {preprocessed_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{preprocessed_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .where(preprocessed_table.ngram.isin(words))
        .orderby(preprocessed_table.match_count, order=Order.desc)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_unprocessed_words_query(
    words: list[str], date_range: DateRange, raw_table: Table = RAW_TABLE
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT {raw_table.get_table_name()}",
    )
    current_span.set_attribute(
        "db.collection.name",
        f"{constants.DB_NAME}.{raw_table.get_table_name()}",
    )

    query = (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count))
        .where(
            raw_table.ngram.isin(words)
            & raw_table.year.between(date_range.start_year, date_range.end_year)
        )
        .groupby(raw_table.ngram)
        .orderby(fn.Sum(raw_table.match_count), order=Order.desc)
        .get_sql()
    )

    current_span.set_attribute("db.query.text", query)

    return query


def build_mixed_words_query(
    words: list[str],
    date_range: DateRange,
    preprocessed_table: Table = PREPROCESSED_TABLE,
    raw_table: Table = RAW_TABLE,
    preprocessed_date_range: DateRange = DateRange(
        constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
    ),
) -> str:
    current_span = trace.get_current_span()
    current_span.set_attribute(
        "db.query.summary",
        f"SELECT SELECT {raw_table.get_table_name()} SELECT {preprocessed_table.get_table_name()}",
    )
    raw = (
        PikaQuery.from_(raw_table)
        .select(raw_table.ngram, fn.Sum(raw_table.match_count).as_("match_count"))
        .where(raw_table.year.between(date_range.start_year, date_range.end_year))
        .where(
            raw_table.year.between(
                preprocessed_date_range.start_year, preprocessed_date_range.end_year
            ).negate()
        )
        .where(raw_table.ngram.isin(words))
        .groupby(raw_table.ngram)
    )
    preprocessed = (
        PikaQuery.from_(preprocessed_table)
        .select(preprocessed_table.ngram, preprocessed_table.match_count)
        .where(preprocessed_table.ngram.isin(words))
    )
    sub = raw.union_all(preprocessed).as_("combined")
    query = (
        PikaQuery.from_(sub)
        .select(sub.ngram, fn.Sum(sub.match_count))
        .groupby(sub.ngram)
        .orderby(fn.Sum(sub.match_count), order=Order.desc)
        .get_sql()
    )
    current_span.set_attribute("db.query.text", query)
    return query


def build_single_response(row: tuple[str, int]) -> WordEntry:

    return WordEntry(
        row[0],
        row[1],
    )


def is_processed_range(
    query_date_range: DateRange,
    processed_date_range: DateRange = PREPROCESSED_DATE_RANGE,
) -> bool:
    """Check if a given range is exactly the date range for processed data"""
    return (
        query_date_range.start_year == processed_date_range.start_year
        and query_date_range.end_year == processed_date_range.end_year
    )


def is_mixed_range(
    query_date_range: DateRange,
    processed_date_range: DateRange = PREPROCESSED_DATE_RANGE,
) -> bool:
    """Check if a given range contains the processed range in its entirety"""
    return (
        query_date_range.start_year <= processed_date_range.start_year
        and query_date_range.end_year >= processed_date_range.end_year
        and not is_processed_range(query_date_range)
    )


def is_unprocessed_range(
    query_date_range: DateRange,
    processed_date_range: DateRange = PREPROCESSED_DATE_RANGE,
) -> bool:
    """Check if a given range does not completely overlap with the processed range"""
    return (
        query_date_range.start_year > processed_date_range.start_year
        or query_date_range.end_year < processed_date_range.end_year
    )


# TODO: Use sqlglot to translate between duckdb and bigquery
# TODO: Rename

SettingsDep = Annotated[Settings, Depends(get_settings)]


@singledispatch
def process_request(
    params: object, settings: Settings, query_ctx: QueryBuilderSet
) -> EndpointSerializer:
    raise NotImplementedError(f"No handler for {type(params)}")


@process_request.register
def _(
    params: TopWordsParams, settings: Settings, query_builder: QueryBuilderSet
) -> FrequencyResponse:
    return cast(
        FrequencyResponse,
        run_query(
            sql_fn=lambda: query_builder.top_n(params.word_limit),
            execute_fn=lambda sql: execute(build_executor(sql, settings)),
            response_fn=build_words_response,
        ),
    )


@process_request.register
def _(
    params: WordFreqParams, settings: Settings, query_builder: QueryBuilderSet
) -> WordEntry:
    return cast(
        WordEntry,
        run_query(
            sql_fn=lambda: query_builder.word(params.word),
            execute_fn=lambda sql: execute(build_executor(sql, settings)),
            response_fn=lambda rows: build_single_response(rows[0]),
        ),
    )


@process_request.register
def _(
    params: WordsFreqParams, settings: Settings, query_builder: QueryBuilderSet
) -> FrequencyResponse:

    return cast(
        FrequencyResponse,
        run_query(
            sql_fn=lambda: query_builder.words(params.words),
            execute_fn=lambda sql: execute(build_executor(sql, settings)),
            response_fn=lambda rows: build_words_response(rows),
        ),
    )


def prepare_request_processing(
    params_obj: CommonParams,
    settings: Settings,
) -> EndpointSerializer:
    date_range = DateRange(params_obj.start_year, params_obj.end_year)
    query_builder = get_query_builder(date_range)
    return process_request(params_obj, settings, query_builder)


def run_query(
    sql_fn: SqlFn,
    response_fn: ResponseFn,
    execute_fn: ExecuteFn,
) -> EndpointSerializer:
    with tracer.start_as_current_span(
        "SELECT ngrams",
        kind=trace.SpanKind.CLIENT,
        attributes={"db.operation.name": "SELECT"},
    ) as span:
        sql = sql_fn()
        rows = execute_fn(sql)
        span.set_attribute("db.response.returned_rows", len(rows))

        summary = getattr(span, "attributes", {}).get("db.query.summary")
        if summary:
            span.update_name(str(summary))

        return response_fn(rows)


@app.get("/top-words")
async def get_top_words(
    params: Annotated[TopWordsParams, Query()],
    settings: SettingsDep,
) -> FrequencyResponse:
    response = cast(FrequencyResponse, prepare_request_processing(params, settings))
    return response


@app.get("/word-freq")
async def get_word_freq(
    params: Annotated[WordFreqParams, Query()],
    settings: SettingsDep,
) -> WordEntry:
    response = cast(WordEntry, prepare_request_processing(params, settings))
    logger.info("Response: %s", asdict(response))
    return response


@app.get("/words-freq")
async def get_words_freq(
    params: Annotated[WordsFreqParams, Query()], settings: SettingsDep
) -> FrequencyResponse:

    response = cast(FrequencyResponse, prepare_request_processing(params, settings))
    logger.info("Response: %s", asdict(response))

    return response
