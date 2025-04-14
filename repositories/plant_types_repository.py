from pymongo import MongoClient
from bson import ObjectId
from core.config import MONGO_URI, DB_NAME

class PlantTypesRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["plant_types"]

    def create(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get(self, plant_type_id: str):
        return self.collection.find_one({"_id": ObjectId(plant_type_id)})

    def update(self, plant_type_id: str, data: dict):
        return self.collection.update_one({"_id": ObjectId(plant_type_id)}, {"$set": data})

    def delete(self, plant_type_id: str):
        return self.collection.delete_one({"_id": ObjectId(plant_type_id)})
