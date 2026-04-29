"""Tests for public functions in main.py."""

import src.constants as constants
from src.main import (
    DateRangeParams,
    _is_within_preprocessed_range,
)


# --- is_within_preprocessed_range ---


def test_within_preprocessed_range():
    assert _is_within_preprocessed_range(
        DateRangeParams(
            constants.PROCESSED_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
        )
    )


def test_outside_preprocessed_range():
    assert not _is_within_preprocessed_range(
        DateRangeParams(constants.RAW_DATA_START_YEAR, constants.RAW_DATA_END_YEAR)
    )


def test_start_year_before_preprocessed_range():
    assert not _is_within_preprocessed_range(
        DateRangeParams(
            constants.RAW_DATA_START_YEAR, constants.PROCESSED_DATA_END_YEAR
        )
    )


# --- build_query (top words) ---

# TODO: To refactor
"""def test_build_top_words_query_uses_preprocessed_table():
    params = TopWordsParams(
        start_year=constants.PROCESSED_DATA_START_YEAR,
        end_year=constants.PROCESSED_DATA_END_YEAR,
        word_limit=constants.TOP_WORDS_DEFAULT_LIMIT,
    )
    sql = build_query(get_top_word_query_type(params))
    assert constants.PREPROCESSED_TABLE_NAME in sql
    assert constants.UNPROCESSED_TABLE_NAME not in sql


def test_build_top_words_query_uses_unprocessed_table():
    params = TopWordsParams(
        start_year=constants.RAW_DATA_START_YEAR,
        end_year=constants.RAW_DATA_END_YEAR,
        word_limit=constants.TOP_WORDS_DEFAULT_LIMIT,
    )
    sql = build_query(get_top_word_query_type(params))
    assert constants.UNPROCESSED_TABLE_NAME in sql
    assert constants.PREPROCESSED_TABLE_NAME not in sql

# --- build_query (word freq) ---


def test_build_word_freq_query_uses_preprocessed_table():
    params = WordFreqParams(
        start_year=constants.PROCESSED_DATA_START_YEAR,
        end_year=constants.PROCESSED_DATA_END_YEAR,
        word=SAMPLE_PROCESSED_WORD,
    )
    sql = build_query(get_word_freq_query_type(params))
    assert constants.PREPROCESSED_TABLE_NAME in sql
    assert constants.UNPROCESSED_TABLE_NAME not in sql


def test_build_word_freq_query_uses_unprocessed_table():
    params = WordFreqParams(
        start_year=constants.RAW_DATA_START_YEAR,
        end_year=constants.RAW_DATA_END_YEAR,
        word=SAMPLE_UNPROCESSED_WORD,
    )
    sql = build_query(get_word_freq_query_type(params))
    assert constants.UNPROCESSED_TABLE_NAME in sql
    assert constants.PREPROCESSED_TABLE_NAME not in sql


def test_build_word_freq_query_includes_word():
    params = WordFreqParams(
        start_year=constants.PROCESSED_DATA_START_YEAR,
        end_year=constants.PROCESSED_DATA_END_YEAR,
        word=SAMPLE_PROCESSED_WORD,
    )
    sql = build_query(get_word_freq_query_type(params))
    assert SAMPLE_PROCESSED_WORD in sql
"""
