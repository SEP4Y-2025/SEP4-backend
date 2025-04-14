from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
import pydantic
from py_object_id import PyObjectId

class PlantType(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    plant_type_name: str
    watering_frequency: str
    water_dosage: str
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}