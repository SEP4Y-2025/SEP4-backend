from db.database import MongoRepository
from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME

class ArduinosRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["arduinos"]

    def is_registered(self, pot_id: str) -> bool:
        return self.collection.find_one({"_id": pot_id}) is not None

    def mark_active(self, pot_id: str):
        return self.collection.update_one({"_id": pot_id}, {"$set": {"active": True}})
    
    def mark_inactive(self, pot_id: str):
        return self.collection.update_one({"_id": pot_id}, {"$set": {"active": False}})
    
    def get_all_arduinos(self):
        return list(self.collection.find({}))
