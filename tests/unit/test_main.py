"""Tests for public functions in main.py."""

import src.constants as constants
from src.main import (
    build_top_words_query,
    build_specific_word_query,
    is_within_preprocessed_range,
)
from tests.constants import SAMPLE_PROCESSED_WORD, SAMPLE_UNPROCESSED_WORD

# --- is_within_preprocessed_range ---


def test_within_preprocessed_range():
    assert is_within_preprocessed_range(
        constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
    )


def test_outside_preprocessed_range():
    assert not is_within_preprocessed_range(
        constants.RAW_DATA_START_YEAR, constants.RAW_DATA_END_YEAR
    )


def test_start_year_before_preprocessed_range():
    assert not is_within_preprocessed_range(
        constants.RAW_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
    )


# --- build_query ---


def test_build_query_uses_preprocessed_table():
    sql = build_top_words_query(
        constants.PROCESSED_DATA_START_YEAR,
        constants.PROCESSED_DATA_END_YEAR,
        constants.TOP_WORDS_DEFAULT_LIMIT,
    )
    assert constants.PREPROCESSED_TABLE_NAME in sql
    assert constants.UNPROCESSED_TABLE_NAME not in sql


def test_build_query_uses_unprocessed_table():
    sql = build_top_words_query(
        constants.RAW_DATA_START_YEAR,
        constants.RAW_DATA_END_YEAR,
        constants.TOP_WORDS_DEFAULT_LIMIT,
    )
    assert constants.UNPROCESSED_TABLE_NAME in sql
    assert constants.PREPROCESSED_TABLE_NAME not in sql


# --- build_specific_word_query ---


def test_build_specific_word_query_uses_preprocessed_table():
    sql = build_specific_word_query(
        constants.PROCESSED_DATA_START_YEAR,
        constants.PROCESSED_DATA_END_YEAR,
        SAMPLE_PROCESSED_WORD,
    )
    assert constants.PREPROCESSED_TABLE_NAME in sql
    assert constants.UNPROCESSED_TABLE_NAME not in sql


def test_build_specific_word_query_uses_unprocessed_table():
    sql = build_specific_word_query(
        constants.RAW_DATA_START_YEAR,
        constants.RAW_DATA_END_YEAR,
        SAMPLE_UNPROCESSED_WORD,
    )
    assert constants.UNPROCESSED_TABLE_NAME in sql
    assert constants.PREPROCESSED_TABLE_NAME not in sql


def test_build_specific_word_query_includes_word():
    sql = build_specific_word_query(
        constants.PROCESSED_DATA_START_YEAR,
        constants.PROCESSED_DATA_END_YEAR,
        SAMPLE_PROCESSED_WORD,
    )
    assert SAMPLE_PROCESSED_WORD in sql
