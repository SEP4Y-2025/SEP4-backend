from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from services.environments_service import EnvironmentsService
from models.environment import AddEnvironmentRequest, AddEnvironmentResponse
from utils.helper import JSONEncoder
import json
from utils.helper import convert_object_ids
from models.environment import (
    AddEnvironmentRequest,
    AddEnvironmentResponse,
)

router = APIRouter()


@router.get("/environments", response_class=JSONResponse)
def get_environments():
    try:
        service = EnvironmentsService()
        environments = service.get_environments()

        if not environments:
            return JSONResponse(
                status_code=404, content={"message": "No environments found"}
            )

        serialized_data = json.dumps({"environments": environments}, cls=JSONEncoder)
        parsed_data = json.loads(serialized_data)

        return JSONResponse(status_code=200, content=parsed_data)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": f"Internal server error: {str(e)}"}
        )


@router.get("/environments/{environment_id}", response_class=JSONResponse)
def get_environment_by_id(environment_id: str):
    try:
        service = EnvironmentsService()
        environment = service.get_environment_by_id(environment_id)

        if not environment:
            return JSONResponse(
                status_code=404, content={"message": "Environment not found"}
            )

        serialized_data = json.dumps({"environment": environment}, cls=JSONEncoder)
        parsed_data = json.loads(serialized_data)

        return JSONResponse(status_code=200, content=parsed_data)
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": f"Internal server error: {str(e)}"}
        )


@router.post("/environments", response_model=AddEnvironmentResponse)
def add_environment(request: AddEnvironmentRequest):
    try:
        service = EnvironmentsService()
        response = service.add_environment(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": f"An error occurred: {str(e)}"}
        )


@router.delete("/environments/{environment_id}", response_class=JSONResponse)
def delete_environment(environment_id: str):
    try:
        service = EnvironmentsService()
        deleted = service.delete_environment(environment_id)
        if not deleted:
            return JSONResponse(
                status_code=404, content={"message": "Environment could not be deleted"}
            )
        return JSONResponse(
            status_code=200, content={"message": "Environment deleted successfully"}
        )
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": f"Internal server error: {str(e)}"}
        )
