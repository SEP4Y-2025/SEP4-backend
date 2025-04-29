# api/endpoints/plant_types.py

from fastapi import APIRouter, HTTPException
from services.plant_types_service import PlantTypesService

router = APIRouter()

@router.get("/plant_types/environments/{environment_id}")
def get_all_plant_types(environment_id: str): 
    print(f"Received GET /plant-types/{environment_id}.")
    try:
        service = PlantTypesService()
        plantTypes = service.get_all_plant_types(environment_id)
        return {"PlantTypes": plantTypes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
