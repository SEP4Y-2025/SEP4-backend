from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME

class PlantPotsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["plant_pots"]

    def insert_pot(self, pot_data: dict):
        try:
            result = self.collection.insert_one(pot_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting pot: {e}")
            return None

    def get_pot(self, pot_id: str):
        return self.collection.find_one({"_id": pot_id})

    def update_pot(self, pot_id: str, update_data: dict):
        return self.collection.update_one({"_id": pot_id}, {"$set": update_data})
