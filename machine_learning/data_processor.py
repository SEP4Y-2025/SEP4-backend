import pandas as pd
import numpy as np
from datetime import datetime
from repositories.plant_data_repository import PlantDataRepository
import logging
import traceback

logger = logging.getLogger(__name__)


class DataProcessor:
    def __init__(self):
        self.plant_data_repository = PlantDataRepository()

    def load_data(self):
        try:
            data = self.plant_data_repository.get_all_data()
            df = pd.DataFrame(data)

            if df.empty:
                logger.warning("No data available in the database")
                return pd.DataFrame()

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            return df
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()

    def extract_time_features(self, data):
        try:
            if data.empty:
                return data

            data["hour"] = data["timestamp"].dt.hour
            data["hour_sin"] = np.sin(data["hour"] * (2 * np.pi / 24))
            data["hour_cos"] = np.cos(data["hour"] * (2 * np.pi / 24))

            conditions = [
                (data["hour"] >= 6) & (data["hour"] < 12),
                (data["hour"] >= 12) & (data["hour"] < 18),
                (data["hour"] >= 18) & (data["hour"] < 22),
                (data["hour"] >= 22) | (data["hour"] < 6),
            ]
            categories = ["morning", "afternoon", "evening", "night"]
            data["day_part"] = np.select(conditions, categories, default="unknown")

            day_part_dummies = pd.get_dummies(data["day_part"], prefix="day_part")
            data = pd.concat([data, day_part_dummies], axis=1)

            return data
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error extracting time features: {str(e)}")
            return data

    def prepare_features_and_target(self, data):
        try:
            if data.empty or "soil_humidity" not in data.columns:
                return pd.DataFrame(), pd.Series()

            features = [
                "temperature",
                "air_humidity",
                "light_intensity",
                "hour_sin",
                "hour_cos",
                "day_part_morning",
                "day_part_afternoon",
                "day_part_evening",
                "day_part_night",
            ]

            for feature in features:
                if feature not in data.columns:
                    data[feature] = 0

            X = data[features]
            y = data["soil_humidity"]

            return X, y
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error preparing features: {str(e)}")
            return pd.DataFrame(), pd.Series()

    def process_data(self):
        try:
            data = self.load_data()

            if data.empty:
                return pd.DataFrame(), pd.DataFrame(), pd.Series()

            data = self.extract_time_features(data)
            X, y = self.prepare_features_and_target(data)

            return data, X, y
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error processing data: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.Series()

    def get_latest_data_for_prediction(self, pot_id=None):
        try:
            data = self.plant_data_repository.get_latest_data(pot_id)

            if not data:
                return None

            df = pd.DataFrame(data)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])

            df = self.extract_time_features(df)

            return df
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error getting latest data: {str(e)}")
            return None
