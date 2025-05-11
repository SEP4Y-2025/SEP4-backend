import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.controllers.users_controller import router as user_router

app = FastAPI()
app.include_router(user_router)
@pytest.fixture
def client():
    return TestClient(app)
def test_add_user_permission_success(client):
    mock_response = {
        "message": "User permission added successfully",
    }

    payload = {
        "user_email": "email2@domain.com"
    }

    with patch("services.users_service.UsersService.add_permission", return_value=None):
        response = client.put("/environments/env_1/assistants", json=payload)
        assert response.status_code == 200
        assert response.json() == mock_response

def test_add_user_permission_missing_data(client):
    payload = {
        "user_email": ""
    }

    with patch("services.users_service.UsersService.add_permission") as mock_service:
        mock_service.side_effect = ValueError("Invalid user permission data: 'user_email' is required")
        response = client.put("/environments/env_1/assistants", json=payload)
        assert response.status_code == 400
        assert "Invalid user permission data" in response.json()["detail"]