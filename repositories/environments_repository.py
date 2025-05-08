from pymongo import MongoClient
from bson import ObjectId
from core.config import MONGO_URI, DB_NAME

class EnvironmentsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["environments"]

    def insert_environment(self, env_data: dict):
        result = self.collection.insert_one(env_data)
        return str(result.inserted_id)

    def get_environment(self, env_id: str):
        return self.collection.find_one({"_id": ObjectId(env_id)})

    def update_environment(self, env_id: str, update_data: dict):
        return self.collection.update_one({"_id": ObjectId(env_id)}, {"$set": update_data})

    def delete_environment(self, env_id: str):
        return self.collection.delete_one({"_id": ObjectId(env_id)})
