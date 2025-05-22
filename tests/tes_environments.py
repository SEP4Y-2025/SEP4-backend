import pytest
from fastapi.testclient import TestClient
from main import app  # Adjust if your FastAPI app is in a different file

client = TestClient(app)


def test_add_get_delete_environment():
    # 1. Add environment
    payload = {"name": "Test Environment"}
    response = client.post("/environments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Environment created successfully"
    env_id = data["environment_id"]
    assert env_id

    # 2. Get environment by id
    get_response = client.get(f"/environments/{env_id}")
    assert get_response.status_code == 200
    assert get_response.json()["environment"]["_id"] == env_id
    assert get_response.json()["environment"]["name"] == "Test Environment"

    # 3. Get all environments (should include the new one)
    all_response = client.get("/environments")
    assert all_response.status_code == 200
    envs = all_response.json()["environments"]
    assert any(e["_id"] == env_id for e in envs)

    # 4. Delete environment
    del_response = client.delete(f"/environments/{env_id}")
    assert del_response.status_code == 200
    assert "deleted" in del_response.json()["message"].lower()

    # 5. Get by id after delete (shoxuld be 404)
    get_after_del = client.get(f"/environments/{env_id}")
    assert get_after_del.status_code == 404


def test_get_environment_not_found():
    response = client.get("/environments/000000000000000000000000")
    assert response.status_code == 404
    assert response.json()["message"] == "Environment not found"


def test_delete_environment_not_found():
    response = client.delete("/environments/000000000000000000000000")
    assert response.status_code == 404
