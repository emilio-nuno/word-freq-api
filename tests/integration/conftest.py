import os
import tempfile
from fastapi.testclient import TestClient
import pytest

# TODO: Remove and use abstractions
import duckdb
import src.constants as src_constants
from typing import Generator
from src.settings import get_settings, Settings, Envs
from tests.constants import (
    SAMPLE_DB_PATH,
    SAMPLE_PROCESSED_DATA,
    SAMPLE_UNPROCESSED_DATA,
)


@pytest.fixture(scope="module")
def build_test_db() -> Generator[str]:
    """
    Create an in-memory DuckDB database with test data.
    """
    # TODO: Check if we could do this with in-memory database
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path: str = os.path.join(temp_dir, SAMPLE_DB_PATH)

        with duckdb.connect(temp_db_path) as conn:
            conn.execute(f"""
                CREATE TABLE {src_constants.PREPROCESSED_TABLE_NAME} (
                    ngram VARCHAR,
                    match_count BIGINT
                )
            """)

            conn.executemany(
                f"INSERT INTO {src_constants.PREPROCESSED_TABLE_NAME} VALUES (?, ?)",
                SAMPLE_PROCESSED_DATA,
            )

            conn.execute(f"""
                CREATE TABLE {src_constants.UNPROCESSED_TABLE_NAME} (
                    ngram VARCHAR,
                    year INTEGER,
                    match_count BIGINT
                )
            """)

            conn.executemany(
                f"INSERT INTO {src_constants.UNPROCESSED_TABLE_NAME} VALUES (?, ?, ?)",
                SAMPLE_UNPROCESSED_DATA,
            )

        yield temp_db_path


@pytest.fixture(scope="module")
def client(build_test_db: str) -> TestClient:
    """
    Creates the FastAPI test client
    """
    from src.main import app

    app.dependency_overrides[get_settings] = lambda: Settings(
        env=Envs.DEV,
        duckdb_path=build_test_db,
    )

    client = TestClient(app)

    return client
