from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from models.auth import TokenResponse, RegisterRequest, PasswordUpdateRequest
from services.auth_service import AuthService
from datetime import timedelta
from utils.jwt_middleware import decode_jwtheader


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/auth/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        auth_service = AuthService()
        user = auth_service.authenticate_user(form_data.username, form_data.password)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=30)
        token_data = auth_service.create_access_token(
            data={
                "sub": user["username"],
                "email": user["email"],
                "id": str(user["_id"]),
            },
            expires_delta=access_token_expires,
        )

        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user_id=str(user["_id"]),
        )
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/registration")
async def register(user_data: RegisterRequest):
    try:
        auth_service = AuthService()
        user_id = auth_service.create_user(
            user_data.username, user_data.password, user_data.email
        )

        if not user_id:
            raise HTTPException(status_code=400, detail="Username already exists")

        return {"message": "User created successfully", "user_id": user_id}
    except Exception as e:
        import traceback

        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/auth/password")
async def update_password(
    data: PasswordUpdateRequest, Authorization: str = Header(None)
):
    try:
        user_id = decode_jwtheader(Authorization)
        if not data.new_password or not data.old_password.strip():
            raise HTTPException(status_code=400, detail="New password cannot be empty")
        auth_service = AuthService()
        success = auth_service.change_password(
            user_id, data.old_password, data.new_password
        )
        if not success:
            raise HTTPException(status_code=400, detail="Failed to change password")
        return {"message": "Password changed successfully"}
    except Exception as e:
        import traceback

        print(f"Change password error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
