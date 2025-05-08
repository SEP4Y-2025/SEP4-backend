# models/arduino.py
from pydantic import BaseModel

class Arduino(BaseModel):
    id: str
    active: bool = False