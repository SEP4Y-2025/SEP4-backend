from pydantic import BaseModel

class AddPlantTypeRequest(BaseModel):
    plant_type_label: str
    plant_description: str

class PlantTypeResponse(BaseModel):
    message: str
    plant_type_label: str
    plant_description: str