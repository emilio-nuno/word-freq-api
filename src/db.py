from dataclasses import dataclass
from functools import singledispatch
from typing import Protocol

from src.settings import Settings


class DBExecutorData(Protocol):
    sql: str


@dataclass
class BigqueryData:
    sql: str
    project_id: str = "dummy_project"


@dataclass
class DuckDBData:
    sql: str
    db_path: str = ":memory:"


# TODO: Used prepare statements for SQL
# TODO: User input must be lowercased and sanitized


@singledispatch
def execute_single_word_query(executor) -> tuple[str, int]:
    raise NotImplementedError(f"No executor for {type(executor)}")


@execute_single_word_query.register
def _(executor: BigqueryData) -> tuple[str, int]:
    return ("placeholder", -9999)


@execute_single_word_query.register
def _(executor: DuckDBData) -> tuple[str, int]:
    import duckdb

    with duckdb.connect(database=executor.db_path, read_only=True) as db:
        # TODO: Add check to see if query result is empty
        row = db.execute(executor.sql).fetchall()[0]

    return row


@singledispatch
def execute_multiple_word_query(executor) -> list[tuple[str, int]]:
    raise NotImplementedError(f"No executor for {type(executor)}")


@execute_multiple_word_query.register
def _(executor: BigqueryData) -> list[tuple[str, int]]:
    return [("placeholder", -9999)]


@execute_multiple_word_query.register
def _(executor: DuckDBData) -> list[tuple[str, int]]:
    import duckdb

    with duckdb.connect(database=executor.db_path, read_only=True) as db:
        # TODO: Add check to see if query result is empty
        row = db.execute(executor.sql).fetchall()

    return row


# TODO: Where do I document that DuckDB is for dev and Bigquery for prod?
def build_executor(sql: str, settings: Settings) -> BigqueryData | DuckDBData:
    if settings.is_dev:
        # TODO: How to make test data build in tests possible with this new abstraction?
        return DuckDBData(sql=sql, db_path=settings.duckdb_path or ":memory:")
    elif settings.is_prod:
        return BigqueryData(sql=sql, project_id=settings.project_id or "dummy_project")
    else:
        raise ValueError("Unknown environment")
