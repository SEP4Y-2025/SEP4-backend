from datetime import datetime, timezone, timedelta
import traceback
from typing import Optional
import jwt
from passlib.context import CryptContext
from repositories.auth_repository import AuthRepository
from repositories.users_repository import UsersRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "secret-key"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.users_repository = UsersRepository()

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def authenticate_user(self, email: str, password: str):
        user = self.auth_repository.find_user_by_email(email)
        if not user:
            return False
        if not self.verify_password(password, user["password"]):
            return False
        return user

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({"exp": int(expire.timestamp())})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": encoded_jwt,
            "expires_in": (
                int(expires_delta.total_seconds())
                if expires_delta
                else ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ),
            "token_type": "bearer",
        }

    def create_user(self, username, password, email=None):
        try:
            existing_user = self.auth_repository.find_user_by_email(email)
            if existing_user:
                print(f"User {email} already exists")
                return None

            print(f"Hashing password for user {username}")
            hashed_password = self.get_password_hash(password)
            user_data = {"username": username, "password": hashed_password}

            if email:
                user_data["email"] = email

            print(f"Calling repository to create user {username}")
            user_id = self.auth_repository.create_user(user_data)
            create_access_token = self.create_access_token(
                data={"sub": username, "email": email, "id": str(user_id)}
            )
            print(f"User created with ID: {user_id}")
            return user_id
        except Exception as e:

            print(traceback.format_exc())
            return None

    def change_password(self, user_id: str, old_password: str, new_password: str):
        user = self.auth_repository.find_user_by_id(user_id)
        if not user:
            return False
        if not self.verify_password(old_password, user["password"]):
            return False
        new_hashed = self.get_password_hash(new_password)
        return self.auth_repository.update_user_password(user_id, new_hashed)

    def check_user_permissions(self, user_id: str, environment_id: str):
        role = self.users_repository.get_user_role(user_id, environment_id)
        if role == "Owner" or role == "Plant Assistant":
            return True
        return False
