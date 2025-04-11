# db/database.py
from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME

class MongoRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]

    def get_collection(self, name:str):
        return self.db[name]

    def insert_one(self, collection_name: str, document: dict):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find_one(self, collection_name: str, query: dict):
        return self.get_collection(collection_name).find_one(query)

    def update_one(self, collection_name: str, query: dict, update: dict):
        return self.get_collection(collection_name).update_one(query, update)
    
    