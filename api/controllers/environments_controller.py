from fastapi import APIRouter, HTTPException, Header
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
from utils.jwt_middleware import decode_jwtheader

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
def add_environment(request: AddEnvironmentRequest, Authorization: str = Header(None)):
    try:
        request_user_id = decode_jwtheader(Authorization)
        service = EnvironmentsService()
        print(request_user_id)
        response = service.add_environment(request, request_user_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})
    except Exception as e:
        raise HTTPException(
            status_code=500, detail={"message": f"An error occurred: {str(e)}"}
        )


@router.delete("/environments/{environment_id}", response_class=JSONResponse)
def delete_environment(environment_id: str, Authorization: str = Header(None)):
    try:
        request_user_id = decode_jwtheader(Authorization)
        service = EnvironmentsService()
        deleted = service.delete_environment(environment_id, request_user_id)
        if not deleted:
            return JSONResponse(
                status_code=403,
                content={"message": "Not authorized to delete this environment"},
            )
        return JSONResponse(
            status_code=200, content={"message": "Environment deleted successfully"}
        )
    except ValueError as e:
        return JSONResponse(status_code=403, content={"message": str(e)})
    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(
            status_code=500, content={"message": f"Internal server error: {str(e)}"}
        )


@router.get("/environments", response_class=JSONResponse)
def get_environments_for_user(Authorization: str = Header(None)):
    try:
        user_id = decode_jwtheader(Authorization)
        service = EnvironmentsService()
        environments = service.get_environments_by_user(user_id)
        return JSONResponse(status_code=200, content={"environments": environments})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
