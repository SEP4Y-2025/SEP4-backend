
from fastapi import APIRouter, HTTPException
from services.plant_types_service import PlantTypesService
from models.plant_type import AddPlantTypeRequest, PlantTypeResponse

router = APIRouter()

@router.post("/plant-types", response_model=PlantTypeResponse)
def add_plant_type(plant_type: AddPlantTypeRequest):
    try:
        service = PlantTypesService()
        return service.add_plant_type(plant_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
