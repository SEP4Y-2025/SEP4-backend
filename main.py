from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import logging

# Import routers
from api.controllers.plant_pots_controller import router as pots_router
from api.controllers.plant_types_controller import router as plant_types_router
from api.controllers.users_controller import router as user_router
from api.controllers.environments_controller import router as environments_router
from api.controllers.auth_controller import router as auth_router
from api.controllers.soil_humidity_prediction import router as prediction_router
from core.mqtt_client import mqtt_client
from machine_learning.model_initializer import init_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize model in background
    logger.info("Starting up the application")
    try:
        # Initialize ML model in background thread to avoid blocking
        threading.Thread(target=init_model, daemon=True).start()
        logger.info("Machine learning model initialization started in background")
    except Exception as e:
        logger.error(f"Error initializing ML model: {str(e)}")

    yield  # App runs here

    # Shutdown: cleanup if needed
    logger.info("Shutting down the application")


# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - include prediction_router FIRST for priority
app.include_router(prediction_router)
app.include_router(pots_router)
app.include_router(plant_types_router)
app.include_router(user_router)
app.include_router(environments_router)
app.include_router(auth_router)
# mqtt_client.start()


@app.get("/")
async def root():
    return {"message": "Smart Plant Monitoring System API"}
