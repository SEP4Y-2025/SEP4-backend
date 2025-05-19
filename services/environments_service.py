from repositories.environments_repository import EnvironmentsRepository
from models.environment import AddEnvironmentRequest, AddEnvironmentResponse
from bson import ObjectId
import datetime
from services.plant_pots_service import PlantPotsService
from repositories.users_repository import UsersRepository


class EnvironmentsService:
    def __init__(self):
        self.environments_repository = EnvironmentsRepository()
        self.plant_pots_service = PlantPotsService()
        self.user_repository = UsersRepository()

    def get_environments(self):
        result = self.environments_repository.get_environments()
        print(
            f"Environments service returned {len(result) if result else 0} environments"
        )
        return result

    def get_environment_by_id(self, environment_id: str):
        return self.environments_repository.get_environment_by_id(environment_id)

    def add_environment(self, request: AddEnvironmentRequest, request_user_id: str) -> AddEnvironmentResponse:
        if self.environments_repository.environment_name_exists(request_user_id, request.name):
            raise ValueError("Environment name already exists for this user.")
        environment_dict = request.dict()
        environment_dict.setdefault("owner_id", request_user_id)
        environment_dict.setdefault("window_state", "closed")
        environment_dict["access_control"] = [
            {
                "user_id": ObjectId(request_user_id),
                "role": "Owner",
            }
        ]
        environment_dict.setdefault("plant_pots", [])
        inserted_id = self.environments_repository.add_environment(environment_dict, request_user_id)
        self.user_repository.add_environment_to_user(
            request_user_id,
            {
                "environment_id": inserted_id,
                "role": "Owner",
            },
        )
        return AddEnvironmentResponse(
            message="Environment created successfully",
            environment_id=inserted_id,
            name=request.name,
        )

    def delete_environment(self, environment_id: str) -> bool:
        environment = self.environments_repository.get_environment_by_id(environment_id)
        if not environment:
            raise ValueError(f"Environment with ID {environment_id} not found")

        for pot in environment.get("plant_pots", []):
            pot_id = pot.get("pot_id")
            if pot_id:
                try:
                    self.plant_pots_service.delete_plant_pot(pot_id)
                except Exception as e:
                    print(f"Failed to delete pot {pot_id}: {e}")
            
        self.user_repository.remove_environment_from_user(
            environment["owner_id"], environment_id
        )

        return self.environments_repository.delete_environment(environment_id)
