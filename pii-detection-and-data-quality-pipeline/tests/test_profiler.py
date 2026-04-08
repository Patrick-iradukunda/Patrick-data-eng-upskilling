import pandas as pd
import pytest

from src.profiler import profile, _quality_issues

CLEAN_ROWS = {
    "customer_id": ["1", "2"], "first_name": ["John", "Jane"], "last_name": ["Doe", "Smith"],
    "email": ["john@gmail.com", "jane@company.com"], "phone": ["555-123-4567", "555-987-6543"],
    "date_of_birth": ["1985-03-15", "1990-07-22"], "address": ["123 Main St", "456 Oak Ave"],
    "income": ["75000", "95000"], "account_status": ["active", "active"],
    "created_date": ["2024-01-10", "2024-01-11"],
}

DIRTY_ROWS = {
    "customer_id": ["1", "1"], "first_name": [None, "Jane"], "last_name": ["Doe", "Smith"],
    "email": ["not-an-email", "jane@company.com"], "phone": ["555-123-4567", "5551234567"],
    "date_of_birth": ["invalid_date", "1990-07-22"], "address": ["123 Main St", None],
    "income": ["-100", "95000"], "account_status": ["unknown_status", "active"],
    "created_date": ["2024-01-10", "bad_date"],
}


@pytest.fixture
def clean_df(): return pd.DataFrame(CLEAN_ROWS)

@pytest.fixture
def dirty_df(): return pd.DataFrame(DIRTY_ROWS)


def test_completeness_no_missing(clean_df):
    result = profile(clean_df)["completeness"]
    assert all(s["missing"] == 0 for s in result.values())


def test_completeness_with_missing(dirty_df):
    result = profile(dirty_df)["completeness"]
    assert result["first_name"]["missing"] == 1
    assert result["first_name"]["pct"] == 50.0


def test_uniqueness_detects_duplicates(dirty_df):
    assert profile(dirty_df)["uniqueness"]["duplicates"] == 1


def test_uniqueness_clean(clean_df):
    assert profile(clean_df)["uniqueness"]["duplicates"] == 0


@pytest.mark.parametrize("col", ["email", "date_of_birth", "created_date", "account_status", "income"])
def test_quality_issues_detected(dirty_df, col):
    cols = [i["column"] for i in _quality_issues(dirty_df)]
    assert col in cols


def test_profile_returns_expected_keys(clean_df):
    result = profile(clean_df)
    assert set(result.keys()) == {"timestamp", "shape", "completeness", "data_types", "uniqueness", "quality_issues"}
