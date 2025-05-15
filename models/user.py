# models/pot.py

from pydantic import BaseModel


class UserPermissionRequest(BaseModel):
    user_email: str

class UserPermissionResponse(BaseModel):
    message: str