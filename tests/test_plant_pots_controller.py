import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch

from api.controllers.plant_pots_controller import router as pot_router

app = FastAPI()
app.include_router(pot_router)

@pytest.fixture
def client():
    return TestClient(app)


def test_add_plant_pot_success(client):
    mock_response = {
        "message": "Pot added successfully",
        "pot_id": "pot_1",
        "plant_pot_label": "green pot",
        "watering_frequency": 3,
        "water_dosage": 300
    }

    payload = {
        "pot_id": "pot_1",
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff",
        "watering_frequency": 3,
        "water_dosage": 300
    }

    with patch("services.plant_pots_service.PlantPotsService.add_plant_pot", return_value=mock_response):
        response = client.post("/environments/1/pots", json=payload)
        assert response.status_code == 200
        assert response.json() == mock_response