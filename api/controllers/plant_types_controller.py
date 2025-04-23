# api/endpoints/plant_types.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.plant_types_service import PlantTypesService
from models.plant_type import GetAllPlantRequest, GetAllPlantResponse

router = APIRouter()

@router.get("/plant_types/{environment_id}", response_model=GetAllPlantResponse)
def get_all_plant_types(environment_id: str): 
    print(f"Received GET /plant-types/{environment_id}.")
    try:
        return PlantTypesService().get_all_plant_types(environment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
