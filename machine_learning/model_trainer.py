from machine_learning.data_processor import DataProcessor
from machine_learning.feature_selector import NeuralFeatureSelector
from machine_learning.soil_predictor import SoilHumidityPredictor
from sklearn.model_selection import train_test_split
import pandas as pd
import os
import datetime
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model_save_path="machine_learning/models/saved"):
        self.model_save_path = model_save_path
        self.data_processor = DataProcessor()
        self.training_metrics = None
        
    def train_model(self, random_state=42):
        logger.info("Starting XGBoost model training process")
        
        try:
            data, X, y = self.data_processor.process_data()
            
            if X.empty or len(y) < 10:
                logger.warning("Not enough data to train a model. Need at least 10 samples.")
                return None, {"error": "Not enough data to train a model"}
            
            logger.info(f"Training with {len(y)} samples and {X.shape[1]} features")
            
            X_train_val, X_test, y_train_val, y_test = train_test_split(
                X, y, test_size=0.20, random_state=random_state
            )
            
            X_train, X_val, y_train, y_val = train_test_split(
                X_train_val, y_train_val, test_size=0.2, random_state=random_state
            )
            
            logger.info("Training neural network for feature selection")
            feature_selector = NeuralFeatureSelector(input_dim=X.shape[1])
            feature_selector.train(X_train, y_train, X_val, y_val)
            
            top_features = feature_selector.get_top_features(X_test, X.columns, top_n=4)  # Increased to top 4 features
            logger.info(f"Top features selected: {top_features}")
            
            logger.info("Training XGBoost model with selected features")
            predictor = SoilHumidityPredictor()
            equation = predictor.train(X, y, top_features)
            
            logger.info("Evaluating model performance")
            train_metrics = predictor.evaluate(X_train, y_train)
            val_metrics = predictor.evaluate(X_val, y_val)
            test_metrics = predictor.evaluate(X_test, y_test)
            
            logger.info(f"Train metrics: {train_metrics}")
            logger.info(f"Validation metrics: {val_metrics}")
            logger.info(f"Test metrics: {test_metrics}")
            
            self.training_metrics = {
                'train': train_metrics,
                'validation': val_metrics,
                'test': test_metrics
            }
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"soil_humidity_model_{timestamp}.pkl"
            model_path = os.path.join(self.model_save_path, model_filename)
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            logger.info(f"Saving model to {model_path}")
            predictor.save(model_path)
            
            latest_path = os.path.join(self.model_save_path, "latest.pkl")
            predictor.save(latest_path)
            
            results = {
                'timestamp': timestamp,
                'top_features': top_features,
                'equation': equation,
                'metrics': self.training_metrics
            }
            
            logger.info("Model training completed successfully")
            return predictor, results
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error during model training: {str(e)}")
            return None, {"error": f"Model training error: {str(e)}"}

    def get_metrics(self):
        """Return the latest training metrics"""
        return self.training_metrics