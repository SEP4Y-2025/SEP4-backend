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

    def get_environment_by_id(self, environment_id: str, user_id: str):
        environment = self.environments_repository.get_environment_by_id(environment_id)
        if not environment:
            return None

        # Owner check
        if str(environment.get("owner_id")) == str(user_id):
            return environment

        # Plant Assistant check
        for entry in environment.get("access_control", []):
            if str(entry.get("user_id")) == str(user_id) and entry.get("role") == "Plant Assistant":
                return environment

        raise ValueError("User does not have permission to view this environment")

    def add_environment(
        self, request: AddEnvironmentRequest, request_user_id: str
    ) -> AddEnvironmentResponse:
        if self.environments_repository.environment_name_exists(
            request_user_id, request.name
        ):
            raise ValueError("Environment name already exists for this user.")
        environment_dict = request.dict()
        environment_dict.setdefault("owner_id", ObjectId(request_user_id))
        environment_dict.setdefault("window_state", "closed")
        environment_dict["access_control"] = [
        ]
        environment_dict.setdefault("plant_pots", [])
        inserted_id = self.environments_repository.add_environment(
            environment_dict, request_user_id
        )
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

    def delete_environment(self, environment_id: str, user_id: str) -> bool:
        env = self.environments_repository.get_environment_by_id(environment_id)
        if not env:
            return False
        if str(env.get("owner_id")) != str(user_id):
            raise ValueError("User does not have permission to delete this environment")
        for pot in env.get("plant_pots", []):
            pot_id = pot.get("pot_id")
            if pot_id:
                try:
                    self.plant_pots_service.delete_plant_pot(pot_id)
                except Exception as e:
                    print(f"Failed to delete pot {pot_id}: {e}")

        self.user_repository.remove_environment_from_user(
            env["owner_id"], environment_id
        )

        return self.environments_repository.delete_environment(environment_id)

    def get_environments_by_user(self, user_id: str):
        return self.user_repository.get_user_environment_ids(user_id)
