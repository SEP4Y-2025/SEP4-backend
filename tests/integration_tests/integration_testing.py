import os
from bson import ObjectId
import pytest

os.environ["MONGO_URL"] = "mongodb://admin:password@localhost:27017"
os.environ["MONGO_DB"] = "sep_test_database"
from main import app
from fastapi.testclient import TestClient
from pymongo import MongoClient
from unittest.mock import patch


@pytest.fixture(scope="function")
def seeded_test_db():
    client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    )

    # Use separate test database
    test_db_name = "sep_test_database"
    db = client[test_db_name]

    db["arduinos"].delete_many({})
    db["environments"].delete_many({})
    db["plant_types"].delete_many({})
    db["users"].delete_many({})
    db["plant_data"].delete_many({})

    yield db

    db["arduinos"].delete_many({})
    db["environments"].delete_many({})
    db["plant_types"].delete_many({})
    db["users"].delete_many({})
    db["plant_data"].delete_many({})


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_get_plant_types_with_real_db(client, seeded_test_db):
    with patch(
        "api.controllers.plant_types_controller.decode_jwtheader",
        return_value="662ebf49c7b9e2a7681e4a53",
    ):
        response = client.get(
            "/environments/680f8359688cb5341f9f9c19/plant_types",
            headers={"Authorization": "Bearer test_token"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "PlantTypes" in data
        assert len(data["PlantTypes"]) == 3


def test_add_environment_with_real_db(client, seeded_test_db):
    with patch(
        "api.controllers.environments_controller.decode_jwtheader",
        return_value="662ebf49c7b9e2a7681e4a53",
    ):
        request_data = {"name": "Integration Test Environment"}
        response = client.post(
            "/environments",
            json=request_data,
            headers={"Authorization": "Bearer test_token"},
        )
        print(response.status_code, response.json())
        assert response.status_code == 200 or response.status_code == 201
        data = response.json()
        assert "environment_id" in data
        assert data["name"] == "Integration Test Environment"

        env = seeded_test_db["environments"].find_one(
            {"_id": ObjectId(data["environment_id"])}
        )
        assert env is not None
        assert env["name"] == "Integration Test Environment"
