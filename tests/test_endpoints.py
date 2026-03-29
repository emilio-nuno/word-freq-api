from fastapi.testclient import TestClient
from src.main import app
import src.constants as constants

#TODO: Should I use a constant for default word number?
def test_get_data_default_params(override_db_path):
    """Test endpoint with default parameters."""
    client = TestClient(app)
    response = client.get("/top-words")
    assert response.status_code == 200
    data = response.json()
    assert "words" in data
    assert isinstance(data["words"], list)
    assert len(data["words"]) == 10  # Default word_number is 50, but we have 10 in preprocessed


def test_get_data_valid_params(override_db_path):
    """Test endpoint with valid custom parameters."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2000&end_year=2010")
    assert response.status_code == 200
    data = response.json()
    assert "words" in data
    assert isinstance(data["words"], list)


def test_get_data_invalid_year_order(override_db_path):
    """Test that start_year > end_year returns 422."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2010&end_year=2000")
    assert response.status_code == 422


def test_get_data_out_of_range(override_db_path):
    """Test that year out of valid range returns 422."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=1300")
    assert response.status_code == 422


def test_word_number_parameter(override_db_path):
    """Test word_number parameter controls result count."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["words"]) == 5


def test_word_number_minimum(override_db_path):
    """Test word_number=1 returns single result."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data["words"]) == 1
    assert data["words"][0]["ngram"] == "the"
    assert data["words"][0]["count"] == 1000000


def test_word_number_maximum(override_db_path):
    """Test word_number=1000 is accepted."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=1000")
    assert response.status_code == 200


def test_word_number_zero_invalid(override_db_path):
    """Test word_number=0 returns 422."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=0")
    assert response.status_code == 422


def test_word_number_negative_invalid(override_db_path):
    """Test negative word_number returns 422."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=-5")
    assert response.status_code == 422


def test_word_number_above_maximum_invalid(override_db_path):
    """Test word_number > 1000 returns 422."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=1001")
    assert response.status_code == 422


def test_response_structure(override_db_path):
    """Test response has correct structure."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=3")
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level structure
    assert "words" in data
    assert isinstance(data["words"], list)
    
    # Check word entry structure
    for word in data["words"]:
        assert "ngram" in word
        assert "count" in word
        assert isinstance(word["ngram"], str)
        assert isinstance(word["count"], int)


def test_response_sorted_by_count(override_db_path):
    """Test that results are sorted by count in descending order."""
    client = TestClient(app)
    response = client.get("/top-words?word_number=5")
    assert response.status_code == 200
    data = response.json()
    
    counts = [word["count"] for word in data["words"]]
    assert counts == sorted(counts, reverse=True)


def test_preprocessed_path_used(override_db_path):
    """Test that preprocessed table is used for default year range (2000-2019)."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2000&end_year=2019&word_number=3")
    assert response.status_code == 200
    data = response.json()
    
    # Should return preprocessed data
    assert data["words"][0]["ngram"] == "the"
    assert data["words"][0]["count"] == 1000000


def test_unprocessed_path_custom_range(override_db_path):
    """Test that unprocessed table is used for custom year range."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2000&end_year=2001&word_number=3")
    assert response.status_code == 200
    data = response.json()
    
    # Should aggregate from unprocessed data
    # "the" has 50000 (2000) + 51000 (2001) = 101000
    assert data["words"][0]["ngram"] == "the"
    assert data["words"][0]["count"] == 101000


def test_historical_year_range(override_db_path):
    """Test query with historical year range."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=1500&end_year=1600&word_number=5")
    assert response.status_code == 200
    data = response.json()
    
    # Should only return words from that period
    ngrams = [word["ngram"] for word in data["words"]]
    assert "past" in ngrams
    assert "ancient" in ngrams


def test_single_year_query(override_db_path):
    """Test query for a single year."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2000&end_year=2000&word_number=5")
    assert response.status_code == 200
    data = response.json()
    
    # Should return data from year 2000 only
    assert len(data["words"]) > 0


def test_combined_parameters(override_db_path):
    """Test endpoint with all parameters combined."""
    client = TestClient(app)
    response = client.get("/top-words?start_year=2015&end_year=2019&word_number=10")
    assert response.status_code == 200
    data = response.json()
    
    assert "words" in data
    assert len(data["words"]) <= 10


def test_boundary_years(override_db_path):
    """Test with boundary years."""
    client = TestClient(app)
    
    # Test minimum year
    response = client.get(f"/top-words?start_year={constants.RAW_DATA_START_YEAR}&end_year=1500")
    assert response.status_code == 200
    
    # Test maximum year
    response = client.get(f"/top-words?start_year=2015&end_year={constants.RAW_DATA_END_YEAR}")
    assert response.status_code == 200


def test_empty_result_handling(override_db_path):
    """Test handling when no data matches the criteria."""
    client = TestClient(app)
    # Query a year range with no data
    response = client.get("/top-words?start_year=1471&end_year=1499")
    assert response.status_code == 200
    data = response.json()
    assert "words" in data
    # May be empty or have limited results
    assert isinstance(data["words"], list)
