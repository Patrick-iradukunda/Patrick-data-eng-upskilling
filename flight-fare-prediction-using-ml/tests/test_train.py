from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_training_status():
    response = client.get("/api/v1/train/status")
    assert response.status_code == 200
    data = response.json()
    assert "trained" in data


def test_model_comparison_before_training():
    response = client.get("/api/v1/train/comparison")
    assert response.status_code in [200, 503]


def test_feature_importance_before_training():
    response = client.get("/api/v1/train/feature-importance")
    assert response.status_code in [200, 503]