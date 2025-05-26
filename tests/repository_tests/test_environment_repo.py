import os
import pytest
from pymongo import MongoClient
from bson import ObjectId
from repositories.environments_repository import EnvironmentsRepository

TEST_DB = "sep_test_database"


@pytest.fixture(scope="function")
def env_repo():
    client = MongoClient(
        os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017")
    )
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


def test_get_environments(env_repo):
    owner_id = ObjectId()
    env1 = {
        "name": "Env1",
        "owner_id": owner_id,
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    env2 = {
        "name": "Env2",
        "owner_id": owner_id,
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [],
    }
    env_repo.add_environment(env1, str(owner_id))
    env_repo.add_environment(env2, str(owner_id))

    environments = env_repo.get_environments()
    assert len(environments) == 2
    assert any(e["name"] == "Env1" for e in environments)
    assert any(e["name"] == "Env2" for e in environments)


def test_get_environment_by_id_not_found(env_repo):
    fetched = env_repo.get_environment_by_id(ObjectId())
    assert fetched is None


def test_get_pot_by_environment(env_repo):
    env = {
        "name": "EnvWithPots",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [{"pot_id": ObjectId(), "name": "Pot1"}],
    }
    env_id = env_repo.add_environment(env, str(env["owner_id"]))
    fetched = env_repo.get_environment_by_id(env_id)
    assert fetched is not None
    assert len(fetched["plant_pots"]) == 1
    assert fetched["plant_pots"][0]["name"] == "Pot1"


def test_update_pot_in_environment(env_repo):
    env = {
        "name": "EnvToUpdate",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [{"pot_id": ObjectId(), "name": "OldPot"}],
    }
    env_id = env_repo.add_environment(env, str(env["owner_id"]))

    updated_pot = {"pot_id": env["plant_pots"][0]["pot_id"], "name": "UpdatedPot"}
    env_repo.update_pot(env_id, updated_pot)

    fetched = env_repo.get_environment_by_id(env_id)
    assert fetched is not None
    assert len(fetched["plant_pots"]) == 1
    assert fetched["plant_pots"][0]["name"] == "OldPot"
