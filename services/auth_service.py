from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
from repositories.auth_repository import AuthRepository


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "secret-key"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthService:
    def __init__(self):
        self.auth_repository = AuthRepository()

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)

    def authenticate_user(self, username: str, password: str):
        user = self.auth_repository.find_user_by_username(username)
        if not user:
            return False
        if not self.verify_password(password, user["password"]):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(datetime.timezone.utc) + expires_delta
        else:
            expire = datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": int(expire.timestamp())})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return {
            "access_token": encoded_jwt,
            "expires_in": int(expires_delta.total_seconds()) if expires_delta else ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "bearer"
        }

    def create_user(self, username, password, email=None):
        existing_user = self.auth_repository.find_user_by_username(username)
        if existing_user:
            return None

        hashed_password = self.get_password_hash(password)
        user_data = {
            "username": username,
            "password": hashed_password
        }

        if email:
            user_data["email"] = email

        user_id = self.auth_repository.create_user(user_data)
        return user_id