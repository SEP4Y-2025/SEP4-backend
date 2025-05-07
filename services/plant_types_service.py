# service/plant_types_service.py

from repositories.plant_types_repository import PlantTypesRepository
from repositories.arduinos_repository import ArduinosRepository

class PlantTypesService:
    def __init__(self):
        self.repository = PlantTypesRepository()
        self.arduinos = ArduinosRepository()

    def get_all_plant_types(self, environment_id: str):
        plant_type_response = self.repository.get_plant_types_by_environment(environment_id)
        
        if not plant_type_response:
            raise ValueError(f"No plant types found for environment ID: {environment_id}")
        
        return plant_type_response
    
    def add_plant_type(self, plant_type: dict):
        # Validate required fields
        if not plant_type.get("name") or not plant_type.get("plant_env_id"):
            raise ValueError("Invalid plant type data: 'plant_type_name' and 'plant_env_id' are required")

        # Check if the environment exists
        environment = self.repository.get_environment_by_id(plant_type["plant_env_id"])
        if not environment:
            raise ValueError(f"Environment ID {plant_type['plant_env_id']} does not exist")

        # Insert the plant type into the database
        return self.repository.post_plant_type(plant_type)