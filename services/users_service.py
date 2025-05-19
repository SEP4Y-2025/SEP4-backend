from repositories.users_repository import UsersRepository
from services.environments_service import EnvironmentsService
from services.auth_service import AuthService


class UsersService:
    def __init__(self):
        self.repository = UsersRepository()
        self.env_service = EnvironmentsService()
        self.auth_service = AuthService()

    def get_all_users(self):
        users_response = self.repository.get_all_users()

        if not users_response:
            raise ValueError("No users found")

        return users_response

    def add_permission(self, environment_id: str, user: dict, request_user_id: str):
        if not user.get("user_email"):
            raise ValueError("Invalid user data: 'user_email' is required")
        if (self.auth_service.check_user_permissions(request_user_id, environment_id)== True):
            return self.repository.add_permission(environment_id, user)
        else:
            raise ValueError("User does not have permission to add user")

    def get_user_environments(self, user_id: str):
        return self.repository.get_user_environment_ids(user_id)

    def get_user(self, user_id: str):
        if not user_id:
            raise ValueError("Invalid user ID: 'user_id' is required")

        user = self.repository.get_user(user_id)

        if not user:
            raise ValueError("User not found")

        return user

    def delete_permission(self, environment_id: str, user: dict):
        if not user.get("user_email"):
            raise ValueError(
                "Invalid input: 'environment_id' and 'user_id' are required"
            )
        return self.repository.delete_permission(environment_id, user)

    def get_user_permissions(self, environment_id: str):
        if not environment_id:
            raise ValueError("Invalid input: 'environment_id' is required")

        return self.repository.get_user_permissions(environment_id)
