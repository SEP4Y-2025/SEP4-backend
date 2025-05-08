import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.controllers.plant_types_controller import router as plant_types_router

app = FastAPI()
app.include_router(plant_types_router)

@pytest.fixture
def client():
    return TestClient(app)


def test_add_plant_type_success(client):
    mock_response = {
        "message": "Plant type added successfully",
        "plantTypeId": "plant_type_1"
    }

    payload = {
        "name": "Cactus",
        "water_frequency": 7,
        "water_dosage": 100
    }

    with patch("services.plant_types_service.PlantTypesService.add_plant_type", return_value="plant_type_1"):
        response = client.post("/environments/env_1/plant_types", json=payload)
        assert response.status_code == 200
        assert response.json() == mock_response


def test_add_plant_type_missing_data(client):
    payload = {
        "water_frequency": 7,
        "water_dosage": 100
    }

    with patch("services.plant_types_service.PlantTypesService.add_plant_type") as mock_service:
        mock_service.side_effect = ValueError("Invalid plant type data: 'name' and 'plant_env_id' are required")
        response = client.post("/environments/env_1/plant_types", json=payload)
        assert response.status_code == 400
        assert "Invalid plant type data" in response.json()["detail"]


def test_get_plant_types_success(client):
    mock_plant_types = [
        {
            "_id": "123abc",
            "name": "Mint",
            "water_frequency": 3,
            "water_dosage": 200,
            "plant_env_id": "env123"
        },
        {
            "_id": "456def",
            "name": "Rosemary",
            "water_frequency": 5,
            "water_dosage": 150,
            "plant_env_id": "env123"
        }
    ]

    with patch("services.plant_types_service.PlantTypesService.get_all_plant_types", return_value=mock_plant_types):
        response = client.get("/environments/env123/plant_types")
        assert response.status_code == 200
        assert "PlantTypes" in response.json()
        assert len(response.json()["PlantTypes"]) == 2
        assert response.json()["PlantTypes"][0]["name"] == "Mint"


def test_get_plant_types_not_found(client):
    with patch("services.plant_types_service.PlantTypesService.get_all_plant_types") as mock_service:
        mock_service.side_effect = ValueError("No plant types found for environment ID: env999")
        response = client.get("/environments/env999/plant_types")
        assert response.status_code == 400
        assert "No plant types found" in response.json()["detail"]