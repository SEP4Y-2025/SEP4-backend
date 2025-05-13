#models/pot.py

from pydantic import BaseModel

class AddUserPermissionRequest(BaseModel):
    user_email: str
    
class AddUserPermissionResponse(BaseModel):
    message: str