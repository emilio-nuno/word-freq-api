from fastapi.testclient import TestClient
from src.main import app
import src.constants as constants

client = TestClient(app)

def test_get_data_default_params():
    response = client.get("/top-words")
    assert response.status_code == 200

def test_get_data_valid_params():
    response = client.get("/top-words?start_year=2000&end_year=2010")
    assert response.status_code == 200

def test_get_data_invalid_year_order():
    response = client.get("/top-words?start_year=2010&end_year=2000")
    assert response.status_code == 422

def test_get_data_out_of_range():
    response = client.get("/top-words?start_year=1300")
    assert response.status_code == 422