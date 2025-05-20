# service/plant_types_service.py

from repositories.plant_types_repository import PlantTypesRepository
from repositories.environments_repository import EnvironmentsRepository
from repositories.arduinos_repository import ArduinosRepository
from services.auth_service import AuthService

class PlantTypesService:
    def __init__(self):
        self.repository = PlantTypesRepository()
        self.arduinos = ArduinosRepository()
        self.environments_repo = EnvironmentsRepository()
        self.auth_service = AuthService()

    def get_all_plant_types(self, environment_id: str, user_id: str):
        allowed = False

        if(self.auth_service.check_user_permissions(user_id, environment_id)):
            allowed = True
            return self.repository.get_plant_types_by_environment(environment_id)

        if not allowed:
            raise ValueError(
                "User does not have permission to view plant types in this environment"
            )

        plant_type_response = self.repository.get_plant_types_by_environment(
            environment_id
        )

        if not plant_type_response:
            raise ValueError(
                f"No plant types found for environment ID: {environment_id}"
            )

        return plant_type_response

    def add_plant_type(self, plant_type: dict):
        # Validate required fields
        if not plant_type.get("name") or not plant_type.get("environment_id"):
            raise ValueError(
                "Invalid plant type data: 'plant_type_name' and 'plant_env_id' are required"
            )

        if plant_type.get("water_dosage") <= 0:
            raise ValueError("Water dosage must be greater than 0")

        if plant_type.get("watering_frequency") <= 0:
            raise ValueError("Watering frequency must be greater than 0")

        # Check if the environment exists
        environment = self.repository.get_environment_by_id(
            plant_type["environment_id"]
        )
        if not environment:
            raise ValueError(
                f"Environment ID {plant_type['environment_id']} does not exist"
            )

        # Insert the plant type into the database
        return self.repository.post_plant_type(plant_type)
