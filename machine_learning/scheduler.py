import schedule
import time
import os
from datetime import datetime
import threading
import logging
from machine_learning.model_trainer import ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelScheduler:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, model_save_path="machine_learning/models/saved"):
        self.model_save_path = model_save_path
        self.trainer = None
        self.model = None
        self.results = None
        self._initialized = False
        self._scheduler_thread = None

    def initialize(self):
        if self._initialized:
            return

        os.makedirs(self.model_save_path, exist_ok=True)

        self.trainer = ModelTrainer(model_save_path=self.model_save_path)

        try:
            self.retrain_model()
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")

    def retrain_model(self):
        logger.info("Starting model retraining")

        try:
            self.model, self.results = self.trainer.train_model()

            if self.model is None:
                logger.warning("Model training failed or not enough data")
                return

            logger.info("Model retrained successfully")

            log_file = os.path.join(self.model_save_path, "training_log.txt")
            with open(log_file, "a") as f:
                f.write(f"Retraining on {datetime.now()}:\n")
                f.write(f"  Features: {self.results['top_features']}\n")
                f.write(f"  Equation: {self.results['equation']}\n")
                f.write(f"  Test metrics: {self.results['metrics']['test']}\n\n")

        except Exception as e:
            logger.error(f"Error during model retraining: {str(e)}")

    def _scheduler_loop(self, retraining_time="00:00"):
        schedule.every().day.at(retraining_time).do(self.retrain_model)

        while True:
            schedule.run_pending()
            time.sleep(60)

    def start_scheduler(self, retraining_time="00:00"):
        if not self._initialized:
            self.initialize()

        if self._scheduler_thread is None or not self._scheduler_thread.is_alive():
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop, args=(retraining_time,), daemon=True
            )
            self._scheduler_thread.start()
            logger.info(
                f"Scheduler started in background thread, retraining at {retraining_time}"
            )

    def get_model_metrics(self):
        if not self._initialized:
            try:
                self.initialize()
            except Exception as e:
                logger.error(
                    f"Failed to initialize model when getting metrics: {str(e)}"
                )
                return None

        if self.trainer:
            return self.trainer.get_metrics()
        return None


# SINGLETON DESIGN PATTERN
model_scheduler = ModelScheduler.get_instance()


def init_model_scheduler():
    try:
        model_scheduler.initialize()
        model_scheduler.start_scheduler()
        return model_scheduler
    except Exception as e:
        logger.error(f"Failed to initialize model scheduler: {str(e)}")
        return None
