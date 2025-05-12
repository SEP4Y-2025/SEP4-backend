from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str

class RegisterRequest(BaseModel):
    name: str
    username: str
    password: str
    email: EmailStr
#I created a new response model for registration process which includes more user info, not only the token :)
class RegisterResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    access_token: str
    token_type: str = "bearer"
    expires_in: int
