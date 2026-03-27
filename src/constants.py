DB_NAME = "data/ngrams.duckdb"
PREPROCESSED_TABLE_NAME = "gold_ngram_2000_2022"
UNPROCESSED_TABLE_NAME = "gold_ngrams_sorted"

PROCESSED_DATA_START_YEAR = 2000
PROCESSED_DATA_END_YEAR = 2019

RAW_DATA_START_YEAR = 1470
RAW_DATA_END_YEAR = 2019

POS_TAG_MAP: dict[str, str] = {
    "Adjective": "_adj",
    "Adposition": "_adp",
    "Verb": "_verb",
    "Noun": "_noun",
    "Adverb": "_adv",
    "Conjunction": "_conj",
}