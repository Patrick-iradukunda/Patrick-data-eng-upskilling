import pandas as pd
import pytest

from src.masker import _mask_name, _mask_email, _mask_phone, _mask_dob, mask


@pytest.mark.parametrize("raw, expected", [
    ("John",      "J***"),
    ("Patricia",  "P***"),
    ("[UNKNOWN]", "[UNKNOWN]"),
    ("",          ""),
])
def test_mask_name(raw, expected):
    assert _mask_name(raw) == expected


@pytest.mark.parametrize("raw, first, domain", [
    ("john@gmail.com",      "j***", "@gmail.com"),
    ("patricia@company.net", "p***", "@company.net"),
])
def test_mask_email(raw, first, domain):
    result = _mask_email(raw)
    assert result.startswith(first)
    assert result.endswith(domain)


def test_mask_email_no_at_symbol():
    assert _mask_email("not-an-email") == "not-an-email"


@pytest.mark.parametrize("raw, last_four", [
    ("555-123-4567", "4567"),
    ("555-987-6543", "6543"),
])
def test_mask_phone(raw, last_four):
    result = _mask_phone(raw)
    assert result == f"***-***-{last_four}"


def test_mask_phone_non_standard_unchanged():
    assert _mask_phone("not-a-phone") == "not-a-phone"


@pytest.mark.parametrize("raw, expected", [
    ("1985-03-15", "1985-**-**"),
    ("1990-07-22", "1990-**-**"),
    ("[UNKNOWN]",  "[UNKNOWN]"),
])
def test_mask_dob(raw, expected):
    assert _mask_dob(raw) == expected


def test_mask_dataframe():
    df = pd.DataFrame({
        "customer_id": [1], "first_name": ["John"], "last_name": ["Doe"],
        "email": ["john@gmail.com"], "phone": ["555-123-4567"],
        "date_of_birth": ["1985-03-15"], "address": ["123 Main St"],
        "income": [75000.0], "account_status": ["active"], "created_date": ["2024-01-10"],
    })
    masked = mask(df)
    assert masked["first_name"].iloc[0] == "J***"
    assert masked["last_name"].iloc[0] == "D***"
    assert masked["email"].iloc[0] == "j***@gmail.com"
    assert masked["phone"].iloc[0] == "***-***-4567"
    assert masked["date_of_birth"].iloc[0] == "1985-**-**"
    assert masked["address"].iloc[0] == "[MASKED ADDRESS]"
    assert masked["income"].iloc[0] == 75000.0
    assert masked["account_status"].iloc[0] == "active"
