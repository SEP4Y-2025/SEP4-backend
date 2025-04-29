from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME

class PlantTypesRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["plant_types"]

    def get_plant_types_by_environment(self, environment_id: str):
        return list(self.collection.find({"environment_id": environment_id}))
