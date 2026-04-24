from fastapi.testclient import TestClient
import src.constants as constants
from fastapi import status
from tests.constants import SAMPLE_PROCESSED_WORD, SAMPLE_UNPROCESSED_WORD
# --- Top Words Tests ---


def test_top_words_response_structure_default_params(client: TestClient):
    """Test response has correct structure."""
    response = client.get("/top-words")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert "words" in data
    assert isinstance(data["words"], list)
    assert len(data["words"]) > 0

    for word in data["words"]:
        assert isinstance(word, dict)
        assert "ngram" in word
        assert "count" in word
        assert isinstance(word["ngram"], str)
        assert isinstance(word["count"], int)


def test_top_words_status_code_default_params(client: TestClient):
    """Test endpoint with default parameters."""
    response = client.get("/top-words")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    response = client.get(f"/top-words?start_year={constants.RAW_DATA_START_YEAR}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    response = client.get(f"/top-words?end_year={constants.RAW_DATA_END_YEAR}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_END_YEAR}&end_year={constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_START_YEAR - 1}&end_year={constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_START_YEAR}&end_year={constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_word_limit_valid_accepts(client: TestClient):
    """Test endpoint with valid word_limit parameter."""
    response = client.get(f"/top-words?word_limit={constants.TOP_WORDS_DEFAULT_LIMIT}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_word_limit_minimum_boundary_accepts(client: TestClient):
    """Test word_limit=1 returns single result."""
    response = client.get(f"/top-words?word_limit={constants.TOP_WORDS_MIN_LIMIT}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_word_limit_maximum_boundary_accepts(client: TestClient):
    """Test word_limit=TOP_WORDS_MAX_LIMIT is accepted."""
    response = client.get(f"/top-words?word_limit={constants.TOP_WORDS_MAX_LIMIT}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_word_limit_zero_rejects(client: TestClient):
    """Test word_limit=0 returns 422."""
    response = client.get("/top-words?word_limit=0")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_word_limit_negative_rejects(client: TestClient):
    """Test negative word_limit returns 422."""
    response = client.get("/top-words?word_limit=-5")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_word_limit_above_maximum_rejects(client: TestClient):
    """Test word_limit > TOP_WORDS_MAX_LIMIT returns 422."""
    response = client.get(f"/top-words?word_limit={constants.TOP_WORDS_MAX_LIMIT + 1}")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- Word Freq Tests ---


def test_word_freq_response_structure_default_params(client: TestClient):
    """Test response has correct structure."""
    response = client.get(f"/word-freq?word={SAMPLE_PROCESSED_WORD}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert SAMPLE_PROCESSED_WORD in data["ngram"]
    assert isinstance(data, dict)
    assert len(data.keys()) == 2
    assert "ngram" in data
    assert "count" in data
    assert isinstance(data["ngram"], str)
    assert isinstance(data["count"], int)


def test_word_freq_word_required(client: TestClient):
    """Test word parameter is required."""
    response = client.get("/word-freq")
    assert response.status_code != status.HTTP_200_OK


def test_word_freq_status_code_default_params(client: TestClient):
    """Test endpoint with default parameters."""
    response = client.get(f"/word-freq?word={SAMPLE_PROCESSED_WORD}")
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    response = client.get(
        f"/word-freq?word={SAMPLE_UNPROCESSED_WORD}&start_year={constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    response = client.get(
        f"/word-freq?word={SAMPLE_UNPROCESSED_WORD}&end_year={constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    response = client.get(
        f"/word-freq?word={SAMPLE_UNPROCESSED_WORD}&start_year={constants.RAW_DATA_END_YEAR}&end_year={constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_word_freq_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    response = client.get(
        f"/word-freq?word={SAMPLE_UNPROCESSED_WORD}&start_year={constants.RAW_DATA_START_YEAR - 1}&end_year={constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_word_freq_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    response = client.get(
        f"/word-freq?word={SAMPLE_UNPROCESSED_WORD}&start_year={constants.RAW_DATA_START_YEAR}&end_year={constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
