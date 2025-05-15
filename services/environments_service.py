from repositories.environments_repository import EnvironmentsRepository
from models.environment import AddEnvironmentRequest, AddEnvironmentResponse
from services.plant_pots_service import PlantPotsService


class EnvironmentsService:
    def __init__(self):
        self.environments_repository = EnvironmentsRepository()
        self.plant_pots_service = PlantPotsService()
        

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

        return self.environments_repository.delete_environment(environment_id)
