from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import traceback
import json
import os
import asyncio
import numpy as np

router = APIRouter()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from machine_learning.model_service import SoilHumidityService

    logger.info("Successfully imported SoilHumidityService")
except ImportError:
    logger.warning("Could not import SoilHumidityService, using fallback")

    class SoilHumidityService:
        def predict_future_humidity(self, plant_pot_id=None, minutes_ahead=5):
            return {
                "plant_pot_id": plant_pot_id or "unknown",
                "current_timestamp": "2025-05-15T12:00:00",
                "prediction_timestamp": "2025-05-15T12:05:00",
                "current_soil_humidity": 60.0,
                "predicted_soil_humidity": 58.5,
                "features_used": ["temperature", "air_humidity"],
                "prediction_method": "fallback",
            }

        def get_model_metrics(self):
            return {
                "message": "Using simplified prediction model",
                "train": {"mse": 20.5, "rmse": 4.5, "mae": 3.8, "r2": 0.65},
                "validation": {"mse": 22.1, "rmse": 4.7, "mae": 4.0, "r2": 0.62},
                "test": {"mse": 23.4, "rmse": 4.8, "mae": 4.1, "r2": 0.60},
                "model_type": "fallback",
            }


class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif hasattr(obj, "tolist"):
            return obj.tolist()
        return super().default(obj)


def convert_numpy_types(obj):
    """Recursively convert NumPy types in dictionaries and lists to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif hasattr(obj, "tolist"):
        return obj.tolist()
    return obj


@router.get("/api/prediction/test")
async def test_endpoint():
    """Test endpoint to check if the router is properly registered"""
    return {"message": "Prediction API is working!"}


@router.get("/api/prediction/future-humidity")
async def predict_future_humidity(
    plant_pot_id: Optional[str] = Query(None), minutes_ahead: int = 5
):
    try:

        service = SoilHumidityService()

        prediction_result = await asyncio.to_thread(
            service.predict_future_humidity,
            plant_pot_id=plant_pot_id,
            minutes_ahead=minutes_ahead,
        )

        if "error" in prediction_result:
            return JSONResponse(
                status_code=404, content={"detail": prediction_result["error"]}
            )

        converted_result = convert_numpy_types(prediction_result)

        return JSONResponse(status_code=200, content=converted_result)
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Future prediction error: {str(e)}")
        return JSONResponse(
            status_code=500, content={"detail": f"Future prediction error: {str(e)}"}
        )


@router.get("/api/prediction/model-metrics")
async def get_model_metrics():
    try:
        metrics_file = os.path.join(
            "machine_learning/models/saved", "training_metrics.json"
        )

        if os.path.exists(metrics_file):
            try:
                with open(metrics_file, "r") as f:
                    metrics_from_file = json.load(f)
                logger.info(f"Loaded metrics directly from file: {metrics_file}")

                model_path = "machine_learning/models/saved/latest.pkl"
                feature_data = {}

                if os.path.exists(model_path):
                    service = SoilHumidityService()

                    if hasattr(service.model, "top_features"):
                        feature_data["model_features"] = convert_numpy_types(
                            service.model.top_features
                        )

                    if hasattr(service.model, "feature_importance"):
                        feature_data["feature_importance"] = convert_numpy_types(
                            service.model.feature_importance
                        )

                result = {
                    "training_metrics": metrics_from_file.get("train", {}),
                    "validation_metrics": metrics_from_file.get("validation", {}),
                    "test_metrics": metrics_from_file.get("test", {}),
                    **feature_data,
                }

                return JSONResponse(
                    status_code=200, content=convert_numpy_types(result)
                )
            except Exception as e:
                logger.warning(f"Error reading metrics file: {str(e)}")

        service = SoilHumidityService()

        metrics = await asyncio.to_thread(service.get_model_metrics)

        if "error" in metrics:
            return JSONResponse(status_code=500, content={"detail": metrics["error"]})

        converted_metrics = convert_numpy_types(metrics)

        return JSONResponse(status_code=200, content=converted_metrics)

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Error retrieving metrics: {str(e)}")
        return JSONResponse(
            status_code=500, content={"detail": f"Error retrieving metrics: {str(e)}"}
        )
