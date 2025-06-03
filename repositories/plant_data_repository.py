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
                return []

            for item in data:
                if "_id" in item and isinstance(item["_id"], ObjectId):
                    item["_id"] = str(item["_id"])

            return data
        except Exception as e:
            traceback.print_exc()
            print(f"Error fetching all plant data: {e}")
            return []

    def get_historical_data(self, pot_id: str):
        readings = list(
            self.collection.find({"plant_pot_id": pot_id})
            .sort("timestamp", -1)
            .limit(10)
        )
        return readings

    def delete_by_pot(self, pot_id: str):
        # Delete all sensor readings associated with the given pot_id
        result = self.collection.delete_many({"plant_pot_id": pot_id})
        return result.deleted_count  # Return the number of documents deleted
    
    def create(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)