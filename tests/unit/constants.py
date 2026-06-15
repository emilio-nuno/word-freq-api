from typing import Final
import src.constants as src_constants
from src.main import FrequencyResponse, WordEntry

SAMPLE_UNPROCESSED_START_YEAR: Final[int] = 1950
SAMPLE_UNPROCESSED_END_YEAR: Final[int] = 1970

SAMPLE_MIXED_START_YEAR: Final[int] = 1990
SAMPLE_MIXED_END_YEAR: Final[int] = 2019

SAMPLE_WORD_LIMIT: Final[int] = 5
SAMPLE_WORD: Final[str] = "word"
SAMPLE_WORDS: Final[list[str]] = ["word1", "word2"]

_QP = f'"{src_constants.DB_NAME}"."{src_constants.PREPROCESSED_TABLE_NAME}"'
_QU = f'"{src_constants.DB_NAME}"."{src_constants.UNPROCESSED_TABLE_NAME}"'

EXPECTED_PREPROCESSED_TOPWORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM {_QP} ORDER BY "match_count" DESC LIMIT {SAMPLE_WORD_LIMIT}'
)
EXPECTED_UNPROCESSED_TOPWORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM {_QU} WHERE "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} GROUP BY "ngram" ORDER BY SUM("match_count") DESC LIMIT {SAMPLE_WORD_LIMIT}'
)
EXPECTED_MIXED_TOPWORDS_QUERY_SQL: Final[str] = (
    f'SELECT "combined"."ngram",SUM("combined"."match_count") FROM ((SELECT "ngram",SUM("match_count") "match_count" FROM {_QU} WHERE "year" BETWEEN {SAMPLE_MIXED_START_YEAR} AND {SAMPLE_MIXED_END_YEAR} AND NOT "year" BETWEEN {src_constants.PROCESSED_DATA_START_YEAR} AND {src_constants.PROCESSED_DATA_END_YEAR} GROUP BY "ngram") UNION ALL (SELECT "ngram","match_count" FROM {_QP})) "combined" GROUP BY "combined"."ngram" ORDER BY SUM("combined"."match_count") DESC LIMIT {SAMPLE_WORD_LIMIT}'
)

EXPECTED_PREPROCESSED_WORD_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM {_QP} WHERE "ngram"=\'{SAMPLE_WORD}\''
)
EXPECTED_UNPROCESSED_WORD_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM {_QU} WHERE "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} AND "ngram"=\'{SAMPLE_WORD}\' GROUP BY "ngram" ORDER BY SUM("match_count") DESC'
)
EXPECTED_MIXED_WORD_QUERY_SQL: Final[str] = (
    f'SELECT "combined"."ngram",SUM("combined"."match_count") FROM ((SELECT "ngram",SUM("match_count") "match_count" FROM {_QU} WHERE "year" BETWEEN {SAMPLE_MIXED_START_YEAR} AND {SAMPLE_MIXED_END_YEAR} AND NOT "year" BETWEEN {src_constants.PROCESSED_DATA_START_YEAR} AND {src_constants.PROCESSED_DATA_END_YEAR} AND "ngram"=\'{SAMPLE_WORD}\' GROUP BY "ngram") UNION ALL (SELECT "ngram","match_count" FROM {_QP} WHERE "ngram"=\'{SAMPLE_WORD}\')) "combined" GROUP BY "combined"."ngram"'
)

EXPECTED_PREPROCESSED_WORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram","match_count" FROM {_QP} WHERE "ngram" IN (\'{SAMPLE_WORDS[0]}\',\'{SAMPLE_WORDS[1]}\') ORDER BY "match_count" DESC'
)
EXPECTED_UNPROCESSED_WORDS_QUERY_SQL: Final[str] = (
    f'SELECT "ngram",SUM("match_count") FROM {_QU} WHERE "ngram" IN (\'{SAMPLE_WORDS[0]}\',\'{SAMPLE_WORDS[1]}\') AND "year" BETWEEN {SAMPLE_UNPROCESSED_START_YEAR} AND {SAMPLE_UNPROCESSED_END_YEAR} GROUP BY "ngram" ORDER BY SUM("match_count") DESC'
)
EXPECTED_MIXED_WORDS_QUERY_SQL: Final[str] = (
    f'SELECT "combined"."ngram",SUM("combined"."match_count") FROM ((SELECT "ngram",SUM("match_count") "match_count" FROM {_QU} WHERE "year" BETWEEN {SAMPLE_MIXED_START_YEAR} AND {SAMPLE_MIXED_END_YEAR} AND NOT "year" BETWEEN {src_constants.PROCESSED_DATA_START_YEAR} AND {src_constants.PROCESSED_DATA_END_YEAR} AND "ngram" IN (\'{SAMPLE_WORDS[0]}\',\'{SAMPLE_WORDS[1]}\') GROUP BY "ngram") UNION ALL (SELECT "ngram","match_count" FROM {_QP} WHERE "ngram" IN (\'{SAMPLE_WORDS[0]}\',\'{SAMPLE_WORDS[1]}\'))) "combined" GROUP BY "combined"."ngram" ORDER BY SUM("combined"."match_count") DESC'
)

SAMPLE_SINGLE_RESPONSE_WORD: Final[str] = "sample"
SAMPLE_SINGLE_RESPONSE_WORD_COUNT: Final[int] = 1000000

SAMPLE_SINGLE_WORD_RESPONSE_INPUT: Final[tuple[str, int]] = (
    SAMPLE_SINGLE_RESPONSE_WORD,
    SAMPLE_SINGLE_RESPONSE_WORD_COUNT,
)
EXPECTED_SINGLE_WORD_RESPONSE_OUTPUT: Final[WordEntry] = WordEntry(
    SAMPLE_SINGLE_RESPONSE_WORD, SAMPLE_SINGLE_RESPONSE_WORD_COUNT
)

SAMPLE_MULTIPLE_RESPONSE_INPUT: Final[list[tuple[str, int]]] = [
    ("foo1", 1),
    ("foo2", 2),
    ("foo3", 3),
]
EXPECTED_MULTIPLE_WORD_RESPONSE_OUTPUT: Final[FrequencyResponse] = FrequencyResponse(
    words=[
        WordEntry("foo1", 1),
        WordEntry("foo2", 2),
        WordEntry("foo3", 3),
    ]
)
