from main import app
from fastapi.testclient import TestClient
from pymongo import MongoClient
import pytest
from core.seed_arduinos import run_seed_data
import os
from unittest.mock import patch


@pytest.fixture(scope="function")
def seeded_test_db():
    client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    )
    db = client["sep_database"]

    db["arduinos"].delete_many({})
    db["environments"].delete_many({})
    db["plant_types"].delete_many({})
    db["users"].delete_many({})

    run_seed_data()

    yield db

    db["arduinos"].delete_many({})
    db["environments"].delete_many({})
    db["plant_types"].delete_many({})
    db["users"].delete_many({})


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
