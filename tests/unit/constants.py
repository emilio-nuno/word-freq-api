from typing import Final
import src.constants as src_constants
from src.main import FrequencyResponse, WordEntry

SAMPLE_UNPROCESSED_START_YEAR: Final[int] = 1990
SAMPLE_UNPROCESSED_END_YEAR: Final[int] = 2015

SAMPLE_TOPWORDS_WORD_LIMIT: Final[int] = 5
EXPECTED_PREPROCESSED_TOPWORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM "{src_constants.PREPROCESSED_TABLE_NAME}" ORDER BY "match_count" DESC LIMIT {SAMPLE_TOPWORDS_WORD_LIMIT}'
)
EXPECTED_UNPROCESSED_TOPWORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM "{src_constants.UNPROCESSED_TABLE_NAME}" WHERE "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} GROUP BY "ngram" ORDER BY SUM("match_count") DESC LIMIT {SAMPLE_TOPWORDS_WORD_LIMIT}'
)


SAMPLE_PROCESSED_WORD: Final[str] = "the"
SAMPLE_UNPROCESSED_WORD: Final[str] = "and"

EXPECTED_PREPROCESSED_WORD_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM "{src_constants.PREPROCESSED_TABLE_NAME}" WHERE "ngram"=\'{SAMPLE_PROCESSED_WORD}\''
)
EXPECTED_UNPROCESSED_WORD_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM "{src_constants.UNPROCESSED_TABLE_NAME}" WHERE "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} AND "ngram"=\'{SAMPLE_UNPROCESSED_WORD}\' GROUP BY "ngram" ORDER BY SUM("match_count") DESC'
)


SAMPLE_PROCESSED_WORDS: Final[list[str]] = ["the", "and"]
SAMPLE_UNPROCESSED_WORDS: Final[list[str]] = ["future", "past"]

EXPECTED_PREPROCESSED_WORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM "{src_constants.PREPROCESSED_TABLE_NAME}" WHERE "ngram" IN (\'{SAMPLE_PROCESSED_WORDS[0]}\',\'{SAMPLE_PROCESSED_WORDS[1]}\') ORDER BY "match_count" DESC'
)
EXPECTED_UNPROCESSED_WORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM "{src_constants.UNPROCESSED_TABLE_NAME}" WHERE "ngram" IN (\'{SAMPLE_UNPROCESSED_WORDS[0]}\',\'{SAMPLE_UNPROCESSED_WORDS[1]}\') AND "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} GROUP BY "ngram" ORDER BY SUM("match_count") DESC'
)
SAMPLE_WORD_COUNT: Final[int] = 1000000

SAMPLE_SINGLE_WORD_RESPONSE_INPUT: Final[tuple[str, int]] = (
    SAMPLE_PROCESSED_WORD,
    SAMPLE_WORD_COUNT,
)
EXPECTED_SINGLE_WORD_RESPONSE_OUTPUT: Final[WordEntry] = WordEntry(
    SAMPLE_PROCESSED_WORD,
    SAMPLE_WORD_COUNT,
)

SAMPLE_MULTIPLE_RESPONSE_INPUT: Final[list[tuple[str, int]]] = [
    ("the1", 1),
    ("the2", 2),
    ("the3", 3),
]

EXPECTED_MULTIPLE_WORD_RESPONSE_OUTPUT: Final[FrequencyResponse] = FrequencyResponse(
    words=[
        WordEntry("the1", 1),
        WordEntry("the2", 2),
        WordEntry("the3", 3),
    ]
)
