# core/seed_arduinos.py
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

client = MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
db = client["sep_database"]