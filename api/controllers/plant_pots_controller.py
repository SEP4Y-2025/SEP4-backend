# api/endpoints/pot.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.plant_pots_service import PlantPotsService
from models.plant_pot import AddPlantPotRequest, PlantPotResponse
from bson import ObjectId
from core.config import MONGO_URI

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
 
@router.get("/logs")
def get_logs():
    print("Received GET /logs.")
    try:
        logs = [
        "10.34 - plant watered",
        "10.58 - window closed",
        "18.34 - plant watered",
    ]
        return JSONResponse(content={"logs": logs})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environments/{environment_id}/pots/{pot_id}")
def get_plant_pot(pot_id: str):
    try:
        pot = PlantPotsService().get_plant_pot_by_id(pot_id)
        if not pot:
            return {"detail": f"PlantPot with Id {pot_id} not found"}
        return {"pot": pot}
    except Exception as e:
        return {"detail": f"Unexpected error: {str(e)}"}
    
@router.get("/environments/{environment_id}/pots")
def get_pots_by_environment(environment_id: str):
    try:
        if not ObjectId.is_valid(environment_id):
            raise HTTPException(status_code=400, detail="Invalid environment ID")
        
        service = PlantPotsService()
        pots = service.get_pots_by_environment(environment_id)
        
        if not pots:
            raise HTTPException(status_code=404, detail="No plant pots found for the given environment")
        
        return {"pots": pots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/enivironments/{environment_id}/pots/{pot_id}")
def delete_plant_pot(pot_id: str):
    try:
        service = PlantPotsService()
        service.delete_plant_pot(pot_id)
        return {"message": "Plant pot deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    
