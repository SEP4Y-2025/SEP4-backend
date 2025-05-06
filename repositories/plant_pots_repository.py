from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId
from utils.helper import convert_object_ids

class PlantPotsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["environments"]

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
    
    def find_pot_by_id(self, pot_id: str): 
        pot_obj_id = ObjectId(pot_id)
        environment = self.collection.find_one({"plantPots.potId": pot_obj_id})
        if environment:
            for pot in environment["plantPots"]:
                if pot["potId"] == pot_obj_id:
                    return convert_object_ids(pot)
        return None

    def get_pots_by_environment(self, environment_id: str):
        return list(self.collection.find({"environment_id": environment_id}))
    
    def delete_pot(self, pot_id: str):
        return self.collection.delete_one({"_id": pot_id})
