import pandas as pd
import pytest

from src.cleaner import _normalize_phone, _normalize_date, clean


@pytest.mark.parametrize("raw, expected", [
    ("555-123-4567",  "555-123-4567"),
    ("(555) 234-5678", "555-234-5678"),
    ("555.789.0123",  "555-789-0123"),
    ("5557890123",    "555-789-0123"),
    ("",              ""),
])
def test_normalize_phone(raw, expected):
    assert _normalize_phone(raw) == expected


@pytest.mark.parametrize("raw, expected", [
    ("1975/05/10",  "1975-05-10"),
    ("01/15/2024",  "2024-01-15"),
    ("1985-03-15",  "1985-03-15"),
])
def test_normalize_date(raw, expected):
    assert _normalize_date(raw) == expected


def test_normalize_date_invalid_returns_na():
    assert pd.isna(_normalize_date("invalid_date"))


def _make_row(**overrides) -> pd.DataFrame:
    base = {"customer_id": ["1"], "first_name": ["John"], "last_name": ["Doe"],
            "email": ["john@gmail.com"], "phone": ["555-123-4567"], "date_of_birth": ["1985-03-15"],
            "address": ["123 Main St"], "income": ["75000"], "account_status": ["active"],
            "created_date": ["2024-01-10"]}
    base.update({k: [v] for k, v in overrides.items()})
    return pd.DataFrame(base)


def test_clean_fills_missing_first_name():
    cleaned, _ = clean(_make_row(first_name=None))
    assert cleaned["first_name"].iloc[0] == "[UNKNOWN]"


def test_clean_normalizes_phone():
    cleaned, _ = clean(_make_row(phone="5551234567"))
    assert cleaned["phone"].iloc[0] == "555-123-4567"


def test_clean_lowercases_email():
    cleaned, _ = clean(_make_row(email="JOHN@GMAIL.COM"))
    assert cleaned["email"].iloc[0] == "john@gmail.com"


def test_clean_converts_income_to_float():
    cleaned, _ = clean(_make_row())
    assert cleaned["income"].dtype == float


def test_clean_fills_missing_income():
    cleaned, _ = clean(_make_row(income=None))
    assert cleaned["income"].iloc[0] == 0.0


def test_clean_returns_log_entries():
    _, log = clean(_make_row())
    assert len(log) > 0
