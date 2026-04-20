import logging
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Literal, TypeAlias, Self

import duckdb
from duckdb import DuckDBPyConnection
from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pypika import Order
from pypika import Query as PikaQuery
from pypika import Table
from pypika import functions as fn

from src import constants

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

PosTag: TypeAlias = Literal[
    "Adjective", "Adposition", "Verb", "Noun", "Adverb", "Conjunction"
]

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
        default=constants.PROCESSED_DATA_START_YEAR,
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


@dataclass(frozen=True)
class WordEntry:
    ngram: str
    count: int


@dataclass(frozen=True)
class FrequencyResponse:
    words: list[WordEntry]


def _build_response(rows: DuckDBPyConnection) -> FrequencyResponse:
    return FrequencyResponse(
        words=[WordEntry(entry[0], entry[1]) for entry in rows.fetchall()]
    )


def _build_preprocessed_query(table: Table, word_number: int) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, table.match_count)
        .orderby(table.match_count, order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def _build_unprocessed_query(
    table: Table, word_number: int, start_year: int, end_year: int
) -> str:
    return (
        PikaQuery.from_(table)
        .select(table.ngram, fn.Sum(table.match_count))
        .where(table.year.between(start_year, end_year))
        .groupby(table.ngram)
        .orderby(fn.Sum(table.match_count), order=Order.desc)
        .limit(word_number)
        .get_sql()
    )


def is_within_preprocessed_range(start_year: int, end_year: int) -> bool:
    return (
        start_year >= constants.PROCESSED_DATA_START_YEAR
        and end_year <= constants.PROCESSED_DATA_END_YEAR
    )


def build_query(start_year: int, end_year: int, word_number: int) -> str:

    using_preprocessed = is_within_preprocessed_range(start_year, end_year)

    if using_preprocessed:
        table = Table(constants.PREPROCESSED_TABLE_NAME)
        sql = _build_preprocessed_query(table, word_number)
    else:
        table = Table(constants.UNPROCESSED_TABLE_NAME)
        sql = _build_unprocessed_query(table, word_number, start_year, end_year)

    return sql


# TODO: Create a list of words to exclude from the word list
# TODO: Apply pos_tag filter using POS_TAG_MAP
# TODO: This is not quite async
@app.get("/top-words")
async def get_top_words(
    params: Annotated[TopWordsParams, Query()],
) -> FrequencyResponse:

    # TODO: Decouple function from Pydantic
    sql = build_query(params.start_year, params.end_year, params.word_limit)

    logger.info("Executing query: %s", sql)

    with duckdb.connect(database=constants.DB_NAME, read_only=True) as db:
        rows = db.execute(sql)
        response = _build_response(rows)

    logger.info("Response: %s", asdict(response))

    return response
