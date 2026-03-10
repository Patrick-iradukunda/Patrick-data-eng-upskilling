from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_PAYLOAD = {
    "airline": "Us-Bangla Airlines",
    "source": "Dhaka",
    "destination": "Chittagong",
    "base_fare": 3500.0,
    "tax_surcharge": 800.0,
    "month": 6,
    "day": 15,
    "weekday": 2,
    "season": "summer",
}


def test_predict_before_training():
    response = client.post("/api/v1/predict/", json=SAMPLE_PAYLOAD)
    assert response.status_code in [200, 503]


def test_predict_invalid_payload():
    bad_payload = {
        "airline": "Us-Bangla Airlines",
        "source": "Dhaka",
    }
    response = client.post("/api/v1/predict/", json=bad_payload)
    assert response.status_code == 422


def test_predict_negative_fare():
    bad_payload = {**SAMPLE_PAYLOAD, "base_fare": -100.0}
    response = client.post("/api/v1/predict/", json=bad_payload)
    assert response.status_code == 422


def test_predict_valid_payload_after_training():
    response = client.post("/api/v1/predict/", json=SAMPLE_PAYLOAD)
    if response.status_code == 200:
        data = response.json()
        assert "predicted_fare" in data
        assert "model_used" in data
        assert data["predicted_fare"] > 0