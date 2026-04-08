import pandas as pd
import pytest

from src.validator import validate_raw, validate_cleaned


def _raw(**overrides) -> pd.DataFrame:
    base = {"customer_id": ["1", "2"], "first_name": ["John", "Jane"], "last_name": ["Doe", "Smith"],
            "email": ["john@gmail.com", "jane@company.com"], "phone": ["555-123-4567", "555-987-6543"],
            "date_of_birth": ["1985-03-15", "1990-07-22"], "address": ["123 Main St", "456 Oak Ave"],
            "income": ["75000", "95000"], "account_status": ["active", "active"],
            "created_date": ["2024-01-10", "2024-01-11"]}
    base.update({k: [v, v] for k, v in overrides.items()})
    return pd.DataFrame(base)


def _cleaned(**overrides) -> pd.DataFrame:
    base = {"customer_id": [1, 2], "first_name": ["John", "Jane"], "last_name": ["Doe", "Smith"],
            "email": ["john@gmail.com", "jane@company.com"], "phone": ["555-123-4567", "555-987-6543"],
            "date_of_birth": ["1985-03-15", "1990-07-22"], "address": ["123 Main St", "456 Oak Ave"],
            "income": [75000.0, 95000.0], "account_status": ["active", "active"],
            "created_date": ["2024-01-10", "2024-01-11"]}
    base.update(overrides)
    return pd.DataFrame(base)


def test_validate_raw_passes_clean_data():
    passed, failures = validate_raw(_raw())
    assert passed and failures == []


@pytest.mark.parametrize("col, value, expected_col", [
    ("first_name", None,          "first_name"),
    ("email",      "not-an-email","email"),
    ("date_of_birth", "invalid",  "date_of_birth"),
    ("phone",      "5551234567",  "phone"),
])
def test_validate_raw_detects_failures(col, value, expected_col):
    df = _raw(**{col: value})
    passed, failures = validate_raw(df)
    assert not passed
    assert any(f["column"] == expected_col for f in failures)


def test_validate_cleaned_passes_valid_data():
    passed, errors = validate_cleaned(_cleaned())
    assert passed and errors == []


def test_validate_cleaned_fails_negative_income():
    df = _cleaned(income=[-500.0, -500.0])
    passed, _ = validate_cleaned(df)
    assert not passed
