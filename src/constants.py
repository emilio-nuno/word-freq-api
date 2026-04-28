from typing import Final

# TODO: Prefer to pass constants as default params to functions, instead of from global scope

# Logic code
PROCESSED_DATA_START_YEAR: Final[int] = 2000
PROCESSED_DATA_END_YEAR: Final[int] = 2019

RAW_DATA_START_YEAR: Final[int] = 1470
RAW_DATA_END_YEAR: Final[int] = 2019

TOP_WORDS_DEFAULT_LIMIT: Final[int] = 50
TOP_WORDS_MIN_LIMIT: Final[int] = 1
TOP_WORDS_MAX_LIMIT: Final[int] = 1000

POS_TAG_MAP: Final[dict[str, str]] = {
    "Adjective": "_adj",
    "Adposition": "_adp",
    "Verb": "_verb",
    "Noun": "_noun",
    "Adverb": "_adv",
    "Conjunction": "_conj",
}

# DB constants
DB_NAME: Final[str] = "data/ngrams.duckdb"
PREPROCESSED_TABLE_NAME: Final[str] = "gold_ngram_2000_2022"
UNPROCESSED_TABLE_NAME: Final[str] = "gold_ngrams_sorted"
