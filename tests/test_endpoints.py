from fastapi.testclient import TestClient
import src.constants as constants

def test_response_structure_default_params(client: TestClient):
    """Test response has correct structure."""
    response = client.get("/top-words")
    assert response.status_code == 200

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

def test_status_code_default_params(client: TestClient):
    """Test endpoint with default parameters."""
    response = client.get("/top-words")
    assert response.status_code == 200

def test_start_year_valid_accepts(client: TestClient):
    """Test endpoint with valid start_year parameter."""
    response = client.get(f"/top-words?start_year={constants.RAW_DATA_START_YEAR}")
    assert response.status_code == 200


def test_end_year_valid_accepts(client: TestClient):
    """Test endpoint with valid end_year parameter."""
    response = client.get(f"/top-words?end_year={constants.RAW_DATA_END_YEAR}")
    assert response.status_code == 200

def test_year_order_inverted_rejects(client: TestClient):
    """Test that start_year > end_year returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_END_YEAR}&end_year={constants.RAW_DATA_START_YEAR}"
    )
    assert response.status_code == 422


def test_start_year_below_minimum_rejects(client: TestClient):
    """Test that start_year before valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_START_YEAR - 1}&end_year={constants.RAW_DATA_END_YEAR}"
    )
    assert response.status_code == 422


def test_end_year_above_maximum_rejects(client: TestClient):
    """Test that end_year after valid range returns 422."""
    response = client.get(
        f"/top-words?start_year={constants.RAW_DATA_START_YEAR}&end_year={constants.RAW_DATA_END_YEAR + 1}"
    )
    assert response.status_code == 422

def test_word_number_valid_accepts(client: TestClient):
    """Test endpoint with valid word_number parameter."""
    response = client.get(f"/top-words?word_number={constants.TOP_WORDS_DEFAULT_LIMIT}")
    assert response.status_code == 200


def test_word_number_minimum_boundary_accepts(client: TestClient):
    """Test word_number=1 returns single result."""
    response = client.get(f"/top-words?word_number={constants.TOP_WORDS_MIN_LIMIT}")
    assert response.status_code == 200


def test_word_number_maximum_boundary_accepts(client: TestClient):
    """Test word_number=TOP_WORDS_MAX_LIMIT is accepted."""
    response = client.get(f"/top-words?word_number={constants.TOP_WORDS_MAX_LIMIT}")
    assert response.status_code == 200


def test_word_number_zero_rejects(client: TestClient):
    """Test word_number=0 returns 422."""
    response = client.get("/top-words?word_number=0")
    assert response.status_code == 422


def test_word_number_negative_rejects(client: TestClient):
    """Test negative word_number returns 422."""
    response = client.get("/top-words?word_number=-5")
    assert response.status_code == 422


def test_word_number_above_maximum_rejects(client: TestClient):
    """Test word_number > TOP_WORDS_MAX_LIMIT returns 422."""
    response = client.get(f"/top-words?word_number={constants.TOP_WORDS_MAX_LIMIT + 1}")
    assert response.status_code == 422

