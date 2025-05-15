from repositories.environments_repository import EnvironmentsRepository


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
    
    def delete_environment(self, environment_id: str):
        return self.environments_repository.delete_environment(environment_id)
