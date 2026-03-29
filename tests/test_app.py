"""Tests for functions and logic in main.py."""
import duckdb
from pypika import Table

#TODO: Do we need to test internal methods? Could we test them through the public interface?

from src.main import (
    _build_response,
    _build_preprocessed_query,
    _build_unprocessed_query,
    WordEntry,
    FrequencyResponse,
)
import src.constants as constants


def test_build_response_with_data(in_memory_db: str):
    """Test _build_response converts DuckDB results to FrequencyResponse."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    
    # Query some data
    result = conn.execute(
        f"SELECT ngram, match_count FROM {constants.PREPROCESSED_TABLE_NAME} LIMIT 3"
    )
    
    response = _build_response(result)
    
    assert isinstance(response, FrequencyResponse)
    assert len(response.words) == 3
    assert all(isinstance(word, WordEntry) for word in response.words)
    assert response.words[0].ngram == "the"
    assert response.words[0].count == 1000000
    
    conn.close()


def test_build_response_empty(in_memory_db: str):
    """Test _build_response with empty result set."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    
    # Query that returns no results
    result = conn.execute(
        f"SELECT ngram, match_count FROM {constants.PREPROCESSED_TABLE_NAME} WHERE ngram = 'nonexistent'"
    )
    
    response = _build_response(result)
    
    assert isinstance(response, FrequencyResponse)
    assert len(response.words) == 0
    
    conn.close()


def test_build_preprocessed_query_structure():
    """Test _build_preprocessed_query generates correct SQL."""
    table = Table(constants.PREPROCESSED_TABLE_NAME)
    word_number = 50
    
    sql = _build_preprocessed_query(table, word_number)
    
    # Check SQL contains expected components
    assert constants.PREPROCESSED_TABLE_NAME in sql
    assert "ngram" in sql
    assert "match_count" in sql
    assert "ORDER BY" in sql.upper()
    assert "DESC" in sql.upper()
    assert "LIMIT 50" in sql


def test_build_preprocessed_query_different_limits():
    """Test _build_preprocessed_query with different word_number values."""
    table = Table(constants.PREPROCESSED_TABLE_NAME)
    
    sql_10 = _build_preprocessed_query(table, 10)
    assert "LIMIT 10" in sql_10
    
    sql_100 = _build_preprocessed_query(table, 100)
    assert "LIMIT 100" in sql_100


def test_build_preprocessed_query_execution(in_memory_db: str):
    """Test that generated preprocessed query executes correctly."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    table = Table(constants.PREPROCESSED_TABLE_NAME)
    
    sql = _build_preprocessed_query(table, 5)
    result = conn.execute(sql)
    rows = result.fetchall()
    
    assert len(rows) == 5
    # Check ordering (descending by count)
    assert rows[0][1] >= rows[1][1]
    assert rows[1][1] >= rows[2][1]
    
    conn.close()


def test_build_unprocessed_query_structure():
    """Test _build_unprocessed_query generates correct SQL."""
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    word_number = 50
    start_year = 2000
    end_year = 2010
    
    sql = _build_unprocessed_query(table, word_number, start_year, end_year)
    
    # Check SQL contains expected components
    assert constants.UNPROCESSED_TABLE_NAME in sql
    assert "ngram" in sql
    assert "SUM" in sql.upper()
    assert "match_count" in sql
    assert "WHERE" in sql.upper()
    assert "BETWEEN" in sql.upper()
    assert str(start_year) in sql
    assert str(end_year) in sql
    assert "GROUP BY" in sql.upper()
    assert "ORDER BY" in sql.upper()
    assert "DESC" in sql.upper()
    assert "LIMIT 50" in sql


def test_build_unprocessed_query_different_years():
    """Test _build_unprocessed_query with different year ranges."""
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    
    sql_2000_2010 = _build_unprocessed_query(table, 50, 2000, 2010)
    assert "2000" in sql_2000_2010
    assert "2010" in sql_2000_2010
    
    sql_1500_1600 = _build_unprocessed_query(table, 50, 1500, 1600)
    assert "1500" in sql_1500_1600
    assert "1600" in sql_1500_1600


def test_build_unprocessed_query_execution(in_memory_db: str):
    """Test that generated unprocessed query executes correctly."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    
    # Query for years 2000-2001
    sql = _build_unprocessed_query(table, 5, 2000, 2001)
    result = conn.execute(sql)
    rows = result.fetchall()
    
    assert len(rows) > 0
    # Check that results are aggregated (SUM)
    # "the" should have 50000 + 51000 = 101000
    the_row = [row for row in rows if row[0] == "the"][0]
    assert the_row[1] == 101000
    
    conn.close()


