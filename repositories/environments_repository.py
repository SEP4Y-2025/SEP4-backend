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

    def insert_pot(self, environment_id: str, pot_data: dict):
        try:
            # First, try to update the existing pot if it exists
            result = self.collection.update_one(
                {
                    "_id": ObjectId(environment_id),
                    "plant_pots.pot_id": pot_data["pot_id"],
                },
                {"$set": {"plant_pots.$": pot_data}},
            )

            # If no pot was updated, insert the new one
            if result.matched_count == 0:
                result = self.collection.update_one(
                    {"_id": ObjectId(environment_id)},
                    {"$push": {"plant_pots": pot_data}},
                )

            return result.modified_count > 0
        except Exception as e:
            traceback.print_exc()
            return False

    def get_pots_by_environment(self, environment_id: str):
        try:
            env = self.collection.find_one(
                {"_id": ObjectId(environment_id)},
                {"plant_pots": 1},
            )
            return convert_object_ids(env.get("plant_pots", [])) if env else []
        except Exception as e:
            traceback.print_exc()
            return []

    def find_pot_by_id(self, pot_id: str):
        try:
            pipeline = [
                {"$match": {"plant_pots.pot_id": pot_id}},
                {"$project": {"plant_pots": 1}},
                {"$unwind": "$plant_pots"},
                {"$match": {"plant_pots.pot_id": pot_id}},
                {"$replaceRoot": {"newRoot": "$plant_pots"}},
            ]
            result = list(self.collection.aggregate(pipeline))
            return convert_object_ids(result[0]) if result else None
        except Exception as e:
            traceback.print_exc()
            return None

    def update_pot(self, pot_id: str, update_data: dict):
        try:
            result = self.collection.update_one(
                {"plant_pots.pot_id": pot_id},
                {"$set": {f"plant_pots.$.{k}": v for k, v in update_data.items()}},
            )
            return result.modified_count > 0
        except Exception as e:
            traceback.print_exc()
            return False

    def delete_pot(self, pot_id: str):
        try:
            result = self.collection.update_many(
                {},
                {"$pull": {"plant_pots": {"pot_id": pot_id}}},
            )
            return result.modified_count > 0
        except Exception as e:
            traceback.print_exc()
            return False

    def add_environment(self, environment: dict) -> str:
        try:
            result = self.collection.insert_one(environment)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding environment: {e}")
            raise Exception("An error occurred while adding the environment.")

    def delete_environment(self, environment_id: str):
        result = self.collection.delete_one({"_id": ObjectId(environment_id)})
        return result.deleted_count > 0
