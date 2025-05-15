from repositories.environments_repository import EnvironmentsRepository
from models.environment import AddEnvironmentRequest, AddEnvironmentResponse
from bson import ObjectId
import datetime


class EnvironmentsService:
    def __init__(self):
        self.environments_repository = EnvironmentsRepository()

    def get_environments(self):
        result = self.environments_repository.get_environments()
        print(
            f"Environments service returned {len(result) if result else 0} environments"
        )
        return result

    def get_environment_by_id(self, environment_id: str):
        return self.environments_repository.get_environment_by_id(environment_id)
    
    def add_environment(self, request: AddEnvironmentRequest) -> AddEnvironmentResponse: 
        environment_dict = request.dict()
        inserted_id = self.environments_repository.add_environment(environment_dict)
        return AddEnvironmentResponse(
            message="Environment created successfully",
            environment_id=inserted_id,
            name=request.name
        )