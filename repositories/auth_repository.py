from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId


class AuthRepository:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URI)
            server_info = self.client.server_info()

            self.db = self.client[DB_NAME]
            self.collection = self.db["users"]
        except Exception as e:
            print(f"MongoDB connection error: {str(e)}")
            raise

    def find_user_by_email(self, email: str):
        try:
            print(f"Checking if email exists: '{email}'")
            all_users = list(self.collection.find({}, {"email": 1}))
            print(f"All users in database: {all_users}")

            user = self.collection.find_one({"email": email})
            print(f"User found: {user}")
            return user
        except Exception as e:
            print(f"Error checking email: {str(e)}")
            return None

    def find_user_by_id(self, user_id: str):
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print(f"Error fetching user by ID: {str(e)}")
            return None

    def create_user(self, user_data: dict):
        try:
            result = self.collection.insert_one(user_data)
            return str(result.inserted_id)
        except Exception as e:
            import traceback

            print(f"Error inserting user: {str(e)}")
            print(traceback.format_exc())
            return None

    def update_user_password(self, user_id: str, new_password: str):
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password": new_password}},
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating password for user {user_id}: {str(e)}")
            return False
