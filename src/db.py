from contextlib import contextmanager
from dataclasses import dataclass
from functools import singledispatch
from typing import Generator, Protocol, cast

from duckdb import DuckDBPyConnection
from google.cloud.bigquery import Client

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


@contextmanager
def _get_duckdb_connection(executor: DuckDBData) -> Generator[DuckDBPyConnection]:
    import duckdb

    conn = duckdb.connect(database=executor.db_path, read_only=True)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def _get_bigquery_connection(executor: BigqueryData) -> Generator[Client]:
    from google.cloud import bigquery

    client = bigquery.Client(project=executor.project_id)
    try:
        yield client
    finally:
        client.close()


# TODO: Used prepare statements for SQL
# TODO: User input must be lowercased and sanitized


@singledispatch
def execute(executor: object) -> list[tuple[str, int]]:
    raise NotImplementedError(f"No executor for {type(executor)}")


@execute.register
def _(executor: BigqueryData) -> list[tuple[str, int]]:
    return [("placeholder", -9999)]


@execute.register
def _(executor: DuckDBData) -> list[tuple[str, int]]:

    with _get_duckdb_connection(executor) as db:
        # TODO: Add check to see if query result is empty
        # TODO: Swap out functions for OOP interfaces
        db = cast(DuckDBPyConnection, db)
        row = db.execute(executor.sql).fetchall()

    return row


# TODO: Remove SQL parameter from here
def build_executor(sql: str, settings: Settings) -> DBExecutorData:
    if settings.is_dev:
        return DuckDBData(sql=sql, db_path=settings.duckdb_path or ":memory:")
    elif settings.is_prod:
        return BigqueryData(sql=sql, project_id=settings.project_id or "dummy_project")
    else:
        raise ValueError("Unknown environment")
