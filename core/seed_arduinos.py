# core/seed_arduinos.py
from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["sep_database"]
collection = db["arduinos"]

initial_arduinos = [
    {"_id": "pot_1", "active": False},
    {"_id": "pot_2", "active": False},
    {"_id": "pot_3", "active": False},
    {"_id": "pot_4", "active": False},
    {"_id": "pot_5", "active": False},
    {"_id": "pot_6", "active": False}
]

for pot in initial_arduinos:
    try:
        collection.insert_one(pot)
        print(f"Inserted: {pot['_id']}")
    except Exception as e:
        print(f"Skipping {pot['_id']}: {e}")