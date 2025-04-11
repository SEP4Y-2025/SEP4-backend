# api/endpoints/pot.py

from fastapi import APIRouter, HTTPException
from services.plant_pots_service import PlantPotsService
from models.plant_pot import AddPlantPotRequest, PlantPotResponse

router = APIRouter()

@router.post("/pots", response_model=PlantPotResponse)
def add_plant_pot(pot: AddPlantPotRequest):
    print("Received POST /pots with:", pot.model_dump())
    try:
        return PlantPotsService().add_plant_pot(pot)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=str(e))