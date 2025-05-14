from pymongo import MongoClient
from core.config import MONGO_URI, DB_NAME
from bson import ObjectId


class AuthRepository:
    def __init__(self):
        try:
            print(f"Connecting to MongoDB at {MONGO_URI}")
            self.client = MongoClient(MONGO_URI)
            # Test connection
            server_info = self.client.server_info()
            print(
                f"Connected to MongoDB version: {server_info.get('version', 'unknown')}"
            )

            self.db = self.client[DB_NAME]
            print(f"Using database: {DB_NAME}")
            self.collection = self.db["users"]
            print(f"Collection names in database: {self.db.list_collection_names()}")
        except Exception as e:
            print(f"MongoDB connection error: {str(e)}")
            raise

    def find_user_by_username(self, username: str):
        try:
            print(f"Checking if username exists: '{username}'")
            # Add a debug query to see what's in the database
            all_users = list(self.collection.find({}, {"username": 1}))
            print(f"All users in database: {all_users}")

            # Perform the actual query
            user = self.collection.find_one({"username": username})
            print(f"User found: {user}")
            return user
        except Exception as e:
            print(f"Error checking username: {str(e)}")
            # Return None on error instead of a possible exception
            return None

    def find_user_by_id(self, user_id: str):
        try:
            return self.collection.find_one({"_id": ObjectId(user_id)})
        except:
            print(f"Error finding user by ID: {user_id}")
            return None

    def create_user(self, user_data: dict):
        try:
            print(f"Attempting to insert user: {user_data.get('username')}")
            result = self.collection.insert_one(user_data)
            print(f"User inserted with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            import traceback

            print(f"Error inserting user: {str(e)}")
            print(traceback.format_exc())
            return None

    def update_user_password(self, username, new_password: str):
        try:
            result = self.collection.update_one(
                {"username": username}, {"$set": {"password": new_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating password for user {username}: {str(e)}")
            return False
