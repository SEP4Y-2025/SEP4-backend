from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME

class PlantTypesRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["plant_types"]

    def add_plant_type(self, plant_type_data: dict):
        result = self.collection.insert_one(plant_type_data)
        return str(result.inserted_id)
