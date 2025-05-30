from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from utils.helper import convert_object_ids
from bson import ObjectId


class UsersRepository:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.user_collection = self.db["users"]
        self.env_collection = self.db["environments"]

    def add_permission(self, environment_id: str, user: dict):
        try:
            user = self.user_collection.find_one({"email": user["user_email"]})
            if not user:
                raise ValueError("Invalid user data: 'user_email' is required")
            user_id = user["_id"]

            result = self.env_collection.update_one(
                {"_id": ObjectId(environment_id)},
                {
                    "$addToSet": {
                        "access_control": {
                            "user_id": user_id,
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            if result.modified_count == 0:
                raise ValueError(f"No environment found with ID {environment_id}")

            self.user_collection.update_one(
                {"_id": user_id},
                {
                    "$addToSet": {
                        "environments": {
                            "environment_id": ObjectId(environment_id),
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            return True
        except Exception as e:
            print(f"Error in add_permission: {e}")
            raise

    def get_user_environment_ids(self, user_id: str):
        try:
            user = self.user_collection.find_one(
                {"_id": ObjectId(user_id)},
                {"environments.environment_id": 1, "environments.role": 1},
            )
            if not user:
                raise ValueError("User not found")

            environments = user.get("environments", [])
            environment_data = []
            for env in environments:
                if "environment_id" in env and "role" in env:
                    env_doc = self.env_collection.find_one(
                        {"_id": ObjectId(env["environment_id"])}, {"name": 1}
                    )
                    env_name = (
                        env_doc["name"] if env_doc and "name" in env_doc else None
                    )
                    environment_data.append(
                        {
                            "environment_id": str(env["environment_id"]),
                            "environment_name": env_name,
                            "role": env["role"],
                        }
                    )

            return environment_data
        except Exception as e:
            print(f"Error fetching environment data: {e}")
            raise

    def get_user(self, user_id: str):
        try:
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise ValueError("User not found")

            return convert_object_ids(user)
        except Exception as e:
            print(f"Error in get_user: {e}")
            raise

    def delete_permission(self, environment_id: str, user: dict):
        if not user.get("user_email"):
            raise ValueError(
                "Invalid input: 'environment_id' and 'user_id' are required"
            )

        try:
            user = self.user_collection.find_one({"email": user["user_email"]})
            if not user:
                raise ValueError("Invalid user data: 'user_email' is required")
            user_id = user["_id"]

            result = self.env_collection.update_one(
                {"_id": ObjectId(environment_id)},
                {
                    "$pull": {
                        "access_control": {
                            "user_id": user_id,
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            if result.modified_count == 0:
                raise ValueError(f"No environment found with ID {environment_id}")

            self.user_collection.update_one(
                {"_id": user_id},
                {
                    "$pull": {
                        "environments": {
                            "environment_id": ObjectId(environment_id),
                            "role": "Plant Assistant",
                        }
                    }
                },
            )
            return True
        except Exception as e:
            print(f"Error in delete_permission: {e}")
            raise

    def get_user_permissions(self, environment_id: str):
        if not environment_id:
            raise ValueError("Invalid input: 'environment_id' is required")
        try:
            environment = self.env_collection.find_one(
                {"_id": ObjectId(environment_id)},
                {"access_control.user_id": 1, "access_control.role": 1},
            )
            if not environment:
                raise ValueError("Environment not found")

            permissions = environment.get("access_control", [])
            user_permissions = [
                {"user_id": str(perm["user_id"]), "role": perm["role"]}
                for perm in permissions
                if "user_id" in perm and "role" in perm
            ]

            return user_permissions
        except Exception as e:
            print(f"Error fetching user permissions: {e}")
            raise

    def get_user_role(self, user_id: str, environment_id: str):
        try:
            user = self.user_collection.find_one(
                {"_id": ObjectId(user_id)},
                {"environments.environment_id": 1, "environments.role": 1},
            )
            if not user:
                raise ValueError("User not found")

            environments = user.get("environments", [])
            print(f"Environments: {environments}")
            for env in environments:
                if str(env["environment_id"]) == environment_id:
                    return env["role"]

            raise ValueError("User does not have access to this environment")
        except Exception as e:
            print(f"Error in get_user_role: {e}")
            raise

    def add_environment_to_user(self, user_id: str, environment: dict):
        try:
            self.user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$addToSet": {
                        "environments": {
                            "environment_id": ObjectId(environment["environment_id"]),
                            "role": environment["role"],
                        }
                    }
                },
            )
        except Exception as e:
            print(f"Error in add_environment_to_user: {e}")
            raise

    def remove_environment_from_user(self, user_id: str, environment_id: str):
        try:
            self.user_collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$pull": {
                        "environments": {
                            "environment_id": ObjectId(environment_id),
                        }
                    }
                },
            )
        except Exception as e:
            print(f"Error in remove_environment_from_user: {e}")
            raise
