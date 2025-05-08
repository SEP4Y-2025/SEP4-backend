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
        "plant_type_id": "67fce650e50105831f316bff",
        "plant_type_name": "mint",
        "watering_frequency": 3,
        "water_dosage": 300,
        "environment_id": "1"
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


def test_add_pot_missing_field(client):
    payload = {
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff",
        "watering_frequency": 3,
        "water_dosage": 300
        # Missing "pot_id"
    }
    response = client.post("/environments/1/pots", json=payload)
    assert response.status_code == 422


def test_get_plant_pot_success(client):
    mock_pot = {
        "pot_id": "60f6f48e8d3f5b001f0e4d2b",
        "plant_pot_label": "Green Mint Pot",
        "watering_frequency": 3,
        "water_dosage": 250,
        "env_id": "234ab",
        "plant_type_id": "456gh"
    }

    with patch("services.plant_pots_service.PlantPotsService.get_plant_pot_by_id", return_value=mock_pot):
        response = client.get("/environments/234ab/pots/60f6f48e8d3f5b001f0e4d2b")
        assert response.status_code == 200
        assert response.json() == {"pot": mock_pot}


def test_get_plant_pot_not_found(client):
    environment_id = "234ab"
    non_existent_pot_id = "nonexistentpotid"

    with patch("services.plant_pots_service.PlantPotsService.get_plant_pot_by_id", return_value=None):
        response = client.get(f"/environments/{environment_id}/pots/{non_existent_pot_id}")
        assert response.status_code == 200
        assert response.json() == {"detail": f"PlantPot with Id {non_existent_pot_id} not found"}


def test_delete_plant_pot_success(client):
    with patch("services.plant_pots_service.PlantPotsService.delete_plant_pot", return_value=True):
        response = client.delete("/environments/1/pots/pot_1")
        assert response.status_code == 200
        assert response.json() == {"message": "Plant pot deleted successfully"}


def test_delete_nonexistent_pot(client):
    with patch("services.plant_pots_service.PlantPotsService.delete_plant_pot") as mock_delete:
        mock_delete.side_effect = ValueError("Plant pot not found")
        response = client.delete("/environments/1/pots/nonexistent_pot")
        assert response.status_code == 404
        assert "Plant pot not found" in response.json()["detail"]


def test_delete_pot_unexpected_error(client):
    with patch("services.plant_pots_service.PlantPotsService.delete_plant_pot") as mock_delete:
        mock_delete.side_effect = Exception("Unexpected error")
        response = client.delete("/environments/1/pots/pot_1")
        assert response.status_code == 500
        assert "Unexpected error" in response.json()["detail"]