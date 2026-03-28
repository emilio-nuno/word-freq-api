import pytest
from pydantic import ValidationError
from src.main import FilterParams
import src.constants as constants

INVALID_START_YEAR = 1300
INVALID_END_YEAR = 3000

#TODO: Add tests to check the path when start and end years are

def test_valid_start_year_invalid_end_year():
    with pytest.raises(ValidationError, match=f"Input should be less than or equal to {constants.RAW_DATA_END_YEAR}") as exc_info:
        FilterParams(
            start_year=constants.RAW_DATA_START_YEAR, end_year=INVALID_END_YEAR
        )

    assert exc_info.value.error_count() == 1

def test_invalid_start_year_valid_end_year():
    with pytest.raises(ValidationError, match=f"Input should be greater than or equal to {constants.RAW_DATA_START_YEAR}") as exc_info:
        FilterParams(
            start_year=INVALID_START_YEAR, end_year=constants.RAW_DATA_END_YEAR
        )

    assert exc_info.value.error_count() == 1

def test_valid_start_year_valid_end_year():
    
    FilterParams(start_year=constants.PROCESSED_DATA_START_YEAR, end_year=constants.PROCESSED_DATA_END_YEAR)


def test_extra_fields_forbidden():

    with pytest.raises(ValidationError):
        FilterParams(start_year=2000, end_year=2010, extra_param=10)
