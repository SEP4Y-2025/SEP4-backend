# This was my refference:
# https://blog.marzeta.pl/python-and-jwt-a-comprehensive-guide-to-secure-sessions/#:~:text=Implementing%20JWTs%20with%20Python&text=In%20this%20code%2C%20we%20first,and%20the%20decoded%20JWT%20payload.

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import PyJWTError
from services.auth_service import SECRET_KEY, ALGORITHM
from repositories.auth_repository import AuthRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")

        if username is None or user_id is None:
            raise credentials_exception

    except PyJWTError:
        raise credentials_exception

    user = AuthRepository().find_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user