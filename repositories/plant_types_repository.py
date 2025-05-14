from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from utils.helper import convert_object_ids
from bson import ObjectId


class PlantTypesRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.env_collection = self.db["environments"]  # for environments
        self.plant_type_collection = self.db["plant_types"]  # for plant types

    def get_plant_type_by_id(self, plant_type_id: str):
        return self.plant_type_collection.find_one({"_id": ObjectId(plant_type_id)})

    def get_environment_by_id(self, environment_id: str):
        try:
            env_obj_id = ObjectId(environment_id)  # Convert to ObjectId
            environment = self.env_collection.find_one({"_id": env_obj_id})
            print(f"Environment found: {environment}")
            return environment
        except Exception as e:
            print(f"Error fetching environment by ID: {e}")
            return None

    def get_plant_types_by_environment(self, environment_id: str):
        try:
            env_obj_id = ObjectId(environment_id)

            plant_types = list(
                self.plant_type_collection.find({"environment_id": env_obj_id})
            )

            if not plant_types:
                print(f"No plant types found for environment ID {environment_id}.")
                return []

            return convert_object_ids(plant_types)

        except Exception as e:
            import traceback

            traceback.print_exc()
            print(f"Error fetching plant types by environment: {e}")
            return []

    def post_plant_type(self, plant_type: dict):
        try:
            plant_type["environment_id"] = ObjectId(plant_type["environment_id"])
            result = self.plant_type_collection.insert_one(plant_type)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting plant type: {e}")
            return None
