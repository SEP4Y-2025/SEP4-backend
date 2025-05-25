from unittest.mock import patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

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
        "environment_id": "1",
    }

    payload = {
        "pot_id": "pot_1",
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff",
        "watering_frequency": 3,
        "water_dosage": 300,
    }

    with patch(
        "services.plant_pots_service.PlantPotsService.add_plant_pot",
        return_value=mock_response,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.post(
                "/environments/1/pots",
                json=payload,
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == mock_response


def test_add_pot_missing_field(client):
    payload = {
        "plant_pot_label": "green pot",
        "plant_type_id": "67fce650e50105831f316bff",
        "watering_frequency": 3,
        "water_dosage": 300,
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
        "plant_type_id": "456gh",
    }

    with patch(
        "services.plant_pots_service.PlantPotsService.get_plant_pot_by_id",
        return_value=mock_pot,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                "/environments/234ab/pots/60f6f48e8d3f5b001f0e4d2b",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == {"pot": mock_pot}


def test_get_plant_pot_not_found(client):
    environment_id = "234ab"
    non_existent_pot_id = "nonexistentpotid"

    with patch(
        "services.plant_pots_service.PlantPotsService.get_plant_pot_by_id",
        return_value=None,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                f"/environments/{environment_id}/pots/{non_existent_pot_id}",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 404
            assert response.json() == {"detail": "Plant pot not found"}


def test_delete_plant_pot_success(client):
    with patch(
        "services.plant_pots_service.PlantPotsService.delete_plant_pot",
        return_value=True,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.delete(
                "/environments/1/pots/662ebf49c7b9e2a7681e4a54",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == {"message": "Pot deleted successfully"}


def test_delete_pot_unexpected_error(client):
    with patch(
        "services.plant_pots_service.PlantPotsService.delete_plant_pot"
    ) as mock_delete:
        mock_delete.side_effect = Exception("Unexpected error")
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.delete(
                "/environments/1/pots/pot_1",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 500
            assert "Unexpected error" in response.json()["detail"]


def get_pots_by_environment_success(client):
    mock_pots = [
        {"pot_id": "pot_1", "plant_pot_label": "Pot 1"},
        {"pot_id": "pot_2", "plant_pot_label": "Pot 2"},
    ]

    with patch(
        "services.plant_pots_service.PlantPotsService.get_pots_by_environment",
        return_value=mock_pots,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                "/environments/1/pots",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == {"pots": mock_pots}


def test_get_pots_by_environment_not_found(client):
    with patch(
        "services.plant_pots_service.PlantPotsService.get_pots_by_environment",
        return_value=None,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                "/environments/1/pots",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 400
            assert response.json() == {"detail": "Invalid environment ID"}


def test_get_history_success(client):
    mock_history = [
        {"pot_id": "pot_1", "timestamp": "2023-01-01T00:00:00", "temperature": 25.5},
        {"pot_id": "pot_1", "timestamp": "2023-01-02T00:00:00", "temperature": 26.0},
    ]

    with patch(
        "services.plant_pots_service.PlantPotsService.get_historical_data",
        return_value=mock_history,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                "/environments/1/pots/pot_1/historicalData",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == {"historicalData": mock_history}


def test_get_history_not_found(client):
    with patch(
        "services.plant_pots_service.PlantPotsService.get_historical_data",
        return_value=None,
    ):
        with patch(
            "api.controllers.plant_pots_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.get(
                "/environments/1/pots/pot_1/historicalData",
                headers={"Authorization": "Bearer test_token"},
            )
            assert response.status_code == 200
            assert response.json() == {"historicalData": None}
