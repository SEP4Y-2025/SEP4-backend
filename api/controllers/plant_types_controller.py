# api/endpoints/plant_types.py

from fastapi import APIRouter, HTTPException
from services.plant_types_service import PlantTypesService

router = APIRouter()


@router.get("/environments/{environment_id}/plant_types")
def get_plant_types_by_environment(environment_id: str):
    try:
        service = PlantTypesService()
        plantTypes = service.get_all_plant_types(environment_id)
        return {"PlantTypes": plantTypes}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from pydantic import BaseModel


class AddPlantTypeRequest(BaseModel):
    name: str
    water_frequency: int
    water_dosage: int


# testing


class AddPlantTypeResponse(BaseModel):
    message: str
    plantTypeId: str


@router.post("/environments/{environment_id}/plant_types")
def add_plant_type(environment_id: str, plant_type: AddPlantTypeRequest):
    try:
        service = PlantTypesService()
        plant_type_data = plant_type.dict()
        plant_type_data["plant_env_id"] = environment_id
        plant_type_id = service.add_plant_type(plant_type_data)
        return AddPlantTypeResponse(
            message="Plant type added successfully", plantTypeId=plant_type_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
