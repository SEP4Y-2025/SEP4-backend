from pymongo import MongoClient
import os
from bson import ObjectId
from datetime import datetime

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["sep_database"]
collection = db["arduinos"]
collectionEnv = db["environments"]
collectionPlantTypes = db["plant_types"]

# Initial Arduino data
initial_arduinos = [
    {"_id": "pot_1", "active": False},
    {"_id": "pot_2", "active": False},
    {"_id": "pot_3", "active": False},
    {"_id": "pot_4", "active": False},
    {"_id": "pot_5", "active": False},
    {"_id": "pot_6", "active": False},
]

# Initial environment data
initial_envs = [
    {
        "_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Greenhouse #1",
        "ownerId": ObjectId("662ebf49c7b9e2a7681e4a53"),
        "windowState": "closed",
        "temperature": 20,
        "accessControl": [{"userId": ObjectId("662ebf49c7b9e2a7681e4a53")}],
        "plantPots": [
            {
                "potId": ObjectId("662ebf49c7b9e2a7681e4a54"),
                "name": "pot1",
                "state": {
                    "airHumidity": [datetime(2025, 4, 29, 12, 0, 0), 30],
                    "temperature": [datetime(2025, 4, 29, 12, 0, 0), 20],
                    "soilHumidity": [datetime(2025, 4, 29, 12, 0, 0), 20],
                },
                "plantTypeId": ObjectId("662ebf49c7b9e2a7681e4a55"),
                "waterTank": {
                    "capacityMl": 1000,
                    "currentLevelMl": 750,
                    "status": "active",
                },
            },
            {
                "potId": ObjectId("662ebf49c7b9e2a7681e4a56"),
                "name": "pot2",
                "state": {
                    "airHumidity": [datetime(2025, 4, 29, 12, 0, 0), 30],
                    "temperature": [datetime(2025, 4, 29, 12, 0, 0), 20],
                    "soilHumidity": [datetime(2025, 4, 29, 12, 0, 0), 24],
                },
                "plantTypeId": ObjectId("662ebf49c7b9e2a7681e4a55"),
                "waterTank": {
                    "capacityMl": 1000,
                    "currentLevelMl": 500,
                    "status": "active",
                },
            },
            {
                "potId": ObjectId("662ebf49c7b9e2a7681e4a57"),
                "name": "pot3",
                "state": {
                    "airHumidity": [datetime(2025, 4, 29, 12, 0, 0), 30],
                    "temperature": [datetime(2025, 4, 29, 12, 0, 0), 20],
                    "soilHumidity": [datetime(2025, 4, 29, 12, 0, 0), 18],
                },
                "plantTypeId": ObjectId("662ebf49c7b9e2a7681e4a58"),
                "waterTank": {
                    "capacityMl": 1000,
                    "currentLevelMl": 900,
                    "status": "active",
                },
            },
        ],
    }
]

# Initial plant types
plant_types = [
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Rose",
        "water_dosage": 50,
        "water_frequency": 2,
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Tulip",
        "water_dosage": 40,
        "water_frequency": 3,
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a59"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Sunflower",
        "water_dosage": 60,
        "water_frequency": 1,
    },
]

# Insert plant types
for pt in plant_types:
    try:
        collectionPlantTypes.insert_one(pt)
        print(f"Inserted plant type: {pt['name']}")
    except Exception as e:
        print(f"Skipping {pt['name']}: {e}")

# Insert arduinos
for pot in initial_arduinos:
    try:
        collection.insert_one(pot)
        print(f"Inserted: {pot['_id']}")
    except Exception as e:
        print(f"Skipping {pot['_id']}: {e}")

# Insert environments
for env in initial_envs:
    try:
        collectionEnv.insert_one(env)
        print(f"Inserted: {env['_id']}")
    except Exception as e:
        print(f"Skipping {env['_id']}: {e}")
