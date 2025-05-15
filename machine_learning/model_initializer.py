
import os
import logging
from datetime import datetime
from machine_learning.model_trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelInitializer:
    """A simpler model initializer without threading or scheduling"""
    
    def __init__(self, model_save_path="machine_learning/models/saved"):
        self.model_save_path = model_save_path
        self.model = None
        self.results = None
        
    def initialize(self):
        """Train the model if it doesn't exist"""
        logger.info("Initializing ML model")
        
        os.makedirs(self.model_save_path, exist_ok=True)
        
        model_path = os.path.join(self.model_save_path, "latest.pkl")
        if os.path.exists(model_path):
            logger.info(f"Model already exists at {model_path}")
            return True
            
        try:
            trainer = ModelTrainer(model_save_path=self.model_save_path)
            self.model, self.results = trainer.train_model()
            
            if self.model is None:
                logger.warning("Model training failed or not enough data")
                return False
                
            logger.info("Model trained successfully")
            
            log_file = os.path.join(self.model_save_path, "training_log.txt")
            with open(log_file, "a") as f:
                f.write(f"Initial training on {datetime.now()}:\n")
                if 'top_features' in self.results:
                    f.write(f"  Features: {self.results['top_features']}\n")
                if 'equation' in self.results:
                    f.write(f"  Equation: {self.results['equation']}\n")
                if 'metrics' in self.results and 'test' in self.results['metrics']:
                    f.write(f"  Test metrics: {self.results['metrics']['test']}\n\n")
            
            return True
                
        except Exception as e:
            logger.error(f"Error during model initialization: {str(e)}")
            return False

model_initializer = ModelInitializer()

def init_model():
    """Initialize the model - can be called from FastAPI startup event"""
    try:
        return model_initializer.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        return False