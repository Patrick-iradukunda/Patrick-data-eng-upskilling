import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_raw_summary_no_data():
    response = client.get("/api/v1/data/raw/summary")
    assert response.status_code in [200, 404]


def test_raw_sample_default():
    response = client.get("/api/v1/data/raw/sample")
    assert response.status_code in [200, 404]


def test_raw_sample_custom_n():
    response = client.get("/api/v1/data/raw/sample?n=5")
    assert response.status_code in [200, 404]


def test_cleaned_summary():
    response = client.get("/api/v1/data/cleaned/summary")
    assert response.status_code in [200, 404]


def test_cleaned_sample():
    response = client.get("/api/v1/data/cleaned/sample")
    assert response.status_code in [200, 404]


def test_cleaning_report():
    response = client.get("/api/v1/data/cleaning-report")
    assert response.status_code in [200, 404, 422]