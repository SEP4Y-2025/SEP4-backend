# tests/test_plant_types.py

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.controllers.plant_types_controller import router as plant_types_router

app = FastAPI()
app.include_router(plant_types_router)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_plant_types_success(client):
    mock_plant_types = [
        {
            "_id": "123abc",
            "plant_type_name": "Mint",
            "watering_freq": 3,
            "water_dosage": 200,
            "env_id": "env123",
            "plant_pot_id": "234ABC",
        },
        {
            "_id": "456def",
            "plant_type_name": "Rosemary",
            "watering_freq": 5,
            "water_dosage": 150,
            "env_id": "env123",
            "plant_pot_id": "789XYZ",
        },
    ]

    with patch(
        "services.plant_types_service.PlantTypesService.get_all_plant_types",
        return_value=mock_plant_types,
    ):
        response = client.get("/environments/env123/plant_types")
        assert response.status_code == 200
        assert "PlantTypes" in response.json()
        assert len(response.json()["PlantTypes"]) == 2
        assert response.json()["PlantTypes"][0]["plant_type_name"] == "Mint"
        assert response.json()["PlantTypes"][0]["plant_pot_id"] == "234ABC"


def test_get_plant_types_not_found(client):
    with patch(
        "services.plant_types_service.PlantTypesService.get_all_plant_types"
    ) as mock_service:
        mock_service.side_effect = ValueError(
            "No plant types found for environment ID: env999"
        )
        response = client.get("/environments/env999/plant_types")
        assert response.status_code == 400
        assert "No plant types found" in response.json()["detail"]
