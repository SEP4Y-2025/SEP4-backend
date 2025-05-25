import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.controllers.auth_controller import router
from models.auth import TokenResponse

from fastapi import FastAPI

app = FastAPI()
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_login_success(client):
    with patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_service = MockAuthService.return_value
        mock_service.authenticate_user.return_value = {
            "_id": "user_id",
            "username": "testuser",
            "email": "test@example.com"
        }
        mock_service.create_access_token.return_value = {
            "access_token": "token",
            "token_type": "bearer",
            "expires_in": 1800
        }
        response = client.post(
            "/auth/login",
            data={"username": "testuser", "password": "password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "token"
        assert data["user_id"] == "user_id"

def test_login_failure(client):
    with patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_service = MockAuthService.return_value
        mock_service.authenticate_user.return_value = None
        response = client.post(
            "/auth/login",
            data={"username": "wrong", "password": "wrong"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 500

def test_register_success(client):
    with patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_service = MockAuthService.return_value
        mock_service.create_user.return_value = "user_id"
        response = client.post(
            "/auth/registration",
            json={"username": "testuser", "password": "password", "email": "test@example.com"}
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == "user_id"

def test_register_duplicate(client):
    with patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_service = MockAuthService.return_value
        mock_service.create_user.return_value = None
        response = client.post(
            "/auth/registration",
            json={"username": "testuser", "password": "password", "email": "test@example.com"}
        )
        assert response.status_code == 500

def test_update_password_success(client):
    with patch("api.controllers.auth_controller.decode_jwtheader") as mock_decode, \
         patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_decode.return_value = "user_id"
        mock_service = MockAuthService.return_value
        mock_service.change_password.return_value = True
        response = client.put(
            "/auth/password",
            json={"old_password": "old", "new_password": "new"},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

def test_update_password_failure(client):
    with patch("api.controllers.auth_controller.decode_jwtheader") as mock_decode, \
         patch("api.controllers.auth_controller.AuthService") as MockAuthService:
        mock_decode.return_value = "user_id"
        mock_service = MockAuthService.return_value
        mock_service.change_password.return_value = False
        response = client.put(
            "/auth/password",
            json={"old_password": "old", "new_password": "new"},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == 500

def test_update_password_empty_new(client):
    with patch("api.controllers.auth_controller.decode_jwtheader") as mock_decode:
        mock_decode.return_value = "user_id"
        response = client.put(
            "/auth/password",
            json={"old_password": "old", "new_password": ""},
            headers={"Authorization": "Bearer token"}
        )
        assert response.status_code == 500