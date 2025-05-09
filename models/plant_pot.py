#models/pot.py

from pydantic import BaseModel
from datetime import datetime

class AddPlantPotRequest(BaseModel):
    plant_pot_label: str
    pot_id: str
    plant_type_id: str
    
class AddPlantPotResponse(BaseModel):
    message: str
    pot_id: str
    plant_pot_label: str
    plant_type_id: str
    plant_type_name: str
    watering_frequency: int
    water_dosage: int
    environment_id: str

class GetPlantPotResponse(BaseModel):
    pot_id: str
    plant_pot_label: str
    plant_type_id: str
    plant_type_name: str
    watering_frequency: int
    water_dosage: int
    environment_id: str
    soil_humidity_percentage: int
    air_humidity_percentage: int
    temperature_celsius: float
    light_intensity_lux: int
    water_tank_capacity_ml: int
    current_water_level_percentage: int
    measured_at: datetime
    