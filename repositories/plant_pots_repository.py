from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId
from utils.helper import convert_object_ids


# How does this work?
# The environment contains multiple plant pots, but the PlantPotsRepository class is responsible for managing plant pots in the database.
# It provides methods to insert, update, delete, and retrieve plant pots and their associated environments.
class PlantPotsRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.env_collection = self.db["environments"]
        self.plant_pots_collection = self.db["plant_pots"]

    def insert_pot(self, pot_data: dict):
        try:
            environment_id = pot_data.get("environment_id")
            pot_id = pot_data.get("_id")  # Must be a string

            if not pot_id or not environment_id:
                raise ValueError("Pot data must include '_id' and 'environment_id'")

            # Insert into plant_pots collection
            self.plant_pots_collection.insert_one(pot_data)

            # Update environment to include this pot ID
            self.env_collection.update_one(
                {"_id": ObjectId(environment_id)}, {"$addToSet": {"plantPots": pot_id}}
            )
            return pot_id
        except Exception as e:
            print(f"Error inserting pot: {e}")
            return None

    def get_pot(self, pot_id: str):
        return self.plant_pots_collection.find_one({"_id": pot_id})

    def update_pot(self, pot_id: str, update_data: dict):
        return self.plant_pots_collection.update_one(
            {"_id": pot_id}, {"$set": update_data}
        )

    def find_pot_by_id(self, pot_id: str):
        pot = self.plant_pots_collection.find_one({"_id": pot_id})
        return pot if pot else None
        # return convert_object_ids(pot) if pot else None

    def get_pots_by_environment(self, environment_id: str):
        try:
            env_obj_id = ObjectId(environment_id)
            environment = self.env_collection.find_one({"_id": env_obj_id})
            pots = environment.get("plantPots", [])
            return convert_object_ids(pots)
        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Error fetching pots by environment: {e}")
            return []

    def delete_pot(self, pot_id: str):
        # Remove from environments
        self.env_collection.update_many(
            {"plantPots": pot_id}, {"$pull": {"plantPots": pot_id}}
        )

        # Delete from plant_pots
        result = self.plant_pots_collection.delete_one({"_id": pot_id})
        if result.deleted_count == 0:
            raise ValueError(f"No plant pot found with ID {pot_id}")
        return True
