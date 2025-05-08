#models/pot.py

from pydantic import BaseModel

class AddPlantPotRequest(BaseModel):
    plant_pot_label: str
    pot_id: str
    plant_type_id: str
    
class PlantPotResponse(BaseModel):
    message: str
    pot_id: str
    plant_pot_label: str
    plant_type_id: str
    plant_type_name: str
    watering_frequency: int
    water_dosage: int

    # Add this to your models/pot.py (or plant_pot.py)
class GetPlantPotResponse(BaseModel):
    pot_id: str
    plant_pot_label: str
    watering_frequency: int
    water_dosage: int
    # Add any other fields needed for retrieving a plant potdis
    environment_id: str
