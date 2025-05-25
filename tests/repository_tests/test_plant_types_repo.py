import os
import pytest
from pymongo import MongoClient
from bson import ObjectId
from repositories.plant_types_repository import PlantTypesRepository

TEST_DB = "sep_test_database"


@pytest.fixture(scope="function")
def plant_types_repo():
    client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    )
    db = client[TEST_DB]
    db["plant_types"].delete_many({})
    db["environments"].delete_many({})
    repo = PlantTypesRepository()
    repo.db = db
    repo.collection = db["plant_types"]
    repo.plant_type_collection = db["plant_types"]
    repo.env_collection = db["environments"]
    yield repo
    db["plant_types"].delete_many({})
    db["environments"].delete_many({})


def test_add_plant_type(plant_types_repo):
    plant_type = {
        "name": "Plant1",
        "id": {"$oid": "680f8359688cb5341f9f9c18"},
        "watering_frequency": 7,
        "water_dosage": 50,
        "environment_id": "680f8359688cb5341f9f9c19",
    }
    plant_type_id = plant_types_repo.post_plant_type(plant_type)
    assert plant_type_id
    fetched = plant_types_repo.get_plant_type_by_id(plant_type_id)
    assert fetched is not None
    assert fetched["name"] == "Plant1"


def test_get_all_plant_types(plant_types_repo):
    plant_type1 = {
        "name": "Plant1",
        "id": {"$oid": "680f8359688cb5341f9f9c18"},
        "watering_frequency": 7,
        "water_dosage": 50,
        "environment_id": "680f8359688cb5341f9f9c19",
    }

    plant_type2 = {
        "name": "Plant2",
        "id": {"$oid": "680f8359688cb5341f9f9c17"},
        "watering_frequency": 2,
        "water_dosage": 70,
        "environment_id": "680f8359688cb5341f9f9c19",
    }
    plant_types_repo.post_plant_type(plant_type1)
    plant_types_repo.post_plant_type(plant_type2)

    all_plants = plant_types_repo.get_plant_types_by_environment(
        "680f8359688cb5341f9f9c19"
    )
    assert len(all_plants) == 2
    assert all_plants[0]["name"] == "Plant1"
    assert all_plants[1]["name"] == "Plant2"


def test_get_plant_type_by_id(plant_types_repo):
    plant_type = {
        "name": "Plant1",
        "id": {"$oid": "680f8359688cb5341f9f9c18"},
        "watering_frequency": 7,
        "water_dosage": 50,
        "environment_id": "680f8359688cb5341f9f9c19",
    }
    plant_type_id = plant_types_repo.post_plant_type(plant_type)
    fetched = plant_types_repo.get_plant_type_by_id(plant_type_id)
    assert fetched is not None
    assert fetched["name"] == "Plant1"


def test_get_plant_type_by_id_not_found(plant_types_repo):
    fetched = plant_types_repo.get_plant_type_by_id(
        ObjectId("680f8359688cb5341f9f9c18")
    )
    assert fetched is None


def test_get_environment_by_id(plant_types_repo):
    environment = {
        "_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Test Environment",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    plant_types_repo.env_collection.insert_one(environment)

    fetched_env = plant_types_repo.get_environment_by_id("680f8359688cb5341f9f9c19")
    assert fetched_env is not None
    assert fetched_env["_id"] == ObjectId("680f8359688cb5341f9f9c19")
    assert fetched_env["name"] == "Test Environment"


def test_add_plant_type_fail(plant_types_repo):
    plant_type = {"name": "Plant1", "watering_frequency": 7, "water_dosage": 50}
    assert plant_types_repo.post_plant_type(plant_type) is None
