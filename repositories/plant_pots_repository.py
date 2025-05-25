from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId
from utils.helper import convert_object_ids


class PlantPotsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.env_collection = self.db["environments"]

    def insert_pot(self, pot_data: dict):
        try:
            environment_id = pot_data.get("environment_id")
            pot_id = pot_data.get("pot_id")

            if not pot_id or not environment_id:
                raise ValueError("Pot data must include 'pot_id' and 'environment_id'")

            self.env_collection.update_one(
                {"_id": ObjectId(environment_id)},
                {"$addToSet": {"plant_pots": pot_data}}
            )
            return pot_id
        except Exception as e:
            print(f"Error inserting pot: {e}")
            return None

        
    def get_pots_by_environment(self, environment_id: str):
        try:
            env_obj_id = ObjectId(environment_id)
            environment = self.env_collection.find_one({"_id": env_obj_id})
            pots = environment.get("plant_pots", [])
            return convert_object_ids(pots)
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Error fetching pots by environment: {e}")
            return []

    def delete_pot(self, pot_id: str):
        result = self.env_collection.update_one(
            {"plant_pots.pot_id": pot_id},
            {"$pull": {"plant_pots": {"pot_id": pot_id}}}
        )
        return result.modified_count > 0
