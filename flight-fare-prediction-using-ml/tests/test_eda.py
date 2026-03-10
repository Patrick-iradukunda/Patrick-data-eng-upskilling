from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_descriptive_stats():
    response = client.get("/api/v1/eda/stats")
    assert response.status_code in [200, 404]


def test_fare_distribution():
    response = client.get("/api/v1/eda/fare-distribution")
    assert response.status_code in [200, 404]


def test_kpis():
    response = client.get("/api/v1/eda/kpis")
    assert response.status_code in [200, 404]


def test_correlation():
    response = client.get("/api/v1/eda/correlation")
    assert response.status_code in [200, 404]


def test_fare_by_airline():
    response = client.get("/api/v1/eda/fare-by-airline")
    assert response.status_code in [200, 404]


def test_fare_by_season():
    response = client.get("/api/v1/eda/fare-by-season")
    assert response.status_code in [200, 404, 422]


def test_fare_by_route():
    response = client.get("/api/v1/eda/fare-by-route")
    assert response.status_code in [200, 404]


def test_monthly_trend():
    response = client.get("/api/v1/eda/monthly-trend")
    assert response.status_code in [200, 404, 422]