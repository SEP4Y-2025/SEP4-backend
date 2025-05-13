from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from utils.helper import convert_object_ids
from bson import ObjectId

class UsersRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.user_collection = self.db["users"]
        self.env_collection = self.db["environments"]

    def add_permission(self, environment_id: str, user: dict):
        user = self.user_collection.find_one({"email": user["user_email"]})
        if not user:
            raise ValueError("Invalid user data: 'user_email' is required")
            user_id = str(user["_id"])
            result = self.env_collection.update_one(
                {"_id": ObjectId(environment_id)},
                {"$addToSet": {"accessControl": {"userId": ObjectId(user_id),
                                                 "role": "Plant Assistant"}}}
            )
            if result.modified_count == 0:
                raise ValueError(f"No environment found with ID {environment_id}")
            else:
                return True
        except Exception as e:
            print(f"Error adding permission: {e}")
            return False
    
    def get_user_environment_ids(self, user_id: str):
        try:
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")

            return user.get("environments", [])
        except Exception as e:
            print(f"Error fetching environment IDs: {e}")
            raise

        user_id = str(user["_id"])
        env = self.env_collection.find_one({"_id": ObjectId(environment_id)})
        if not env:
            raise ValueError(f"No environment found with ID {environment_id}")
            
        if str(env["owner_id"]) == user_id:
            raise ValueError("User is already the owner of this environment")
            
        self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$addToSet": {
                    "environments": {
                        "environment_id": ObjectId(environment_id),
                        "role": "Plant assistant"
                    }
                }
            }
        )

        result = self.env_collection.update_one(
            {"_id": ObjectId(environment_id)},
            {"$addToSet": {"access_control": {"userId": ObjectId(user_id)}}}
        )
        if result.modified_count == 0:
            raise ValueError(f"No environment found with ID {environment_id}")
        else:
            return True
        
    def get_user(self, user_id: str):
        user = self.user_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        return convert_object_ids(user)
