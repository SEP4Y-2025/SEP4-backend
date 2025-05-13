from repositories.users_repository import UsersRepository
from services.environments_service import EnvironmentsService

class UsersService:
    def __init__(self):
        self.repository = UsersRepository()
        self.env_service = EnvironmentsService()

    def get_all_users(self):
        users_response = self.repository.get_all_users()
        
        if not users_response:
            raise ValueError("No users found")
        
        return users_response
    
    def add_permission(self, environment_id: str, user: dict):
        if not user.get("user_email"):
            raise ValueError("Invalid user data: 'user_email' is required")

        return self.repository.add_permission(environment_id, user)
   
    def get_user_environments(self, user_id: str):
        env_ids = self.repository.get_user_environment_ids(user_id)

        if not env_ids:
            return []

        environments = []

        for env_id in env_ids:
            try:
                env = self.env_service.get_environment_by_id(str(env_id))
                if env:
                    environments.append(env)
            except Exception as e:
                print(f"Failed to fetch environment {env_id}: {e}")
                continue

        return environments
    def get_user(self, user_id: str):
        if not user_id:
            raise ValueError("Invalid user ID: 'user_id' is required")
        
        user = self.repository.get_user(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        return user
