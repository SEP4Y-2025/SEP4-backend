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
        try:
            user = self.user_collection.find_one({"email": user["user_email"]})
            if not user:
                raise ValueError("Invalid user data: 'user_email' is required")
            user_id = user["_id"]

            result = self.env_collection.update_one(
                {"_id": ObjectId(environment_id)},
                {
                    "$addToSet": {
                        "accessControl": {
                            "userId": user_id,
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            if result.modified_count == 0:
                raise ValueError(f"No environment found with ID {environment_id}")

            self.user_collection.update_one(
                {"_id": user_id},
                {
                    "$addToSet": {
                        "environments": {
                            "environment_id": ObjectId(environment_id),
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            return True
        except Exception as e:
            print(f"Error in add_permission: {e}")
            raise

    def get_user_environment_ids(self, user_id: str):
        try:
            user = self.user_collection.find_one(
                {"_id": ObjectId(user_id)}, {"environments.environment_id": 1, "environments.role": 1}
            )
            if not user:
                raise ValueError("User not found")

            environments = user.get("environments", [])
            environment_data = [
                {
                    "environment_id": str(env["environment_id"]),
                    "role": env["role"]
                }
                for env in environments if "environment_id" in env and "role" in env
            ]

            return environment_data
        except Exception as e:
            print(f"Error fetching environment data: {e}")
            raise

    def get_user(self, user_id: str):
        try:
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")

            return convert_object_ids(user)
        except Exception as e:
            print(f"Error in get_user: {e}")
            raise
