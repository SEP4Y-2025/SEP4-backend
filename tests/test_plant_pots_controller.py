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

################## add_plant_pot ######################

def test_add_plant_pot_success(client):
    mock_response = {
        "message": "Pot added successfully",
        "pot_id": "pot_1",
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff",
        "plant_type_name": "mint",
        "watering_frequency": 3,
        "water_dosage": 300,
        "environment_id": "1"
    }

    payload = {
        "pot_id": "pot_1",
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff"
    }

    with patch("services.plant_pots_service.PlantPotsService.add_plant_pot", return_value=mock_response):
        response = client.post("/environments/1/pots", json=payload)
        assert response.status_code == 200
        assert response.json() == mock_response

def test_add_pot_missing_field(client):
    payload = {
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff"
        # Missing "pot_id"
    }
    response = client.post("/environments/1/pots", json=payload)
    assert response.status_code == 422

def test_add_pot_invalid_plant_type(client):
    payload = {
        "plant_pot_label": "test pot",
        "pot_id": "pot_1",
        "plant_type_id": "invalid_plant_type_id"
    }

    with patch("services.plant_pots_service.PlantPotsService.add_plant_pot") as mock_add:
        mock_add.side_effect = ValueError("Invalid plant type ID")
        response = client.post("/environments/1/pots", json=payload)
        assert response.status_code == 400
        assert "Invalid plant type ID" in response.json()["detail"]

def test_add_pot_unregistered_arduino(client):
    payload = {
        "plant_pot_label": "Unregistered",
        "pot_id": "pot_9999999",
        "plant_type_id": "67fce650e50105831f316bff"
    }

    with patch("services.plant_pots_service.PlantPotsService.add_plant_pot") as mock_add:
        mock_add.side_effect = ValueError("Unknown or unregistered Arduino")
        response = client.post("/environments/1/pots", json=payload)
        assert response.status_code == 400
        assert "Unknown or unregistered Arduino" in response.json()["detail"]


################## delete_plant_pot ######################

def test_delete_plant_pot_success(client):
    with patch("services.plant_pots_service.PlantPotsService.delete_plant_pot", return_value=True):
        response = client.delete("/environments/1/pots/pot_1")
        assert response.status_code == 200
        assert response.json() == {"message": "Pot deleted successfully"}

def test_delete_nonexistent_pot(client):
    with patch("services.plant_pots_service.PlantPotsService.delete_plant_pot") as mock_delete:
        mock_delete.side_effect = ValueError("Plant pot not found")
        response = client.delete("/environments/1/pots/nonexistent_pot")
        assert response.status_code == 400
        assert "Plant pot not found" in response.json()["detail"]
