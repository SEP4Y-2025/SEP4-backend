from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId

class AuthRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["users"]

    def find_user_by_username(self, username: str):
        user = self.collection.find_one({"username": username})
        return user

    def find_user_by_id(self, user_id: str):
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            return None

    def create_user(self, user_data: dict):
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)