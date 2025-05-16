from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.user import (
    UserPermissionRequest,
    UserPermissionResponse,
)
from services.users_service import UsersService
from bson import ObjectId
from core.config import MONGO_URI

router = APIRouter()

@router.put(
    "/environments/{environment_id}/assistants",
    response_model=UserPermissionResponse,
)
def add_user_permission(environment_id: str, user_permission: UserPermissionRequest):
    try:
        service = UsersService()
        service.add_permission(environment_id, user_permission.dict())
        return UserPermissionResponse(
            message="User permission added successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.put(
    "/environments/{environment_id}/assistants",
    response_model=UserPermissionResponse,
)

@router.get("/users/{user_id}/environments")
def get_user_environments(user_id: str):
    try:
        service = UsersService()
        environments = service.get_user_environments(user_id)

        return JSONResponse(status_code=200, content={"environments": environments})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}")
def get_user(user_id: str):
    try:
        service = UsersService()
        user = service.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/environments/{environment_id}/assistants/{user_email}",
    response_model=UserPermissionResponse,
)
def delete_user_permission(
    environment_id: str, user_email: str
):
    try:
        service = UsersService()
        service.delete_permission(environment_id, {"user_email": user_email})
        return UserPermissionResponse(message="User permission deleted successfully")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environments/{environment_id}/assistants")
def get_user_permissions(environment_id: str):
    try:
        service = UsersService()
        permissions = service.get_user_permissions(environment_id)
        return JSONResponse(status_code=200, content={"assistants": permissions})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
