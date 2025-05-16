import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.controllers.environments_controller import router as environments_router

app = FastAPI()
app.include_router(environments_router)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_environment_by_id_success(client):
    mock_environment = {
        "_id": "680f8359688cb5341f9f9c19",
        "name": "Living Room",
    }

    with patch(
        "services.environments_service.EnvironmentsService.get_environment_by_id",
        return_value=mock_environment,
    ):
        response = client.get("/environments/680f8359688cb5341f9f9c19")
        assert response.status_code == 200
        assert response.json() == {"environment": mock_environment}


def test_get_environment_by_id_not_found(client):
    with patch(
        "services.environments_service.EnvironmentsService.get_environment_by_id"
    ) as mock_service:
        mock_service.return_value = None
        response = client.get("/environments/680f8359688cb5341f9f9c19")
        assert response.status_code == 404
        assert response.json() == {"message": "Environment not found"}


def test_add_environment_success(client):
    mock_response = {
        "message": "Environment created successfully",
        "environment_id": "680f8359688cb5341f9f9c19",
        "name": "Living Room",
    }

    payload = {"name": "Living Room"}

    with patch(
        "services.environments_service.EnvironmentsService.add_environment",
        return_value=mock_response,
    ):
        response = client.post("/environments", json=payload)
        assert response.status_code == 200
        assert response.json() == mock_response


def test_add_environment_missing_name(client):
    payload = {}

    response = client.post("/environments", json=payload)
    assert response.status_code == 422  # Unprocessable Entity
    error_detail = response.json()["detail"]
    assert any(
        err.get("loc") == ["body", "name"]
        and "field required" in err.get("msg", "").lower()
        for err in error_detail
    )


def test_add_environment_internal_server_error(client):
    payload = {"name": "Living Room"}

    with patch(
        "services.environments_service.EnvironmentsService.add_environment"
    ) as mock_service:
        mock_service.side_effect = Exception("Unexpected error")
        response = client.post("/environments", json=payload)
        assert response.status_code == 500
        assert "An error occurred" in response.json()["detail"]["message"]
