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
    environment_id: str