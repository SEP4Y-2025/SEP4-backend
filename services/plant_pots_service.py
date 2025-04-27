# service/pots_service.py

from models.plant_pot import AddPlantPotRequest, PlantPotResponse
from repositories.plant_pots_repository import PlantPotsRepository
from repositories.arduinos_repository import ArduinosRepository
from core.mqtt_client import mqtt_client

class PlantPotsService:
    def __init__(self):
        self.repository = PlantPotsRepository()
        self.arduinos = ArduinosRepository()

    def add_plant_pot(self, pot : AddPlantPotRequest) -> PlantPotResponse:
        if not self.arduinos.is_registered(pot.pot_id):
            raise ValueError("Unknown or unregistered Arduino")
        
        payload = {
            "command": "pots/add",
            "pot_id": pot.pot_id,
            "frequency": pot.watering_frequency,
            "dosage": pot.water_dosage
        }
        
        result = mqtt_client.send(f"{pot.pot_id}/pots/add", payload)

        if result.get("error"):
            raise ValueError(result["error"])
        
        self.repository.insert_pot({"_id": pot.pot_id, **pot.model_dump()})
        self.arduinos.mark_active(pot.pot_id)
    
        return PlantPotResponse(
            message="Pot added successfully",
            **pot.model_dump())
    
    def get_pots_by_environment(self, environment_id: str):
        return self.repository.get_pots_by_environment(environment_id)
        