def test_build_unprocessed_query_single_year(in_memory_db: str):
    """Test unprocessed query for a single year."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    
    # Query for year 2000 only
    sql = _build_unprocessed_query(table, 10, 2000, 2000)
    result = conn.execute(sql)
    rows = result.fetchall()
    
    assert len(rows) > 0
    # "the" in 2000 should be exactly 50000
    the_row = [row for row in rows if row[0] == "the"][0]
    assert the_row[1] == 50000
    
    conn.close()


def test_build_unprocessed_query_historical_range(in_memory_db: str):
    """Test unprocessed query for historical year range."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    
    # Query for years 1500-1600
    sql = _build_unprocessed_query(table, 10, 1500, 1600)
    result = conn.execute(sql)
    rows = result.fetchall()
    
    # Should only return words from that period
    ngrams = [row[0] for row in rows]
    assert "past" in ngrams
    assert "ancient" in ngrams
    # Modern words should not be in this range
    assert "modern" not in ngrams
    
    conn.close()


def test_build_unprocessed_query_ordering(in_memory_db: str):
    """Test that unprocessed query results are ordered by count descending."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    table = Table(constants.UNPROCESSED_TABLE_NAME)
    
    sql = _build_unprocessed_query(table, 10, 2000, 2019)
    result = conn.execute(sql)
    rows = result.fetchall()
    
    # Check that results are in descending order
    counts = [row[1] for row in rows]
    assert counts == sorted(counts, reverse=True)
    
    conn.close()


def test_query_limit_respected(in_memory_db: str):
    """Test that LIMIT clause is respected in queries."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    
    # Test preprocessed query
    table_preprocessed = Table(constants.PREPROCESSED_TABLE_NAME)
    sql_preprocessed = _build_preprocessed_query(table_preprocessed, 3)
    result = conn.execute(sql_preprocessed)
    rows = result.fetchall()
    assert len(rows) == 3
    
    # Test unprocessed query
    table_unprocessed = Table(constants.UNPROCESSED_TABLE_NAME)
    sql_unprocessed = _build_unprocessed_query(table_unprocessed, 5, 2000, 2019)
    result = conn.execute(sql_unprocessed)
    rows = result.fetchall()
    assert len(rows) == 5
    
    conn.close()


def test_preprocessed_vs_unprocessed_data_difference(in_memory_db: str):
    """Test that preprocessed and unprocessed queries return different results for different ranges."""
    conn = duckdb.connect(in_memory_db, read_only=True)
    
    # Preprocessed query (2000-2019 aggregated)
    table_preprocessed = Table(constants.PREPROCESSED_TABLE_NAME)
    sql_preprocessed = _build_preprocessed_query(table_preprocessed, 1)
    result_preprocessed = conn.execute(sql_preprocessed)
    preprocessed_count = result_preprocessed.fetchall()[0][1]
    
    # Unprocessed query for subset (2000-2001)
    table_unprocessed = Table(constants.UNPROCESSED_TABLE_NAME)
    sql_unprocessed = _build_unprocessed_query(table_unprocessed, 1, 2000, 2001)
    result_unprocessed = conn.execute(sql_unprocessed)
    unprocessed_count = result_unprocessed.fetchall()[0][1]
    
    # Preprocessed should have higher count (covers more years)
    assert preprocessed_count > unprocessed_count
    
    conn.close()
