from pymongo import MongoClient
import os
from bson import ObjectId
from datetime import datetime
from utils.password_hash import hash_password

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["sep_database"]
collection = db["arduinos"]
collectionEnv = db["environments"]
collectionPlantTypes = db["plant_types"]
collectionUsers = db["users"]

# Initial Arduino data
initial_arduinos = [
    {"_id": "pot_1", "active": False},
    {"_id": "pot_2", "active": False},
    {"_id": "pot_3", "active": False},
    {"_id": "pot_4", "active": False},
    {"_id": "pot_5", "active": False},
    {"_id": "pot_6", "active": False}#,
    #{"_id": "662ebf49c7b9e2a7681e4a54", "active": False}, #Isn't this a user?
]

# Initial environment data
initial_envs = [
    {
        "_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Greenhouse #1",
        "owner_id": ObjectId("662ebf49c7b9e2a7681e4a53"),
        "window_state": "closed",
        "access_control": [],
        "plant_pots": [
            {
                "pot_id": "pot_2",
                "label": "pot2",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
                "state": {
                    "air_humidity": 30,
                    "temperature": 20,
                    "soil_humidity": 20,
                    "light_intensity": 50,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
            {
                "pot_id": "pot_3",
                "label": "pot3",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
                "state": {
                    "air_humidity": 10,
                    "temperature": 22,
                    "soil_humidity": 30,
                    "light_intensity": 40,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
            {
                "pot_id": "pot_4",
                "label": "pot4",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
                "state": {
                    "air_humidity": 20,
                    "temperature": 17,
                    "soil_humidity": 10,
                    "light_intensity": 10,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
        ],
    },
        {
        "_id": ObjectId("680f8359688cb5341f9f9c20"),
        "name": "Greenhouse #2",
        "owner_id": ObjectId("662ebf49c7b9e2a7681e4a54"),
        "window_state": "open",
        "access_control": [],
        "plant_pots": [
            {
                "pot_id": "pot_5",
                "label": "pot5",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a60"),
                "state": {
                    "air_humidity": 30,
                    "temperature": 20,
                    "soil_humidity": 20,
                    "light_intensity": 50,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
            {
                "pot_id": "pot_6",
                "label": "pot6",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a61"),
                "state": {
                    "air_humidity": 10,
                    "temperature": 22,
                    "soil_humidity": 30,
                    "light_intensity": 40,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
            {
                "pot_id": "pot_7",
                "label": "pot7",
                "plant_type_id": ObjectId("662ebf49c7b9e2a7681e4a61"),
                "state": {
                    "air_humidity": 28,
                    "temperature": 21,
                    "soil_humidity": 31,
                    "light_intensity": 10,
                    "water_level": 750,
                    "water_tank_capacity": 1000,
                    "measured_at": datetime(2025, 4, 29, 12, 0, 0),
                },
            },
        ],
    }
]

# Initial plant types
plant_types = [
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "name": "Rose",
        "watering_frequency": 2,
        "water_dosage": 50,
        "environment_id": ObjectId("680f8359688cb5341f9f9c19"),
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
        "name": "Tulip",
        "watering_frequency": 3,
        "water_dosage": 40,
        "environment_id": ObjectId("680f8359688cb5341f9f9c19"),
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a59"),
        "name": "Sunflower",
        "watering_frequency": 1,
        "water_dosage": 60,
        "environment_id": ObjectId("680f8359688cb5341f9f9c19"),
    },
        {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a60"),
        "name": "Mint",
        "watering_frequency": 5,
        "water_dosage": 60,
        "environment_id": ObjectId("680f8359688cb5341f9f9c20"),
    },
            {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a61"),
        "name": "Daisy",
        "watering_frequency": 4,
        "water_dosage": 80,
        "environment_id": ObjectId("680f8359688cb5341f9f9c20"),
    },
]

users = [
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a53"),
        "username": "Allan",
        "password": hash_password("password1"),
        "email": "email1@domain.com",
        "environments": [
            {"environment_id": ObjectId("680f8359688cb5341f9f9c19"), "role": "Owner"}
        ],
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a54"),
        "username": "Bob",
        "password": hash_password("password2"),
        "email": "email2@domain.com",
        "environments": [{"environment_id": ObjectId("680f8359688cb5341f9f9c20"), "role": "Owner"}],
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "username": "Charlie",
        "password": hash_password("password3"),
        "email": "email3@domain.com",
        "environments": [],
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

# Insert users
for user in users:
    try:
        collectionUsers.insert_one(user)
        print(f"Inserted: {user['_id']}")
    except Exception as e:
        print(f"Skipping {user['_id']}: {e}")

