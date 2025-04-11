# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.mqtt_client import mqtt_client
from api.controllers.plant_pots_controller import router as pots_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to the actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.include_router(pots_router)

#mqtt_client.start()




