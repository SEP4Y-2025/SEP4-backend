import os
import pytest
from pymongo import MongoClient
from bson import ObjectId
from repositories.users_repository import UsersRepository

TEST_DB = "sep_test_database"

@pytest.fixture(scope="function")
def users_repo():
    client = MongoClient(os.getenv("MONGO_URL", "mongodb://admin:password@localhost:27017"))
    db = client[TEST_DB]
    db["users"].delete_many({})
    db["environments"].delete_many({})
    repo = UsersRepository()
    repo.db = db
    repo.user_collection = db["users"]
    repo.env_collection = db["environments"]
    yield repo
    db["users"].delete_many({})
    db["environments"].delete_many({})

def test_add_permission(users_repo):
    user_param = {
        "user_email": "email1@domain.com"
    }
    
    user_doc = {
        "email": "email1@domain.com",
        "password": "password1",
        "name": "User1",
        "environments": []
    }
    
    environment_id = ObjectId("680f8359688cb5341f9f9c19")
    
    users_repo.user_collection.insert_one(user_doc)
    
    users_repo.env_collection.insert_one({
        "_id": environment_id,
        "name": "Test Environment",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": []
    })
    
    assert users_repo.add_permission(str(environment_id), user_param) is True
    
    updated_user = users_repo.user_collection.find_one({"email": "email1@domain.com"})
    assert updated_user is not None
    assert len(updated_user["environments"]) > 0
    assert updated_user["environments"][0]["environment_id"] == environment_id
    assert updated_user["environments"][0]["role"] == "Plant Assistant"

def test_get_user_environment_ids(users_repo):
    user_doc = {
        "_id": ObjectId("680f8359688cb5341f9f9c18"),
        "email": "email1@domain.com",
        "password": "password1",
        "name": "User1",
        "environments": [
            {
                "environment_id": ObjectId("680f8359688cb5341f9f9c19"),
                "role": "Plant Assistant"
            }
        ]
    }
    
    users_repo.user_collection.insert_one(user_doc)
    
    users_repo.env_collection.insert_one({
        "_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Test Environment",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": []
    })
    
    assert users_repo.get_user_environment_ids("680f8359688cb5341f9f9c18") is not None
    envs = users_repo.get_user_environment_ids("680f8359688cb5341f9f9c18")
    assert len(envs) == 1
    assert envs[0]["environment_id"] == "680f8359688cb5341f9f9c19"
    assert envs[0]["role"] == "Plant Assistant"

def test_delete_user_permission(users_repo):
    user_doc = {
        "_id": ObjectId("680f8359688cb5341f9f9c18"),
        "email": "email1@domain.com",
        "password": "password1",
        "name": "User1",
        "environments": [
            {
                "environment_id": ObjectId("680f8359688cb5341f9f9c19"),
                "role": "Plant Assistant"
            }   
        ]
    }
    users_repo.user_collection.insert_one(user_doc)
    users_repo.env_collection.insert_one({
        "_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Test Environment",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [
            {
                "user_id": ObjectId("680f8359688cb5341f9f9c18"),
                "role": "Plant Assistant"
            }
        ],
        "plant_pots": []
    })
    user_param = {
        "user_email": "email1@domain.com"
    }
    assert users_repo.delete_permission("680f8359688cb5341f9f9c19", user_param) is True    
    updated_user = users_repo.user_collection.find_one({"email": "email1@domain.com"})
    assert updated_user is not None    
    assert len(updated_user["environments"]) == 0
    assert users_repo.env_collection.find_one({"_id": ObjectId("680f8359688cb5341f9f9c19")}) is not None
    assert users_repo.env_collection.find_one({"_id": ObjectId("680f8359688cb5341f9f9c19")})["access_control"] == []

def test_get_user_permissions(users_repo):
    env_id = ObjectId("680f8359688cb5341f9f9c19")
    user_id = ObjectId("680f8359688cb5341f9f9c18")

    user_doc = {
        "_id": user_id,
        "email": "email1@domain.com",
        "password": "password1",
        "name": "User1",
        "environments": [
            {
                "environment_id": env_id,
                "role": "Plant Assistant"
            }
        ]
    }
    users_repo.user_collection.insert_one(user_doc)
    users_repo.env_collection.insert_one({
        "_id": env_id,
        "name": "Test Environment",
        "owner_id": ObjectId(),
        "window_state": "closed",
        "access_control": [
            {
                "user_id": user_id,
                "role": "Plant Assistant"
            }
        ],
        "plant_pots": []
    })

    user_permissions = users_repo.get_user_permissions(str(env_id))
    assert user_permissions is not None
    assert len(user_permissions) == 1
    assert user_permissions[0]["user_id"] == str(user_id)
    assert user_permissions[0]["role"] == "Plant Assistant"

def test_get_user_permissions_not_found(users_repo):
    env_id = ObjectId("680f8359688cb5341f9f9c19")
    with pytest.raises(ValueError, match="Environment not found"):
        users_repo.get_user_permissions(str(env_id))