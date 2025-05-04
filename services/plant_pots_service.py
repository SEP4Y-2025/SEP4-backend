# service/pots_service.py

from models.plant_pot import AddPlantPotRequest, PlantPotResponse, GetPlantPotResponse
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

    def get_plant_pot_by_id(self, pot_id: str):
        pot = self.repository.find_pot_by_id(pot_id)
        if not pot:
            raise ValueError("PlantPot with Id " + pot_id + " not found")
    
        return pot
    
    def get_pots_by_environment(self, environment_id: str):
        return self.repository.get_pots_by_environment(environment_id)
    
    def delete_plant_pot(self, pot_id: str):
        pot = self.repository.find_pot_by_id(pot_id)
        if not pot:
            raise ValueError("Plant pot with id " + pot_id + " not found")
        self.repository.delete_pot(pot_id)
        
        
        