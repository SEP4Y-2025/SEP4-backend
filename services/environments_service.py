from repositories.environments_repository import EnvironmentsRepository

class EnvironmentsService:
    def __init__(self):
        self.environments_repository = EnvironmentsRepository()

    def get_environments(self):
        result = self.environments_repository.get_environments()
        print(f"Environments service returned {len(result) if result else 0} environments")
        return result