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