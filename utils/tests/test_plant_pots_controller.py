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

################## delete_plant_pot ######################

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
    with patch("services.plant_pots_service.PlantPotsService.delete_p   lant_pot") as mock_delete:
        mock_delete.side_effect = Exception("Unexpected error")
        response = client.delete("/environments/1/pots/pot_1")
        assert response.status_code == 500
        assert "Unexpected error" in response.json()["detail"]