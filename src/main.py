import logging
import sys
from dataclasses import asdict, dataclass
from typing import Annotated, Literal, TypeAlias, Self

import duckdb
from duckdb import DuckDBPyConnection
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator, ValidationError
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


# Cannot catch RequestValidationError as Depends() causes FastApi not to wrap ValidationError in RequestValidationError
@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    errors = [{"msg": e["msg"]} for e in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors})


class FilterParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    start_year: int = Field(
        default=constants.PROCESSED_DATA_START_YEAR,
        ge=constants.RAW_DATA_START_YEAR,
        le=constants.RAW_DATA_END_YEAR,
    )
    end_year: int = Field(
        default=constants.PROCESSED_DATA_END_YEAR,
        ge=constants.RAW_DATA_START_YEAR,
        le=constants.RAW_DATA_END_YEAR,
    )
    pos_tag: PosTag | None = None

    @model_validator(mode="after")
    def check_year_order(self) -> Self:
        if self.start_year > self.end_year:
            raise ValueError(
                f"start_year ({self.start_year}) must be <= end_year ({self.end_year})"
            )

        return self


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


# TODO: Create a list of words to exclude from the word list
# TODO: Apply pos_tag filter using POS_TAG_MAP
@app.get("/top-words")
async def get_top_words(
    filter_params: Annotated[FilterParams, Depends()],
    word_number: Annotated[int, Query(ge=1, le=1000)] = 50,
) -> FrequencyResponse:

    if filter_params.start_year > filter_params.end_year:
        raise HTTPException(status_code=400, detail="start_year must be <= end_year")

    using_preprocessed = (
        filter_params.start_year == constants.PROCESSED_DATA_START_YEAR
        and filter_params.end_year == constants.PROCESSED_DATA_END_YEAR
    )

    if using_preprocessed:
        table = Table(constants.PREPROCESSED_TABLE_NAME)
        sql = _build_preprocessed_query(table, word_number)
    else:
        table = Table(constants.UNPROCESSED_TABLE_NAME)
        sql = _build_unprocessed_query(
            table, word_number, filter_params.start_year, filter_params.end_year
        )

    logger.info("Executing query: %s", sql)

    with duckdb.connect(database=constants.DB_NAME, read_only=True) as db:
        rows = db.execute(sql)
        response = _build_response(rows)

    logger.info("Response: %s", asdict(response))

    return response
