from repositories.users_repository import UsersRepository

class UsersService:
    def __init__(self):
        self.repository = UsersRepository()

    def get_all_users(self):
        users_response = self.repository.get_all_users()
        
        if not users_response:
            raise ValueError("No users found")
        
        return users_response
    
    def add_permission(self, environment_id: str, user: dict):
        if not user.get("user_email"):
            raise ValueError("Invalid user data: 'user_email' is required")

        return self.repository.add_permission(environment_id, user)
    
    def get_user(self, user_id: str):
        if not user_id:
            raise ValueError("Invalid user ID: 'user_id' is required")
        
        user = self.repository.get_user(user_id)
        
        if not user:
            raise ValueError("User not found")
        
        return user