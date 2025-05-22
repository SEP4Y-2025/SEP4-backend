import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch
from api.controllers.users_controller import router as user_router
import json

app = FastAPI()
app.include_router(user_router)


@pytest.fixture
def client():
    return TestClient(app)


def test_add_user_permission_success(client):
    mock_response = {
        "message": "User permission added successfully",
    }

    token = "Bearer test_token"

    with patch("services.users_service.UsersService.add_permission", return_value=None):
        with patch(
            "api.controllers.users_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.post(
                f"/environments/env1/assistants?user_email=email2@domain.com",
                headers={"Authorization": token},
            )
            assert response.status_code == 200
            assert response.json() == mock_response


def test_add_user_permission_missing_data(client):

    mock_response = {"detail": "Invalid user data: 'user_email' is required"}

    with patch(
        "services.users_service.UsersService.add_permission"
    ) as mock_add_permission:
        mock_add_permission.side_effect = ValueError(
            "Invalid user data: 'user_email' is required"
        )
        with patch(
            "api.controllers.users_controller.decode_jwtheader",
            return_value="mock_user_id",
        ):
            response = client.post(
                "/environments/env1/assistants?user_email=",
                headers={"Authorization": "Bearer test_token"},
            )
        assert response.status_code == 400
        assert response.json() == mock_response


def test_get_user_success(client):
    mock_response = {
        "_id": "662ebf49c7b9e2a7681e4a53",
        "username": "Allan",
        "password": "$2b$12$5b53fKRZFsqCoSx1k0EsA.pwbqsdktsAEiyiopZopin/J7rcDMTNq",
        "email": "email1@domain.com",
        "environments": ["680f8359688cb5341f9f9c19"],
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


def test_delete_user_permission_success(client):
    mock_response = {
        "message": "User permission deleted successfully",
    }
    email = "email2@domain.com"
    with patch(
        "services.users_service.UsersService.delete_permission", return_value=None
    ):
        response = client.delete(f"/environments/env_1/assistants/{email}")
        assert response.status_code == 200
        assert response.json() == mock_response


def test_delete_user_permission_success(client):
    email = "user@example.com"
    environment_id = "env_1"

    with patch("services.users_service.UsersService.delete_permission") as mock_service:
        mock_service.return_value = None

        response = client.delete(
            f"/environments/{environment_id}/assistants", params={"user_email": email}
        )

        assert response.status_code == 200
        assert response.json() == {"message": "User permission deleted successfully"}


def test_get_environment_permissions_success(client):
    mock_response = {
        "assistants": [
            {"user_id": "662ebf49c7b9e2a7681e4a55", "role": "Plant Assistant"},
            {"user_id": "662ebf49c7b9e2a7681e4a54", "role": "Plant Assistant"},
        ]
    }

    with patch(
        "services.users_service.UsersService.get_user_permissions",
        return_value=mock_response["assistants"],
    ):
        response = client.get("/environments/env_1/assistants")
        assert response.status_code == 200
        assert response.json() == mock_response


def test_get_environment_permissions_not_found(client):
    with patch(
        "services.users_service.UsersService.get_user_permissions"
    ) as mock_service:
        mock_service.side_effect = ValueError("Environment not found")
        response = client.get("/environments/env_1/assistants")
        assert response.status_code == 404
        assert response.json() == {"detail": "Environment not found"}
