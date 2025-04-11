# import os
# from dotenv import load_dotenv

# load_dotenv()

# class Config:
#     ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
#     DEBUG = os.getenv("DEBUG", "True") == "True"
#     DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
#     MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "mqtt://localhost")
#     MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
#     LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# core/config.py
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URL", "mongodb://mongo:27017")
DB_NAME = "sep_database"
MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "mqtt://mqtt:1883")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
