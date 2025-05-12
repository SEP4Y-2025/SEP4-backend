from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.auth import TokenResponse, RegisterRequest, RegisterResponse
from services.auth_service import AuthService
from datetime import timedelta

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
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=30)
        token_data = auth_service.create_access_token(
            data={"sub": user["username"], "id": str(user["_id"])},
            expires_delta=access_token_expires
        )

        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user_id=str(user["_id"])
        )
    except Exception as e:
        import traceback
        print(f"Login error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/auth/register", response_model=RegisterResponse)
async def register(user_data: RegisterRequest):
    try:
        auth_service = AuthService()
        result = auth_service.create_user(
            name=user_data.name, 
            username=user_data.username, 
            password=user_data.password,
            email=user_data.email
        )
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        return RegisterResponse(**result)
    except Exception as e:
        import traceback
        print(f"Registration error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )