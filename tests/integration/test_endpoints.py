import src.constants as src_constants

import tests.integration.constants as tests_integration

from fastapi.testclient import TestClient
from fastapi import status

# --- Top Words Tests ---


def test_top_words_response_structure_default_params(client: TestClient):
    """Test response has correct structure."""

    response = client.get("/top-words")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_PROCESSED_TOPWORDS_DEFAULT_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_top_words_response_structure_processed_params(client: TestClient):
    """Test response has correct structure."""

    response = client.get(
        f"/top-words?word_limit={tests_integration.SAMPLE_TOPWORDS_WORD_LIMIT}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_PROCESSED_TOPWORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_top_words_response_structure_mixed_params(client: TestClient):
    """Test response has correct structure."""

    response = client.get(
        f"/top-words?word_limit={tests_integration.SAMPLE_TOPWORDS_WORD_LIMIT}&start_year={tests_integration.SAMPLE_MIXED_START_YEAR}&end_year={tests_integration.SAMPLE_MIXED_END_YEAR}"
    )

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_MIXED_TOPWORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_top_words_response_structure_unprocessed_params(client: TestClient):
    """Test response has correct structure."""

    response = client.get(
        f"/top-words?word_limit={tests_integration.SAMPLE_TOPWORDS_WORD_LIMIT}&start_year={tests_integration.SAMPLE_UNPROCESSED_START_YEAR}&end_year={tests_integration.SAMPLE_UNPROCESSED_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_UNPROCESSED_TOPWORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_top_words_status_code_default_params(client: TestClient):
    """Test endpoint with default parameters."""
    response = client.get("/top-words")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    response = client.get(f"/top-words?start_year={src_constants.RAW_DATA_START_YEAR}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    response = client.get(f"/top-words?end_year={src_constants.RAW_DATA_END_YEAR}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    response = client.get(
        f"/top-words?start_year={src_constants.RAW_DATA_END_YEAR}&end_year={src_constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={src_constants.RAW_DATA_START_YEAR - 1}&end_year={src_constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={src_constants.RAW_DATA_START_YEAR}&end_year={src_constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_top_words_word_limit_valid_accepts(client: TestClient):
    """Test endpoint with valid word_limit parameter."""
    response = client.get(
        f"/top-words?word_limit={src_constants.TOP_WORDS_DEFAULT_LIMIT}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_top_words_word_limit_minimum_boundary_accepts(client: TestClient):
    """Test word_limit=1 returns single result."""
    response = client.get(f"/top-words?word_limit={src_constants.TOP_WORDS_MIN_LIMIT}")
    assert response.status_code == status.HTTP_200_OK


def test_top_words_word_limit_maximum_boundary_accepts(client: TestClient):
    """Test word_limit=TOP_WORDS_MAX_LIMIT is accepted."""
    response = client.get(f"/top-words?word_limit={src_constants.TOP_WORDS_MAX_LIMIT}")
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
    response = client.get(
        f"/top-words?word_limit={src_constants.TOP_WORDS_MAX_LIMIT + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- Word Freq Tests ---


def test_word_freq_response_structure_processed_params(client: TestClient):
    """Test response has correct structure."""
    response = client.get(f"/word-freq?word={tests_integration.SAMPLE_PROCESSED_WORD}")
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_PROCESSED_WORD_RESPONSE

    assert isinstance(response_data["ngram"], str)
    assert isinstance(response_data["count"], int)


def test_word_freq_response_structure_unprocessed_params(client: TestClient):
    """Test response has correct structure with unprocessed input."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORD}&start_year={tests_integration.SAMPLE_UNPROCESSED_START_YEAR}&end_year={tests_integration.SAMPLE_UNPROCESSED_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_UNPROCESSED_WORD_RESPONSE

    assert isinstance(response_data["ngram"], str)
    assert isinstance(response_data["count"], int)


def test_word_freq_response_structure_mixed_params(client: TestClient):
    """Test response has correct structure with unprocessed input."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_MIXED_WORD}&start_year={tests_integration.SAMPLE_MIXED_START_YEAR}&end_year={tests_integration.SAMPLE_MIXED_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_MIXED_WORD_RESPONSE

    assert isinstance(response_data["ngram"], str)
    assert isinstance(response_data["count"], int)


def test_word_freq_word_required(client: TestClient):
    """Test word parameter is required."""
    response = client.get("/word-freq")
    assert response.status_code != status.HTTP_200_OK


def test_word_freq_status_code_default_params(client: TestClient):
    """Test endpoint with default parameters."""
    response = client.get(f"/word-freq?word={tests_integration.SAMPLE_PROCESSED_WORD}")
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORD}&start_year={src_constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORD}&end_year={src_constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_word_freq_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORDS_QUERY_RESPONSE}&start_year={src_constants.RAW_DATA_END_YEAR}&end_year={src_constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_word_freq_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORDS_QUERY_RESPONSE}&start_year={src_constants.RAW_DATA_START_YEAR - 1}&end_year={src_constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_word_freq_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    response = client.get(
        f"/word-freq?word={tests_integration.SAMPLE_UNPROCESSED_WORDS_QUERY_RESPONSE}&start_year={src_constants.RAW_DATA_START_YEAR}&end_year={src_constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# --- Words Freq Tests ---


def test_words_freq_response_structure_default_params(client: TestClient):
    """Test response has correct structure."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_PROCESSED_WORDS]
    )
    response = client.get(f"/words-freq?{words_url}")

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_PROCESSED_WORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_words_freq_response_structure_unprocessed_params(client: TestClient):
    """Test response has correct structure."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )
    response = client.get(
        f"/words-freq?{words_url}&start_year={tests_integration.SAMPLE_UNPROCESSED_START_YEAR}&end_year={tests_integration.SAMPLE_UNPROCESSED_END_YEAR}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_UNPROCESSED_WORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_words_freq_response_structure_mixed_params(client: TestClient):
    """Test response has correct structure."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_MIXED_WORDS]
    )
    response = client.get(
        f"/words-freq?{words_url}&start_year={tests_integration.SAMPLE_MIXED_START_YEAR}&end_year={tests_integration.SAMPLE_MIXED_END_YEAR}"
    )

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()

    assert response_data == tests_integration.SAMPLE_MIXED_WORDS_QUERY_RESPONSE

    assert all(
        isinstance(result["ngram"], str) and isinstance(result["count"], int)
        for result in response_data["words"]
    )


def test_words_freq_words_required(client: TestClient):
    """Test words parameter is required."""
    response = client.get("/words-freq")
    assert response.status_code != status.HTTP_200_OK


def test_words_freq_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )

    response = client.get(
        f"/words-freq?{words_url}&start_year={src_constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_words_freq_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )

    response = client.get(
        f"/words-freq?{words_url}&end_year={src_constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_200_OK


def test_words_freq_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )

    response = client.get(
        f"/words-freq?{words_url}&start_year={src_constants.RAW_DATA_END_YEAR}&end_year={src_constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_words_freq_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )

    response = client.get(
        f"/words-freq?{words_url}&start_year={src_constants.RAW_DATA_START_YEAR - 1}&end_year={src_constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_words_freq_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    words_url = "&".join(
        ["words=" + word for word in tests_integration.SAMPLE_UNPROCESSED_WORDS]
    )

    response = client.get(
        f"/words-freq?{words_url}&start_year={src_constants.RAW_DATA_START_YEAR}&end_year={src_constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
