from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME


class SensorReadingsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db["sensor_readings"]

    def create(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def get_latest_by_pot(self, pot_id: str):
        return self.collection.find_one(
            {"plant_pot_id": pot_id}, sort=[("timestamp", -1)]
        )

    def get_all_by_pot(self, pot_id: str):
        return list(self.collection.find({"plant_pot_id": pot_id}))

    def delete_by_pot(self, pot_id: str):
        # Delete all sensor readings associated with the given pot_id
        result = self.collection.delete_many({"plant_pot_id": pot_id})
        return result.deleted_count  # Return the number of documents deleted

    def get_historical_data(self, pot_id: str):
        readings = list(
            self.collection.find({"plant_pot_id": pot_id})
            .sort("timestamp", -1)
            .limit(10)
        )
        return readings
