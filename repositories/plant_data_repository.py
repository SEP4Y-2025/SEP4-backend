from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId
import traceback


class PlantDataRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["plant_data"]

    def get_latest_data(self, plant_pot_id=None):
        try:
            query = {}
            if plant_pot_id:
                query["plant_pot_id"] = plant_pot_id

            if plant_pot_id:
                data = list(self.collection.find(query).sort("timestamp", -1).limit(1))
            else:
                data = list(self.collection.find().sort("timestamp", -1).limit(1))

            return data
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching plant data: {e}")
            return []

    def get_all_data(self):
        try:
            data = list(self.collection.find())
            if not data:
                print("No plant data found in database")
                return []

            for item in data:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return data
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching all plant data: {e}")
            return []
