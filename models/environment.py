# models/environment.py
from pydantic import BaseModel


class AddEnvironmentRequest(BaseModel):
    name: str
    window_state: str = "closed"
    access_control: list = []
    plant_pots: list = []

class AddEnvironmentResponse(BaseModel):
    message: str
    environment_id: str
    name: str
