#models/pot.py

from pydantic import BaseModel

class AddPlantPotRequest(BaseModel):
    plant_pot_label: str
    pot_id: str
    watering_frequency: int
    water_dosage: int
    
class PlantPotResponse(BaseModel):
    message: str
    pot_id: str
    plant_pot_label: str
    watering_frequency: int
    water_dosage: int