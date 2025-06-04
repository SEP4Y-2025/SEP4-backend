import os
import pytest
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from repositories.plant_pots_repository import PlantPotsRepository

TEST_DB = "sep_test_database"


@pytest.fixture(scope="function")
def plant_pots_repo():
    client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    )
    db = client[TEST_DB]
    db["environments"].delete_many({})
    repo = PlantPotsRepository()
    repo.db = db
    repo.env_collection = db["environments"]
    yield repo
    db["environments"].delete_many({})


def test_insert_pot(plant_pots_repo):
    environment_id = "680f8359688cb5341f9f9c19"
    plant_pots_repo.env_collection.insert_one(
        {
            "_id": ObjectId(environment_id),
            "name": "Test Environment",
            "owner_id": ObjectId("662ebf49c7b9e2a7681e4a53"),
            "window_state": "closed",
            "access_control": [],
            "plant_pots": [],
        }
    )

    pot_data = {
        "pot_id": "pot_1",
        "environment_id": environment_id,
        "label": "Test Pot",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "state": {
            "air_humidity": 30,
            "temperature": 20,
            "soil_humidity": 20,
            "light_intensity": 50,
            "water_level": 750,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }

    pot_data["pot_id"] = "pot_1"
    pot_data["_id"] = pot_data["pot_id"]

    inserted_id = plant_pots_repo.insert_pot(pot_data)
    assert inserted_id == pot_data["pot_id"]

    updated_env = plant_pots_repo.env_collection.find_one(
        {"_id": ObjectId(environment_id)}
    )
    assert any(p["pot_id"] == "pot_1" for p in updated_env["plant_pots"])


def test_get_pot(plant_pots_repo):
    environment_id = "680f8359688cb5341f9f9c19"
    pot_data = {
        "pot_id": "pot_1",
        "label": "Test Pot",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "state": {
            "air_humidity": 30,
            "temperature": 20,
            "soil_humidity": 20,
            "light_intensity": 50,
            "water_level": 750,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }

    plant_pots_repo.env_collection.insert_one(
        {
            "_id": ObjectId(environment_id),
            "name": "Test Environment",
            "plant_pots": [pot_data],
        }
    )

    updated_env = plant_pots_repo.env_collection.find_one(
        {"_id": ObjectId(environment_id)}
    )
    assert "plant_pots" in updated_env
    assert len(updated_env["plant_pots"]) == 1
    assert updated_env["plant_pots"][0]["pot_id"] == "pot_1"


def test_get_pots_by_environment(plant_pots_repo):
    environment_id = "680f8359688cb5341f9f9c19"
    pot1_data = {
        "pot_id": "pot_1",
        "label": "Pot 1",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "state": {
            "air_humidity": 30,
            "temperature": 20,
            "soil_humidity": 20,
            "light_intensity": 50,
            "water_level": 750,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }
    pot2_data = {
        "pot_id": "pot_2",
        "label": "Pot 2",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
        "state": {
            "air_humidity": 20,
            "temperature": 22,
            "soil_humidity": 30,
            "light_intensity": 40,
            "water_level": 500,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }

    # Insert environment with multiple pots
    plant_pots_repo.env_collection.insert_one(
        {
            "_id": ObjectId(environment_id),
            "name": "Test Environment",
            "plant_pots": [pot1_data, pot2_data],
        }
    )

    pots = plant_pots_repo.get_pots_by_environment(environment_id)
    assert len(pots) == 2
    assert pots[0]["label"] == "Pot 1"
    assert pots[1]["label"] == "Pot 2"


def test_delete_pot(plant_pots_repo):
    environment_id = "680f8359688cb5341f9f9c19"
    pot1_data = {
        "pot_id": "pot_1",
        "label": "Pot 1",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "state": {
            "air_humidity": 30,
            "temperature": 20,
            "soil_humidity": 20,
            "light_intensity": 50,
            "water_level": 750,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }
    pot2_data = {
        "pot_id": "pot_2",
        "label": "Pot 2",
        "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
        "state": {
            "air_humidity": 20,
            "temperature": 22,
            "soil_humidity": 30,
            "light_intensity": 40,
            "water_level": 500,
            "water_tank_capacity": 1000,
            "measured_at": datetime.now(),
        },
    }

    plant_pots_repo.env_collection.insert_one(
        {
            "_id": ObjectId(environment_id),
            "name": "Test Environment",
            "plant_pots": [pot1_data, pot2_data],
        }
    )

    assert plant_pots_repo.delete_pot("pot_1") is True
    updated_env = plant_pots_repo.env_collection.find_one(
        {"_id": ObjectId(environment_id)}
    )
    assert len(updated_env["plant_pots"]) == 1
    assert updated_env["plant_pots"][0]["pot_id"] == "pot_2"
