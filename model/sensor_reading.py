from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
import pydantic
from py_object_id import PyObjectId
from datetime import datetime

class SensorReading(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    plant_pot_id: PyObjectId
    timestamp: datetime
    soil_moisture: float
    air_humidity: float
    light_intensity: float
    temperature: float
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}