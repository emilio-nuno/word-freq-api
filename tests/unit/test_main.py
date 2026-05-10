"""Tests for public functions in main.py."""

from pypika import Table

import src.constants as src_constants

import tests.unit.constants as tests_unit

from src.main import (
    DateRange,
    is_within_preprocessed_range,
    build_preprocessed_query,
    build_unprocessed_query,
    build_preprocessed_word_query,
    build_unprocessed_word_query,
    build_single_response,
    build_words_response,
    build_preprocessed_words_query,
    build_unprocessed_words_query,
)

# --- is_within_preprocessed_range ---


def test_within_preprocessed_range():
    assert is_within_preprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_outside_preprocessed_range():
    assert not is_within_preprocessed_range(
        DateRange(src_constants.RAW_DATA_START_YEAR, src_constants.RAW_DATA_END_YEAR)
    )


def test_start_year_before_preprocessed_boundary():
    assert not is_within_preprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR - 1,
            src_constants.PROCESSED_DATA_END_YEAR,
        )
    )


def test_end_year_after_preprocessed_boundary():
    assert not is_within_preprocessed_range(
        DateRange(
            src_constants.PROCESSED_DATA_START_YEAR,
            src_constants.PROCESSED_DATA_END_YEAR + 1,
        )
    )


# --- build_query (top words) ---


def test_build_top_words_query_preprocessed_sql():

    table = Table(src_constants.PREPROCESSED_TABLE_NAME)

    sql = build_preprocessed_query(table, tests_unit.SAMPLE_TOPWORDS_WORD_LIMIT)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_TOPWORDS_QUERY_SQL


def test_build_top_words_query_unprocessed_sql():
    table = Table(src_constants.UNPROCESSED_TABLE_NAME)
    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_query(
        table, tests_unit.SAMPLE_TOPWORDS_WORD_LIMIT, date_range
    )

    assert sql == tests_unit.EXPECTED_UNPROCESSED_TOPWORDS_QUERY_SQL


# --- build_query (word freq) ---


def test_build_word_query_preprocessed_sql():
    table = Table(src_constants.PREPROCESSED_TABLE_NAME)

    sql = build_preprocessed_word_query(table, tests_unit.SAMPLE_PROCESSED_WORD)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_WORD_QUERY_SQL


def test_build_word_query_unprocessed_sql():
    table = Table(src_constants.UNPROCESSED_TABLE_NAME)

    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_word_query(
        table, tests_unit.SAMPLE_UNPROCESSED_WORD, date_range
    )

    assert sql == tests_unit.EXPECTED_UNPROCESSED_WORD_QUERY_SQL


# --- build_query (words-freq) ---


def test_build_words_query_preprocessed_sql():
    table = Table(src_constants.PREPROCESSED_TABLE_NAME)

    sql = build_preprocessed_words_query(table, tests_unit.SAMPLE_PROCESSED_WORDS)

    assert sql == tests_unit.EXPECTED_PREPROCESSED_WORDS_QUERY_SQL


def test_build_words_query_unprocessed_sql():
    table = Table(src_constants.UNPROCESSED_TABLE_NAME)

    date_range = DateRange(
        tests_unit.SAMPLE_UNPROCESSED_START_YEAR, tests_unit.SAMPLE_UNPROCESSED_END_YEAR
    )

    sql = build_unprocessed_words_query(
        table, tests_unit.SAMPLE_UNPROCESSED_WORDS, date_range
    )

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


# TODO Add test for the functions from the new endpoint
