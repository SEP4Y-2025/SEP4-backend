from machine_learning.soil_predictor import SoilHumidityPredictor
from machine_learning.data_processor import DataProcessor
import pandas as pd
import numpy as np
from datetime import timedelta, datetime
import os
import logging
import traceback
import json
import time

logger = logging.getLogger(__name__)


class SoilHumidityService:
    """
    Service for predicting future soil humidity based on historical data and ML models
    """

    def __init__(
        self, model_path="machine_learning/models/saved/latest.pkl", collection=None
    ):
        self.model_path = model_path
        self.model = None
        self.collection = collection
        self.data_processor = DataProcessor()
        self.default_features = ["temperature", "air_humidity"]
        try:
            self.load_model()
        except Exception as e:
            logger.warning(
                f"Model file not found at {self.model_path}, using default features: {str(e)}"
            )
            self.model = SoilHumidityPredictor()
            self.model.top_features = self.default_features

    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = SoilHumidityPredictor.load(self.model_path)
        else:
            logger.warning(
                f"Model file not found at {self.model_path}, using default features."
            )
            self.model = SoilHumidityPredictor()
            self.model.top_features = self.default_features

    def preprocess_input(self, input_data):
        try:
            if isinstance(input_data, dict):
                input_data = pd.DataFrame([input_data])

            if "timestamp" in input_data.columns:
                input_data["timestamp"] = pd.to_datetime(input_data["timestamp"])

                input_data["hour"] = input_data["timestamp"].dt.hour

                input_data["hour_sin"] = np.sin(input_data["hour"] * (2 * np.pi / 24))
                input_data["hour_cos"] = np.cos(input_data["hour"] * (2 * np.pi / 24))

                conditions = [
                    (input_data["hour"] >= 6) & (input_data["hour"] < 12),
                    (input_data["hour"] >= 12) & (input_data["hour"] < 18),
                    (input_data["hour"] >= 18) & (input_data["hour"] < 22),
                    (input_data["hour"] >= 22) | (input_data["hour"] < 6),
                ]
                categories = ["morning", "afternoon", "evening", "night"]
                input_data["day_part"] = np.select(
                    conditions, categories, default="unknown"
                )

                day_part_dummies = pd.get_dummies(
                    input_data["day_part"], prefix="day_part"
                )
                input_data = pd.concat([input_data, day_part_dummies], axis=1)

            return input_data
        except Exception as e:
            logger.error(f"Error preprocessing input: {str(e)}")
            traceback.print_exc()
            raise

    def predict(self, input_data):
        if self.model is None:
            self.load_model()

        processed_input = self.preprocess_input(input_data)

        for feature in self.model.top_features:
            if feature not in processed_input.columns:
                logger.warning(f"Feature {feature} not found in input, setting to 0")
                processed_input[feature] = 0

        X_selected = processed_input[self.model.top_features]

        prediction = self.model.predict(X_selected)

        current_humidity = None
        if "soil_humidity" in input_data.columns:
            current_humidity = input_data["soil_humidity"].iloc[0]

            if current_humidity is not None and prediction[0] > current_humidity:
                minutes_ahead = 5

                if "minutes_ahead" in input_data.columns:
                    minutes_ahead = input_data["minutes_ahead"].iloc[0]

                natural_drying_rate = 0.005
                expected_humidity = max(
                    0, current_humidity - (natural_drying_rate * minutes_ahead)
                )

                if prediction[0] > current_humidity and minutes_ahead > 0:
                    logger.warning(
                        f"Prediction ({prediction[0]}) higher than current humidity ({current_humidity}) after {minutes_ahead} mins - adjusting to expected {expected_humidity}"
                    )
                    prediction[0] = expected_humidity

        if len(prediction) == 1 and prediction[0] > 100:
            logger.warning(
                f"Unrealistic prediction value: {prediction[0]}, capping at 100"
            )
            return np.array([100.0])

        return prediction[0] if len(prediction) == 1 else prediction

    def predict_future_humidity(self, plant_pot_id=None, minutes_ahead=5):
        try:
            logger.info(
                f"Predicting future humidity for pot: {plant_pot_id}, minutes ahead: {minutes_ahead}"
            )

            latest_data = self.data_processor.get_latest_data_for_prediction(
                plant_pot_id
            )

            if latest_data is None or latest_data.empty:
                logger.warning(
                    f"No data found for plant_pot_id={plant_pot_id}, using fallback data"
                )
                fallback_data = {
                    "plant_pot_id": plant_pot_id or "unknown",
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "temperature": 25.0,
                    "air_humidity": 50.0,
                    "soil_humidity": 30.0,
                    "light_intensity": 500,
                }
                latest_data = pd.DataFrame([fallback_data])
                latest_data["timestamp"] = pd.to_datetime(latest_data["timestamp"])

            logger.info(f"Latest data found: {len(latest_data)} records")

            if (
                "temperature" in latest_data.columns
                and "air_humidity" in latest_data.columns
                and "soil_humidity" in latest_data.columns
            ):
                logger.info(
                    f"Current conditions - Temp: {latest_data['temperature'].iloc[0]}, Air Humidity: {latest_data['air_humidity'].iloc[0]}, Soil Humidity: {latest_data['soil_humidity'].iloc[0]}"
                )

            future_data = latest_data.copy()

            current_timestamp = future_data["timestamp"].iloc[0]
            current_soil_humidity = (
                float(latest_data["soil_humidity"].iloc[0])
                if "soil_humidity" in latest_data.columns
                else None
            )

            future_timestamp = current_timestamp + timedelta(minutes=minutes_ahead)
            future_data["timestamp"] = future_timestamp

            future_data["minutes_ahead"] = minutes_ahead

            future_data = self.data_processor.extract_time_features(future_data)

            time.sleep(0.1)
            predicted_humidity = self.predict(future_data)
            temp = (
                latest_data["temperature"].iloc[0]
                if "temperature" in latest_data.columns
                else 25
            )
            air_humidity = (
                latest_data["air_humidity"].iloc[0]
                if "air_humidity" in latest_data.columns
                else 50
            )

            evaporation_rate = (0.003 * temp - 0.001 * air_humidity) * minutes_ahead
            evaporation_rate = max(0.001 * minutes_ahead, evaporation_rate)

            fallback_prediction = (
                current_soil_humidity - evaporation_rate
                if current_soil_humidity
                else 30
            )
            fallback_prediction = max(0, min(fallback_prediction, 100))

            logger.info(
                f"Used ML model for prediction, features: {self.model.top_features}"
            )
            logger.info(
                f"ML prediction: {predicted_humidity}, Fallback: {fallback_prediction}"
            )

            if predicted_humidity > 100 or predicted_humidity < 0:
                logger.warning(
                    f"ML prediction out of valid range ({predicted_humidity}), using fallback value"
                )
                predicted_humidity = fallback_prediction
            physical_constraints_applied = False
            if predicted_humidity > current_soil_humidity and minutes_ahead > 0:
                logger.warning(
                    f"Prediction ({predicted_humidity}) higher than current humidity ({current_soil_humidity}) - using fallback value ({fallback_prediction})"
                )
                predicted_humidity = fallback_prediction
                physical_constraints_applied = True

            feature_importance = {}
            if hasattr(self.model, "feature_importance"):
                feature_importance = {
                    k: float(v) for k, v in self.model.feature_importance.items()
                }

            features_used = self.model.top_features

            result = {
                "plant_pot_id": (
                    str(latest_data["plant_pot_id"].iloc[0])
                    if "plant_pot_id" in latest_data.columns
                    else str(plant_pot_id or "unknown")
                ),
                "current_timestamp": current_timestamp.isoformat(),
                "prediction_timestamp": future_timestamp.isoformat(),
                "minutes_ahead": int(minutes_ahead),
                "current_soil_humidity": (
                    float(current_soil_humidity)
                    if current_soil_humidity is not None
                    else None
                ),
                "predicted_soil_humidity": float(round(float(predicted_humidity), 2)),
                "features_used": [str(f) for f in features_used],
                "feature_importance": {
                    str(k): float(v) for k, v in feature_importance.items()
                },
                "prediction_method": "machine_learning",
                "physical_constraints_applied": bool(physical_constraints_applied),
            }

            time.sleep(0.1)

            logger.info(f"Prediction result: {result}")
            return result
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error predicting future humidity: {str(e)}")
            return {"error": f"Prediction error: {str(e)}"}

    def get_model_metrics(self):
        """
        Get metrics about the current prediction model.
        """
        try:
            time.sleep(0.1)

            from machine_learning.model_trainer import ModelTrainer

            trainer = ModelTrainer()
            metrics = trainer.get_metrics()

            if metrics is None:
                metrics_file = os.path.join(
                    "machine_learning/models/saved", "training_metrics.json"
                )
                if os.path.exists(metrics_file):
                    try:
                        with open(metrics_file, "r") as f:
                            metrics = json.load(f)
                        logger.info(f"Loaded metrics from {metrics_file}")
                    except Exception as e:
                        logger.warning(f"Could not load metrics from file: {str(e)}")
                else:
                    return {
                        "message": "No metrics available. Model may not have been trained yet."
                    }

            feature_importance = {}
            if hasattr(self.model, "feature_importance"):
                feature_importance = {
                    str(k): float(v) for k, v in self.model.feature_importance.items()
                }

            time.sleep(0.1)

            train_metrics = {
                str(k): (
                    float(v)
                    if isinstance(v, (np.integer, np.floating, float, int))
                    else v
                )
                for k, v in metrics.get("train", {}).items()
            }
            validation_metrics = {
                str(k): (
                    float(v)
                    if isinstance(v, (np.integer, np.floating, float, int))
                    else v
                )
                for k, v in metrics.get("validation", {}).items()
            }
            test_metrics = {
                str(k): (
                    float(v)
                    if isinstance(v, (np.integer, np.floating, float, int))
                    else v
                )
                for k, v in metrics.get("test", {}).items()
            }

            return {
                "model_features": [
                    str(f) for f in (self.model.top_features if self.model else [])
                ],
                "feature_importance": feature_importance,
                "training_metrics": train_metrics,
                "validation_metrics": validation_metrics,
                "test_metrics": test_metrics,
            }
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error getting model metrics: {str(e)}")
            return {"error": f"Could not retrieve model metrics: {str(e)}"}
