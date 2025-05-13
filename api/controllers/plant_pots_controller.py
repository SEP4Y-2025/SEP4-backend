# api/endpoints/pot.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.plant_pots_service import PlantPotsService
from models.plant_pot import AddPlantPotRequest, AddPlantPotResponse
from bson import ObjectId

router = APIRouter()


@router.post("/environments/{env_id}/pots", response_model=AddPlantPotResponse)
def add_plant_pot(env_id : str, pot: AddPlantPotRequest):
    print("Received POST /pots with:", pot.model_dump())
    try:
        return PlantPotsService().add_plant_pot(env_id, pot)
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
def get_plant_pot(environment_id: str, pot_id: str):
    try:
        return PlantPotsService().get_plant_pot_by_id(environment_id, pot_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/environments/{environment_id}/pots")
def get_pots_by_environment(environment_id: str):
    try:
        if not ObjectId.is_valid(environment_id):
            raise HTTPException(status_code=400, detail="Invalid environment ID")

        service = PlantPotsService()
        pots = service.get_pots_by_environment(environment_id)

        if not pots:
            raise HTTPException(
                status_code=404, detail="No plant pots found for the given environment"
            )

        return {"pots": pots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/environments/{env_id}/pots/{pot_id}")
def delete_pot(env_id: str, pot_id: str):
    print("Received DELETE /pots/{pot_id} with id=", pot_id)
    try:
        if PlantPotsService().delete_plant_pot(pot_id):
            return JSONResponse(
                content={"message": "Pot deleted successfully"}, status_code=200
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
