import pytest
from pydantic import ValidationError
from src.main import FilterParams
import src.constants as constants


def test_valid_start_year_invalid_end_year():
    """Test that model raises validation error on invalid end year"""
    with pytest.raises(
        ValidationError,
        match=f"Input should be less than or equal to {constants.RAW_DATA_END_YEAR}",
    ) as exc_info:
        FilterParams(
            start_year=constants.RAW_DATA_START_YEAR,
            end_year=constants.RAW_DATA_END_YEAR + 1,
        )

    assert exc_info.value.error_count() == 1


def test_invalid_start_year_valid_end_year():
    """Test that model raises validation error on invalid start year"""
    with pytest.raises(
        ValidationError,
        match=f"Input should be greater than or equal to {constants.RAW_DATA_START_YEAR}",
    ) as exc_info:
        FilterParams(
            start_year=constants.RAW_DATA_START_YEAR - 1,
            end_year=constants.RAW_DATA_END_YEAR,
        )

    assert exc_info.value.error_count() == 1


def test_extra_fields_forbidden():
    """Test that extra fields cannot be passed to the model."""
    with pytest.raises(ValidationError):
        FilterParams(
            start_year=constants.RAW_DATA_START_YEAR,
            end_year=constants.RAW_DATA_END_YEAR,
            extra_param=10,
        )


def test_start_year_greater_than_end_year():
    """Test that start_year > end_year raises validation error."""
    with pytest.raises(ValidationError, match="start_year.*must be <= end_year"):
        FilterParams(
            start_year=constants.RAW_DATA_END_YEAR,
            end_year=constants.RAW_DATA_START_YEAR,
        )


def test_start_year_equal_to_end_year():
    """Test that start and end date being equal does not raise a validation error."""
    FilterParams(
        start_year=constants.RAW_DATA_START_YEAR, end_year=constants.RAW_DATA_START_YEAR
    )
