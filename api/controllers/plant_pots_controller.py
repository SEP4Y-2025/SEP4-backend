# api/endpoints/pot.py
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from services.plant_pots_service import PlantPotsService
from models.plant_pot import AddPlantPotRequest, AddPlantPotResponse
from bson import ObjectId
from utils.jwt_middleware import decode_jwtheader

router = APIRouter()


@router.post("/environments/{env_id}/pots", response_model=AddPlantPotResponse)
def add_plant_pot(env_id: str, pot: AddPlantPotRequest, Authorization: str = Header(None)):
    try:
        request_user_id = decode_jwtheader(Authorization)
        return PlantPotsService().add_plant_pot(env_id, pot, request_user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
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
        pot = PlantPotsService().get_plant_pot_by_id(environment_id, pot_id)
        if not pot:
            raise HTTPException(status_code=404, detail="Plant pot not found")
        return {"pot": pot}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "timeout" in str(e).lower():
            raise HTTPException(status_code=408, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environments/{environment_id}/pots")
def get_pots_by_environment(environment_id: str, Authorization: str = Header(None)):
    try:
        if not ObjectId.is_valid(environment_id):
            raise HTTPException(status_code=400, detail="Invalid environment ID")

        user_id = decode_jwtheader(Authorization)
        service = PlantPotsService()
        pots = service.get_pots_by_environment(environment_id,user_id)

        if pots is None:
            raise HTTPException(status_code=500, detail="Internal server error")

        return {"pots": pots}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/environments/{env_id}/pots/{pot_id}")
def delete_pot(env_id: str, pot_id: str, Authorization: str = Header(None)):
    print("Received DELETE /pots/{pot_id} with id=", pot_id)
    try:
        request_user_id = decode_jwtheader(Authorization)
        if PlantPotsService().delete_plant_pot(pot_id, env_id, request_user_id):
            return JSONResponse(
                content={"message": "Pot deleted successfully"}, status_code=200
            )
        else:
            raise HTTPException(status_code=403, detail="Not authorised")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
