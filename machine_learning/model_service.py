from machine_learning.soil_predictor import SoilHumidityPredictor
from machine_learning.data_processor import DataProcessor
import pandas as pd
import numpy as np
from datetime import timedelta
import os
import logging

logger = logging.getLogger(__name__)

class SoilHumidityService:
    def __init__(self, model_path="machine_learning/models/saved/latest.pkl", collection="plant_data"):
        self.model_path = model_path
        self.model = None
        self.collection = collection
        self.data_processor = DataProcessor(collection)
        self.default_features = ['temperature', 'air_humidity']
        try:
            self.load_model()
        except Exception as e:
            self.model = SoilHumidityPredictor()
            self.model.top_features = self.default_features
        
    def load_model(self):
        if os.path.exists(self.model_path):
            self.model = SoilHumidityPredictor.load(self.model_path)
        else:
            self.model = SoilHumidityPredictor()
            self.model.top_features = self.default_features
    
    def preprocess_input(self, input_data):
        if isinstance(input_data, dict):
            input_data = pd.DataFrame([input_data])
            
        if 'timestamp' in input_data.columns:
            input_data['timestamp'] = pd.to_datetime(input_data['timestamp'])
            
            input_data['hour'] = input_data['timestamp'].dt.hour
            
            input_data['hour_sin'] = np.sin(input_data['hour'] * (2 * np.pi / 24))
            input_data['hour_cos'] = np.cos(input_data['hour'] * (2 * np.pi / 24))
            
            conditions = [
                (input_data['hour'] >= 6) & (input_data['hour'] < 12),
                (input_data['hour'] >= 12) & (input_data['hour'] < 18),
                (input_data['hour'] >= 18) & (input_data['hour'] < 22),
                (input_data['hour'] >= 22) | (input_data['hour'] < 6)
            ]
            categories = ['morning', 'afternoon', 'evening', 'night']
            input_data['day_part'] = np.select(conditions, categories)
            
            day_part_dummies = pd.get_dummies(input_data['day_part'], prefix='day_part')
            input_data = pd.concat([input_data, day_part_dummies], axis=1)
        
        return input_data
    
    def predict(self, input_data):
        if self.model is None:
            self.load_model()
            
        processed_input = self.preprocess_input(input_data)
        
        for feature in self.model.top_features:
            if feature not in processed_input.columns:
                processed_input[feature] = 0
        
        prediction = self.model.predict(processed_input)
        
        return prediction[0] if len(prediction) == 1 else prediction
    
    def predict_future_humidity(self, pot_id=None, minutes_ahead=5):
        try:
            latest_data = self.data_processor.get_latest_data_for_prediction(pot_id)
            
            if latest_data is None or latest_data.empty:
                return {"error": "No recent data found for the specified plant pot"}
            
            future_data = latest_data.copy()
            
            current_timestamp = future_data['timestamp'].iloc[0]
            future_timestamp = current_timestamp + timedelta(minutes=minutes_ahead)
            future_data['timestamp'] = future_timestamp
            
            future_data = self.data_processor.extract_time_features(future_data)
            
            predicted_humidity = self.predict(future_data)
            
            return {
                "plant_pot_id": latest_data['plant_pot_id'].iloc[0] if 'plant_pot_id' in latest_data.columns else "unknown",
                "current_timestamp": current_timestamp,
                "prediction_timestamp": future_timestamp,
                "current_soil_humidity": float(latest_data['soil_humidity'].iloc[0]) if 'soil_humidity' in latest_data.columns else None,
                "predicted_soil_humidity": round(float(predicted_humidity), 2),
                "features_used": self.model.top_features
            }
        except Exception as e:
            logger.error(f"Error predicting future humidity: {str(e)}")
            return {"error": f"Prediction error: {str(e)}"}