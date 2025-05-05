# core/seed_arduinos.py
from pymongo import MongoClient
import os
from bson import ObjectId

client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["sep_database"]
collection = db["arduinos"]
collectionEnv = db["environments"]
collectionPlantTypes = db["plant_types"]

initial_arduinos = [
    {"_id": "pot_1", "active": False},
    {"_id": "pot_2", "active": False},
    {"_id": "pot_3", "active": False},
    {"_id": "pot_4", "active": False},
    {"_id": "pot_5", "active": False},
    {"_id": "pot_6", "active": False}
]

initial_envs = [
        {
  "_id": {
    "$oid": "680f8359688cb5341f9f9c19"
  },
  "name": "Greenhouse #1",
  "ownerId": {
    "$oid": "662ebf49c7b9e2a7681e4a53"
  },
  "windowState": "closed",
  "temperature": 20,
  "accessControl": [
    {
      "userId": {
        "$oid": "662ebf49c7b9e2a7681e4a53"
      }
    }
  ],
  "plantPots": [
    {
      "potId": {
        "$oid": "662ebf49c7b9e2a7681e4a54"
      },
      "name": "pot1",
      "state": {
        "airHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          30
        ],
        "temperature": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          20
        ],
        "soilHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          20
        ]
      },
      "plantTypeId": {
        "$oid": "662ebf49c7b9e2a7681e4a55"
      },
      "waterTank": {
        "capacityMl": 1000,
        "currentLevelMl": 750,
        "status": "active"
      }
    },
    {
      "potId": {
        "$oid": "662ebf49c7b9e2a7681e4a56"
      },
      "name": "pot2",
      "state": {
        "airHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          30
        ],
        "temperature": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          20
        ],
        "soilHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          24
        ]
      },
      "plantTypeId": {
        "$oid": "662ebf49c7b9e2a7681e4a55"
      },
      "waterTank": {
        "capacityMl": 1000,
        "currentLevelMl": 500,
        "status": "active"
      }
    },
    {
      "potId": {
        "$oid": "662ebf49c7b9e2a7681e4a57"
      },
      "name": "pot3",
      "state": {
        "airHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          30
        ],
        "temperature": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          20
        ],
        "soilHumidity": [
          {
            "$date": "2025-04-29T12:00:00.000Z"
          },
          18
        ]
      },
      "plantTypeId": {
        "$oid": "662ebf49c7b9e2a7681e4a58"
      },
      "waterTank": {
        "capacityMl": 1000,
        "currentLevelMl": 900,
        "status": "active"
      }
    }
  ]
}
]

plant_types = [
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a55"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Rose",
        "water_dosage": 50,  # in ml
        "water_frequency": 2  # in days
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a58"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Tulip",
        "water_dosage": 40,
        "water_frequency": 3
    },
    {
        "_id": ObjectId("662ebf49c7b9e2a7681e4a59"),
        "plant_env_id": ObjectId("680f8359688cb5341f9f9c19"),
        "name": "Sunflower",
        "water_dosage": 60,
        "water_frequency": 1
    }
]

for pt in plant_types:
    try:
        collectionPlantTypes.insert_one(pt)
        print(f"Inserted plant type: {pt['name']}")
    except Exception as e:
        print(f"Skipping {pt['name']}: {e}")

for pot in initial_arduinos:
    try:
        collection.insert_one(pot)
        print(f"Inserted: {pot['_id']}")
    except Exception as e:
        print(f"Skipping {pot['_id']}: {e}")

for env in initial_envs:
    try:
        collectionEnv.insert_one(env)
        print(f"Inserted: {env['_id']}")
    except Exception as e:
        print(f"Skipping {env['_id']}: {e}")
