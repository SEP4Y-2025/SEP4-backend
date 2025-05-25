import os
import pytest
from pymongo import MongoClient
from bson import ObjectId
from repositories.environments_repository import EnvironmentsRepository

TEST_DB = "sep_test_database"

@pytest.fixture(scope="function")
def env_repo():
    client = MongoClient(os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017"))
    db = client[TEST_DB]
    db["environments"].delete_many({})
    repo = EnvironmentsRepository()
    repo.db = db
    repo.collection = db["environments"]
    yield repo
    db["environments"].delete_many({})

def test_add_and_get_environment(env_repo):
    env = {
        "name": "TestEnv",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    env_id = env_repo.add_environment(env, str(env["owner_id"]))
    assert env_id
    fetched = env_repo.get_environment_by_id(env_id)
    assert fetched is not None
    assert fetched["name"] == "TestEnv"

def test_environment_name_exists(env_repo):
    owner_id = ObjectId()
    env = {
        "name": "UniqueEnv",
        "owner_id": owner_id,
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    env_repo.add_environment(env, str(owner_id))
    assert env_repo.environment_name_exists(str(owner_id), "UniqueEnv") is True
    assert env_repo.environment_name_exists(str(owner_id), "Nonexistent") is False

def test_delete_environment(env_repo):
    env = {
        "name": "ToDelete",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    env_id = env_repo.add_environment(env, str(env["owner_id"]))
    assert env_repo.delete_environment(env_id) is True
    assert env_repo.get_environment_by_id(env_id) is None