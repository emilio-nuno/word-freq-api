from typing import Final

# TODO: Change values so that sum of processed range in unprocessed matches processed data sums

SAMPLE_PROCESSED_DATA: Final[list[tuple[str, int]]] = [
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

SAMPLE_UNPROCESSED_DATA: Final[list[tuple[str, int, int]]] = [
    ("the", 2000, 50000),
    ("the", 2001, 51000),
    ("the", 2010, 52000),
    ("the", 2018, 48000),
    ("the", 2019, 49000),
    ("and", 1998, 32000),
    ("and", 1999, 500000),
    ("and", 2000, 40000),
    ("and", 2005, 41000),
    ("and", 2010, 42000),
    ("and", 2019, 43000),
    ("and", 2020, 32000),
    ("and", 2021, 60239),
    ("future", 1999, 5000),
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
SAMPLE_DB_PATH: Final[str] = "test.duckdb"

SAMPLE_UNPROCESSED_START_YEAR: Final[int] = 1990
SAMPLE_UNPROCESSED_END_YEAR: Final[int] = 2015

SAMPLE_MIXED_START_YEAR: Final[int] = 1999
SAMPLE_MIXED_END_YEAR: Final[int] = 2019


# Default is 50, but test dataset is 10 rows, so we return entire dataset
SAMPLE_TOPWORDS_WORD_LIMIT: Final[int] = 5
SAMPLE_PROCESSED_TOPWORDS_DEFAULT_RESPONSE: Final[
    dict[str, list[dict[str, str | int]]]
] = {
    "words": [
        {"ngram": "the", "count": 1000000},
        {"ngram": "and", "count": 800000},
        {"ngram": "of", "count": 600000},
        {"ngram": "to", "count": 400000},
        {"ngram": "a", "count": 300000},
        {"ngram": "in", "count": 250000},
        {"ngram": "is", "count": 200000},
        {"ngram": "it", "count": 150000},
        {"ngram": "that", "count": 100000},
        {"ngram": "for", "count": 90000},
    ]
}

SAMPLE_PROCESSED_TOPWORDS_QUERY_RESPONSE: Final[
    dict[str, list[dict[str, str | int]]]
] = {
    "words": [
        {"ngram": "the", "count": 1000000},
        {"ngram": "and", "count": 800000},
        {"ngram": "of", "count": 600000},
        {"ngram": "to", "count": 400000},
        {"ngram": "a", "count": 300000},
    ]
}
SAMPLE_UNPROCESSED_TOPWORDS_QUERY_RESPONSE: Final[
    dict[str, list[dict[str, str | int]]]
] = {
    "words": [
        {"ngram": "and", "count": 655000},
        {"ngram": "the", "count": 153000},
        {"ngram": "future", "count": 18000},
        {"ngram": "word1", "count": 10000},
        {"ngram": "word2", "count": 9000},
    ]
}
SAMPLE_MIXED_TOPWORDS_QUERY_RESPONSE: Final[dict[str, list[dict[str, str | int]]]] = {
    "words": [
        {"ngram": "and", "count": 1300000},
        {"ngram": "the", "count": 1000000},
        {"ngram": "of", "count": 600000},
        {"ngram": "to", "count": 400000},
        {"ngram": "a", "count": 300000},
    ]
}


SAMPLE_PROCESSED_WORD: Final[str] = "the"
SAMPLE_PROCESSED_WORD_COUNT: Final[int] = 1000000
SAMPLE_PROCESSED_WORD_RESPONSE: Final[dict[str, int | str]] = {
    "ngram": SAMPLE_PROCESSED_WORD,
    "count": SAMPLE_PROCESSED_WORD_COUNT,
}

SAMPLE_UNPROCESSED_WORD: Final[str] = "the"
SAMPLE_UNPROCESSED_WORD_COUNT: Final[int] = 153000
SAMPLE_UNPROCESSED_WORD_RESPONSE: Final[dict[str, int | str]] = {
    "ngram": SAMPLE_UNPROCESSED_WORD,
    "count": SAMPLE_UNPROCESSED_WORD_COUNT,
}
SAMPLE_MIXED_WORD: Final[str] = "and"
SAMPLE_MIXED_WORD_COUNT: Final[int] = 1300000
SAMPLE_MIXED_WORD_RESPONSE: Final[dict[str, int | str]] = {
    "ngram": SAMPLE_MIXED_WORD,
    "count": SAMPLE_MIXED_WORD_COUNT,
}

SAMPLE_PROCESSED_WORDS: Final[tuple[str, str]] = ("the", "and")
SAMPLE_PROCESSED_WORDS_COUNTS: Final[tuple[int, int]] = (1000000, 800000)
SAMPLE_PROCESSED_WORDS_QUERY_RESPONSE: Final[dict[str, list[dict[str, str | int]]]] = {
    "words": [
        {"ngram": SAMPLE_PROCESSED_WORDS[0], "count": SAMPLE_PROCESSED_WORDS_COUNTS[0]},
        {"ngram": SAMPLE_PROCESSED_WORDS[1], "count": SAMPLE_PROCESSED_WORDS_COUNTS[1]},
    ]
}

SAMPLE_UNPROCESSED_WORDS: Final[tuple[str, str]] = ("future", "past")
SAMPLE_UNPROCESSED_WORDS_COUNTS: Final[tuple[int, int]] = (18000, 4000)
SAMPLE_UNPROCESSED_WORDS_QUERY_RESPONSE: Final[
    dict[str, list[dict[str, str | int]]]
] = {
    "words": [
        {
            "ngram": SAMPLE_UNPROCESSED_WORDS[0],
            "count": SAMPLE_UNPROCESSED_WORDS_COUNTS[0],
        },
        {
            "ngram": SAMPLE_UNPROCESSED_WORDS[1],
            "count": SAMPLE_UNPROCESSED_WORDS_COUNTS[1],
        },
    ]
}

SAMPLE_MIXED_WORDS: Final[tuple[str, str]] = ("and", "future")
SAMPLE_MIXED_WORDS_COUNTS: Final[tuple[int, int]] = (1300000, 5000)
SAMPLE_MIXED_WORDS_QUERY_RESPONSE: Final[dict[str, list[dict[str, str | int]]]] = {
    "words": [
        {"ngram": SAMPLE_MIXED_WORDS[0], "count": SAMPLE_MIXED_WORDS_COUNTS[0]},
        {"ngram": "future", "count": SAMPLE_MIXED_WORDS_COUNTS[1]},
    ]
}
