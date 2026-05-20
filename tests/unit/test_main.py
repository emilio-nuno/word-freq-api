"""Tests for public functions in main.py."""

import src.constants as src_constants

import tests.unit.constants as tests_unit

from src.main import (
    DateRange,
    is_processed_range,
    is_mixed_range,
    is_unprocessed_range,
    build_preprocessed_query,
    build_mixed_query,
    build_unprocessed_query,
    build_preprocessed_word_query,
    build_mixed_word_query,
    build_unprocessed_word_query,
    build_single_response,
    build_words_response,
    build_preprocessed_words_query,
    build_mixed_words_query,
    build_unprocessed_words_query,
)

# --- is_within_preprocessed_range ---


def test_is_processed_range_exact_match_returns_true():
    assert is_processed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_is_processed_range_start_before_returns_false():
    assert not is_processed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR - 1,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_is_processed_range_end_after_returns_false():
    assert not is_processed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR + 1,
        )
    )


def test_is_processed_range_raw_start_to_proc_start_returns_false():
    assert not is_processed_range(
        DateRange(
            src_constants.RAW_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_START_YEAR,
        )
    )


def test_is_processed_range_proc_end_to_raw_end_returns_false():
    assert not is_processed_range(
        DateRange(
            src_constants.PROCESSED_DATA_END_YEAR,
            src_constants.RAW_DATA_END_YEAR,
        )
    )


def test_is_processed_range_inner_subset_returns_false():
    assert not is_processed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR + 1,
            src_constants.PROCESSED_DATA_END_YEAR - 1,
        )
    )


def test_is_mixed_range_start_at_proc_start_end_after_returns_true():
    assert is_mixed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR + 1,
        )
    )


def test_is_mixed_range_start_before_end_at_proc_end_returns_true():
    assert is_mixed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR - 1,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_is_mixed_range_raw_start_to_proc_start_returns_false():
    assert not is_mixed_range(
        DateRange(
            src_constants.RAW_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_START_YEAR,
        )
    )


def test_is_mixed_range_proc_end_to_raw_end_returns_false():
    assert not is_mixed_range(
        DateRange(
            src_constants.PROCESSED_DATA_END_YEAR,
            src_constants.RAW_DATA_END_YEAR,
        )
    )


def test_is_mixed_range_exact_processed_range_returns_false():
    assert not is_mixed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_is_mixed_range_inner_subset_returns_false():
    assert not is_mixed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR + 1,
            src_constants.PROCESSED_DATA_END_YEAR - 1,
        )
    )


def test_is_unprocessed_range_raw_start_to_proc_start_returns_true():
    assert is_unprocessed_range(
        DateRange(
            src_constants.RAW_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_START_YEAR,
        )
    )


def test_is_unprocessed_range_proc_end_to_raw_end_returns_true():
    assert is_unprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_END_YEAR,
            src_constants.RAW_DATA_END_YEAR,
        )
    )


def test_is_unprocessed_range_inner_subset_returns_true():
    assert is_unprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR + 1,
            src_constants.PROCESSED_DATA_END_YEAR - 1,
        )
    )


def test_is_unprocessed_range_exact_processed_range_returns_false():
    assert not is_unprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_is_unprocessed_range_wider_than_processed_returns_false():
    assert not is_unprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR - 1,
            src_constants.PROCESSED_DATA_END_YEAR + 1,
        )
    )


# --- build_query (top words) ---


def test_build_top_words_query_preprocessed_sql():

    sql = build_preprocessed_query(tests_unit.SAMPLE_WORD_LIMIT)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_TOPWORDS_QUERY_SQL


def test_build_top_words_query_mixed_sql():
    date_range = DateRange(
        tests_unit.SAMPLE_MIXED_START_YEAR, tests_unit.SAMPLE_MIXED_END_YEAR
    )

    sql = build_mixed_query(tests_unit.SAMPLE_WORD_LIMIT, date_range)

    assert sql == tests_unit.EXPECTED_MIXED_TOPWORDS_QUERY_SQL


def test_build_top_words_query_unprocessed_sql():
    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_query(tests_unit.SAMPLE_WORD_LIMIT, date_range)

    assert sql == tests_unit.EXPECTED_UNPROCESSED_TOPWORDS_QUERY_SQL


# --- build_query (word freq) ---


def test_build_word_query_preprocessed_sql():

    sql = build_preprocessed_word_query(tests_unit.SAMPLE_WORD)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_WORD_QUERY_SQL


def test_build_word_query_mixed_sql():

    date_range = DateRange(
        tests_unit.SAMPLE_MIXED_START_YEAR, tests_unit.SAMPLE_MIXED_END_YEAR
    )

    sql = build_mixed_word_query(tests_unit.SAMPLE_WORD, date_range)

    assert sql == tests_unit.EXPECTED_MIXED_WORD_QUERY_SQL


def test_build_word_query_unprocessed_sql():

    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_word_query(tests_unit.SAMPLE_WORD, date_range)

    assert sql == tests_unit.EXPECTED_UNPROCESSED_WORD_QUERY_SQL


# --- build_query (words-freq) ---


def test_build_words_query_preprocessed_sql():

    sql = build_preprocessed_words_query(tests_unit.SAMPLE_WORDS)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_WORDS_QUERY_SQL


def test_build_words_query_mixed_sql():

    date_range = DateRange(
        tests_unit.SAMPLE_MIXED_START_YEAR, tests_unit.SAMPLE_MIXED_END_YEAR
    )

    sql = build_mixed_words_query(tests_unit.SAMPLE_WORDS, date_range)

    assert sql == tests_unit.EXPECTED_MIXED_WORDS_QUERY_SQL


def test_build_words_query_unprocessed_sql():

    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_words_query(tests_unit.SAMPLE_WORDS, date_range)

    assert sql == tests_unit.EXPECTED_UNPROCESSED_WORDS_QUERY_SQL


def test_build_single_word_response():

    assert (
        build_single_response(tests_unit.SAMPLE_SINGLE_WORD_RESPONSE_INPUT)
        == tests_unit.EXPECTED_SINGLE_WORD_RESPONSE_OUTPUT
    )


def test_build_top_words_response():

    assert (
        build_words_response(tests_unit.SAMPLE_MULTIPLE_RESPONSE_INPUT)
        == tests_unit.EXPECTED_MULTIPLE_WORD_RESPONSE_OUTPUT
    )
