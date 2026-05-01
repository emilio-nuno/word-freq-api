"""Tests for public functions in main.py."""

from pypika import Table

import src.constants as src_constants
import tests.constants as test_constants

from src.main import (
    DateRange,
    FrequencyResponse,
    WordEntry,
    is_within_preprocessed_range,
    build_preprocessed_query,
    build_unprocessed_query,
    build_preprocessed_word_query,
    build_unprocessed_word_query,
    build_single_response,
    build_words_response,
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


def test_start_year_before_preprocessed_range():
    assert not is_within_preprocessed_range(
        DateRange(
            src_constants.RAW_DATA_START_YEAR, src_constants.PROCESSED_DATA_END_YEAR
        )
    )


# --- build_query (top words) ---


# TODO: Put in integration tests
def test_build_top_words_query_uses_preprocessed_table():
    table = Table(src_constants.PREPROCESSED_TABLE_NAME)

    sql = build_preprocessed_query(table, test_constants.SAMPLE_TOPWORDS_WORD_LIMIT)

    assert src_constants.PREPROCESSED_TABLE_NAME in sql
    assert src_constants.UNPROCESSED_TABLE_NAME not in sql


def test_build_top_words_query_uses_unprocessed_table():
    table = Table(src_constants.UNPROCESSED_TABLE_NAME)
    date_range = DateRange(
        src_constants.RAW_DATA_START_YEAR, src_constants.RAW_DATA_END_YEAR
    )

    sql = build_unprocessed_query(
        table, test_constants.SAMPLE_TOPWORDS_WORD_LIMIT, date_range
    )

    assert src_constants.UNPROCESSED_TABLE_NAME in sql
    assert src_constants.PREPROCESSED_TABLE_NAME not in sql

    assert str(test_constants.SAMPLE_TOPWORDS_WORD_LIMIT) in sql

    assert str(date_range.start_year) in sql
    assert str(date_range.end_year) in sql


# --- build_query (word freq) ---


def test_build_word_freq_query_uses_preprocessed_table():
    table = Table(src_constants.PREPROCESSED_TABLE_NAME)

    sql = build_preprocessed_word_query(table, test_constants.SAMPLE_PROCESSED_WORD)

    assert src_constants.PREPROCESSED_TABLE_NAME in sql
    assert src_constants.UNPROCESSED_TABLE_NAME not in sql

    assert test_constants.SAMPLE_PROCESSED_WORD in sql

    assert str(src_constants.PROCESSED_DATA_START_YEAR) in sql
    assert str(src_constants.PROCESSED_DATA_END_YEAR) in sql


# TODO: Perhaps could test with actual SQL sample
def test_build_word_freq_query_uses_unprocessed_table():
    table = Table(src_constants.UNPROCESSED_TABLE_NAME)

    date_range = DateRange(
        src_constants.RAW_DATA_START_YEAR, src_constants.RAW_DATA_END_YEAR
    )

    sql = build_unprocessed_word_query(
        table, test_constants.SAMPLE_UNPROCESSED_WORD, date_range
    )

    assert src_constants.UNPROCESSED_TABLE_NAME in sql
    assert src_constants.PREPROCESSED_TABLE_NAME not in sql

    assert str(test_constants.SAMPLE_UNPROCESSED_WORD) in sql

    assert str(date_range.start_year) in sql
    assert str(date_range.end_year) in sql


def test_build_single_word_response():
    sample_input = (
        test_constants.SAMPLE_PROCESSED_WORD,
        test_constants.SAMPLE_PROCESSED_WORD_COUNT,
    )

    assert build_single_response(sample_input) == WordEntry(
        sample_input[0], sample_input[1]
    )


def test_build_top_words_response():
    inputs = [
        (
            test_constants.SAMPLE_PROCESSED_WORD + "1",
            test_constants.SAMPLE_PROCESSED_WORD_COUNT + 1,
        ),
        (
            test_constants.SAMPLE_PROCESSED_WORD + "2",
            test_constants.SAMPLE_PROCESSED_WORD_COUNT + 2,
        ),
        (
            test_constants.SAMPLE_PROCESSED_WORD + "3",
            test_constants.SAMPLE_PROCESSED_WORD_COUNT + 3,
        ),
    ]
    processed_inputs: FrequencyResponse = build_words_response(inputs)

    assert len(processed_inputs.words) == len(inputs)

    for i, word_entry in enumerate(processed_inputs.words):
        assert word_entry == WordEntry(inputs[i][0], inputs[i][1])
