import pytest
from pydantic import ValidationError
from src.main import FilterParams

def test_valid_params():
    params = FilterParams(start_year=2000, end_year=2010)
    assert params.start_year == 2000

def test_invalid_year_order():
    with pytest.raises(ValidationError):
        FilterParams(start_year=2010, end_year=2000)

def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        FilterParams(start_year=2000, end_year=2010, extra_param=10)