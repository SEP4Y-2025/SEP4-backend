import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from fastapi import FastAPI

from api.controllers.soil_humidity_prediction import router

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_test_endpoint(client):
    response = client.get("/api/prediction/test")
    assert response.status_code == 200
    assert response.json() == {"message": "Prediction API is working!"}

def test_predict_future_humidity_success(client):
    with patch("api.controllers.soil_humidity_prediction.SoilHumidityPredictionService") as MockService:
        mock_service = MockService.return_value
        mock_service.predict_future_humidity.return_value = {
            "plant_pot_id": "pot1",
            "current_timestamp": "2025-05-15T12:00:00",
            "prediction_timestamp": "2025-05-15T12:05:00",
            "current_soil_humidity": 215.0,
            "predicted_soil_humidity": 210.5,
            "features_used": ["temperature", "air_humidity"],
            "prediction_method": "mocked",
        }
        response = client.get("/api/prediction/future-humidity?plant_pot_id=pot1&minutes_ahead=5")
        assert response.status_code == 200
        data = response.json()
        assert data["plant_pot_id"] == "pot1"
        assert data["prediction_method"] == "mocked"

def test_predict_future_humidity_error(client):
    with patch("api.controllers.soil_humidity_prediction.SoilHumidityPredictionService") as MockService:
        mock_service = MockService.return_value
        mock_service.predict_future_humidity.return_value = {"error": "Not found"}
        response = client.get("/api/prediction/future-humidity?plant_pot_id=badpot")
        assert response.status_code == 404
        assert response.json()["detail"] == "Not found"

def test_get_model_metrics_success(client):
    with patch("api.controllers.soil_humidity_prediction.SoilHumidityPredictionService") as MockService:
        mock_service = MockService.return_value
        mock_service.get_model_metrics.return_value = {
            "message": "ok",
            "train": {"mse": 1},
            "validation": {"mse": 2},
            "test": {"mse": 3},
            "model_type": "mocked"
        }
        response = client.get("/api/prediction/model-metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["model_type"] == "mocked"

def test_get_model_metrics_error(client):
    with patch("api.controllers.soil_humidity_prediction.SoilHumidityPredictionService") as MockService:
        mock_service = MockService.return_value
        mock_service.get_model_metrics.return_value = {"error": "metrics error"}
        response = client.get("/api/prediction/model-metrics")
        assert response.status_code == 500
        assert response.json()["detail"] == "metrics error"