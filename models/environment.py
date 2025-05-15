from pydantic import BaseModel

class AddEnvironmentRequest(BaseModel):
    name: str


class AddEnvironmentResponse(BaseModel):
    message: str
    environment_id: str
    name: str