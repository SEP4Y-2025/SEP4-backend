from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from py_object_id import PyObjectId 

class PlantPot(BaseModel):
    #id: PyObjectId = Field(..., alias="_id") 
    id: str = Field(alias="_id")  # Accepts custom string
    plant_pot_label: str
    plant_type_id: PyObjectId
    environment_id: PyObjectId

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}