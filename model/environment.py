from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
import pydantic
from py_object_id import PyObjectId
from typing import List

class Environment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    environment_name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

