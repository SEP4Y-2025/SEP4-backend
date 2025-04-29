# service/plant_types_service.py

from models.plant_type import GetAllPlantRequest, GetAllPlantResponse
from repositories.plant_types_repository import PlantTypesRepository
from repositories.arduinos_repository import ArduinosRepository
from core.mqtt_client import mqtt_client

class PlantPotsService:
    def __init__(self):
        self.repository = PlantTypesRepository()
        self.arduinos = ArduinosRepository()

    def get_all_plant_types(self, request: GetAllPlantRequest) -> GetAllPlantResponse:
        environment_id = request.environment_id
        
        plant_type_response = self.repository.get_plant_types_by_environment(environment_id)
        
        if not plant_type_response:
            raise ValueError(f"No plant types found for environment ID: {environment_id}")
        
        
        return GetAllPlantResponse(
            plant_types=plant_type_response
    )