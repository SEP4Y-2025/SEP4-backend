from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId
from utils.helper import convert_object_ids
import traceback

class EnvironmentsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["environments"]

    def get_environments(self):
        try:
            projection = {"_id": 1, "name": 1}
            environments = list(self.collection.find({}, projection))

            if not environments:
                print("No environments found in database")
                return []

            return convert_object_ids(environments)
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching environments: {e}")
            return []
    
    def get_environment_by_id(self, environment_id: str):
       env = self.collection.find_one({"_id": ObjectId(environment_id)})   
       return env if env else None
        