import os
import tempfile
from fastapi.testclient import TestClient
import pytest

# TODO: Remove and use abstractions
import duckdb
import src.constants as constants
from typing import Generator
from src.settings import get_settings, Settings, Envs
from tests.constants import DUCKDB_DB_PATH


@pytest.fixture(scope="module")
def build_test_db() -> Generator[str]:
    """
    Create an in-memory DuckDB database with test data.
    """
    # TODO: Check if we could do this with in-memory database
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_db_path: str = os.path.join(temp_dir, DUCKDB_DB_PATH)

        with duckdb.connect(temp_db_path) as conn:
            conn.execute(f"""
                CREATE TABLE {constants.PREPROCESSED_TABLE_NAME} (
                    ngram VARCHAR,
                    match_count BIGINT
                )
            """)

            preprocessed_data = [
                ("the", 1000000),
                ("and", 800000),
                ("of", 600000),
                ("to", 400000),
                ("a", 300000),
                ("in", 250000),
                ("is", 200000),
                ("it", 150000),
                ("that", 100000),
                ("for", 90000),
            ]

            conn.executemany(
                f"INSERT INTO {constants.PREPROCESSED_TABLE_NAME} VALUES (?, ?)",
                preprocessed_data,
            )

            conn.execute(f"""
                CREATE TABLE {constants.UNPROCESSED_TABLE_NAME} (
                    ngram VARCHAR,
                    year INTEGER,
                    match_count BIGINT
                )
            """)

            unprocessed_data = [
                ("the", 2000, 50000),
                ("the", 2001, 51000),
                ("the", 2010, 52000),
                ("the", 2018, 48000),
                ("the", 2019, 49000),
                ("and", 2000, 40000),
                ("and", 2005, 41000),
                ("and", 2010, 42000),
                ("and", 2019, 43000),
                ("future", 1990, 5000),
                ("future", 2000, 6000),
                ("future", 2015, 7000),
                ("future", 2019, 8000),
                ("past", 1500, 3000),
                ("past", 1600, 3500),
                ("past", 2000, 4000),
                ("past", 2019, 4500),
                ("modern", 2015, 2000),
                ("modern", 2016, 2100),
                ("modern", 2017, 2200),
                ("modern", 2018, 2300),
                ("modern", 2019, 2400),
                ("ancient", 1470, 1000),
                ("ancient", 1500, 1100),
                ("ancient", 1600, 1200),
                ("word1", 2000, 10000),
                ("word2", 2000, 9000),
                ("word3", 2000, 8000),
                ("word4", 2000, 7000),
                ("word5", 2000, 6000),
            ]

            conn.executemany(
                f"INSERT INTO {constants.UNPROCESSED_TABLE_NAME} VALUES (?, ?, ?)",
                unprocessed_data,
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
