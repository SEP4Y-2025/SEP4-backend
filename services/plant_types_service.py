# service/plant_types_service.py

from repositories.plant_types_repository import PlantTypesRepository
from repositories.arduinos_repository import ArduinosRepository

class PlantPotsService:
    def __init__(self):
        self.repository = PlantTypesRepository()
        self.arduinos = ArduinosRepository()

    def get_all_plant_types(self, environment_id: str):
        plant_type_response = self.repository.get_plant_types_by_environment(environment_id)
        
        if not plant_type_response:
            raise ValueError(f"No plant types found for environment ID: {environment_id}")
        
        return plant_type_response