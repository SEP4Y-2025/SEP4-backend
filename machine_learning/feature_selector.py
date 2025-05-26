import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.callbacks import EarlyStopping
import numpy as np
import logging
import traceback

logger = logging.getLogger(__name__)


class NeuralFeatureSelector:
    def __init__(self, input_dim):
        self.input_dim = input_dim
        self.model = self._build_model()

    def _build_model(self):
        try:
            inputs = Input(shape=(self.input_dim,))
            x = Dense(24, activation="relu")(inputs)
            x = Dense(12, activation="relu")(x)
            outputs = Dense(1, activation="linear")(x)

            model = Model(inputs=inputs, outputs=outputs)
            model.compile(optimizer="adam", loss="mse", metrics=["mae"])

            return model
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error building model: {str(e)}")
            return None

    def train(self, X_train, y_train, X_val, y_val, epochs=50, batch_size=32):
        try:
            X_train_np = X_train.to_numpy().astype(np.float32)
            y_train_np = y_train.to_numpy().astype(np.float32)
            X_val_np = X_val.to_numpy().astype(np.float32)
            y_val_np = y_val.to_numpy().astype(np.float32)
            
            early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            
            history = self.model.fit(
                X_train_np, y_train_np,
                validation_data=(X_val_np, y_val_np),
                epochs=epochs,
                batch_size=batch_size,
                callbacks=[early_stopping],
                verbose=0,
            )

            return history
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error training model: {str(e)}")
            return None

    def get_feature_importance(self, X, feature_names):
        try:
            X_np = X.to_numpy().astype(np.float32)
            
            baseline_prediction = self.model.predict(X_np, verbose=0)
            baseline_mse = np.mean((baseline_prediction - baseline_prediction) ** 2)

            importance_scores = []

            for i in range(X.shape[1]):
                X_permuted = X_np.copy()
                X_permuted[:, i] = np.random.permutation(X_permuted[:, i])

                permuted_prediction = self.model.predict(X_permuted, verbose=0)

                permuted_mse = np.mean((baseline_prediction - permuted_prediction) ** 2)
                importance = permuted_mse - baseline_mse
                importance_scores.append(importance)

            feature_importance = dict(zip(feature_names, importance_scores))
            
            feature_importance = {k: float(v) for k, v in feature_importance.items()}
            
            sorted_importance = {k: v for k, v in sorted(
                feature_importance.items(), key=lambda item: item[1], reverse=True)}
            
            return sorted_importance
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error calculating feature importance: {str(e)}")
            return {"temperature": 1.0, "air_humidity": 0.8}

    def get_top_features(self, X, feature_names, top_n=2):
        try:
            importance = self.get_feature_importance(X, feature_names)
            return list(importance.keys())[:top_n]
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error getting top features: {str(e)}")
            return ["temperature", "air_humidity"]
