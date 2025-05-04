# api/endpoints/pot.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
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


@router.get("/plant_pots/{pot_id}")
def get_plant_pot(pot_id: str):
    print("Received GET /pot with id:", pot_id)
    try:
        return PlantPotsService().get_plant_pot_by_id(pot_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/pots/environments/{environment_id}")
def get_pots_by_environment(environment_id: str):
    try:
        service = PlantPotsService()
        pots = service.get_pots_by_environment(environment_id)
        return {"pots": pots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/pots/{pot_id}")
def delete_plant_pot(pot_id: str):
        try:
            PlantPotsService().delete_plant_pot(pot_id)
            return {"message": f"Plant pot with ID {pot_id} is deleted successfully."}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    
    