# This file marks the endpoints directory as a Python package.
from fastapi import APIRouter

# Create empty router collection
__all__ = ["router"]

# Initialize router placeholder
router = APIRouter()

# Import prediction controller explicitly
try:
    from api.controllers.soil_humidity_prediction import router as prediction_router

    # Include all routes from the prediction router
    router.include_router(prediction_router)
except ImportError:
    # If import fails, log but continue
    import logging

    logging.getLogger(__name__).warning(
        "Failed to import soil_humidity_prediction router"
    )
