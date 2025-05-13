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

def test_get_user_success(client):
    mock_response = {
    "_id": "662ebf49c7b9e2a7681e4a53",
    "username": "Allan",
    "password": "$2b$12$5b53fKRZFsqCoSx1k0EsA.pwbqsdktsAEiyiopZopin/J7rcDMTNq",
    "email": "email1@domain.com",
    "environments": [
        "680f8359688cb5341f9f9c19"
    ]

    }

    with patch("services.users_service.UsersService.get_user") as mock_service:
        mock_service.return_value = mock_response
        response = client.get("/users/email1@domain.com")
        assert response.status_code == 200
        assert response.json() == mock_response

def test_get_user_not_found(client):
    with patch("services.users_service.UsersService.get_user") as mock_service:
        mock_service.side_effect = ValueError("User not found")
        response = client.get("/users/email1@domain.com")
        assert response.status_code == 400
        assert response.json() == {"detail": "User not found"}