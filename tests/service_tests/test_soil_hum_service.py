import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from services.soil_humidity_prediction_service import SoilHumidityPredictionService


@pytest.fixture
def service():
    with patch(
        "services.soil_humidity_prediction_service.DataProcessor"
    ) as MockDP, patch(
        "services.soil_humidity_prediction_service.SoilHumidityPredictor"
    ) as MockPredictor:
        dp = MockDP.return_value
        predictor = MockPredictor.return_value
        s = SoilHumidityPredictionService()
        s.data_processor = dp
        s.model = predictor
        s.model.top_features = ["temperature", "air_humidity"]
        return s


def test_predict_humidity_simple_with_current(service):
    result = service.predict_humidity_simple(
        25, 50, current_humidity=200, minutes_ahead=10
    )
    assert isinstance(result, float)
    assert result > 0


def test_predict_humidity_simple_without_current(service):
    result = service.predict_humidity_simple(
        25, 50, current_humidity=None, minutes_ahead=10
    )
    assert isinstance(result, float)


def test_preprocess_input_dict(service):
    data = {"timestamp": "2024-01-01T12:00:00"}
    df = service.preprocess_input(data)
    assert isinstance(df, pd.DataFrame)


def test_predict_success(service):
    # Mock model.predict to return a list
    service.model.predict.return_value = [123.4]
    df = pd.DataFrame([{"temperature": 25, "air_humidity": 50}])
    service.model.top_features = ["temperature", "air_humidity"]
    result = service.predict(df)
    assert result == 123.4


def test_predict_fallback_on_exception(service):
    # Simulate exception in model.predict
    def raise_exc(*a, **kw):
        raise Exception("fail")

    service.model.predict.side_effect = raise_exc
    df = pd.DataFrame([{"temperature": 25, "air_humidity": 50, "soil_humidity": 200}])
    service.model.top_features = ["temperature", "air_humidity"]
    result = service.predict(df)
    assert isinstance(result, float)


def test_predict_future_humidity_success(service):
    # Mock latest_data DataFrame
    latest_data = pd.DataFrame(
        [
            {
                "plant_pot_id": "pot1",
                "timestamp": pd.Timestamp("2024-01-01T12:00:00"),
                "temperature": 25,
                "air_humidity": 50,
                "soil_humidity": 200,
            }
        ]
    )
    service.data_processor.get_latest_data_for_prediction.return_value = latest_data
    service.data_processor.extract_time_features.return_value = latest_data
    service.model.predict.return_value = [210.0]
    service.model.top_features = ["temperature", "air_humidity"]
    result = service.predict_future_humidity("pot1", 5)
    assert result["plant_pot_id"] == "pot1"
    assert "predicted_soil_humidity" in result


def test_predict_future_humidity_no_data(service):
    service.data_processor.get_latest_data_for_prediction.return_value = None
    result = service.predict_future_humidity("pot1", 5)
    assert "error" in result


def test_get_model_metrics_trained(service):
    with patch(
        "services.soil_humidity_prediction_service.os.path.exists", return_value=True
    ), patch(
        "services.soil_humidity_prediction_service.SoilHumidityPredictor.load"
    ) as mock_load:
        mock_predictor = MagicMock()
        mock_predictor.top_features = ["temperature", "air_humidity"]
        mock_predictor.evaluate.return_value = {"mse": 1, "rmse": 1, "mae": 1, "r2": 1}
        mock_predictor.feature_importance = {"temperature": 0.7, "air_humidity": 0.3}
        mock_load.return_value = mock_predictor
        service.data_processor.process_data.return_value = (
            None,
            pd.DataFrame([{"temperature": 25, "air_humidity": 50}]),
            pd.Series([200]),
        )
        metrics = service.get_model_metrics()
        assert metrics["model_type"] == "machine_learning"
        assert "feature_importance" in metrics


def test_get_model_metrics_fallback(service):
    with patch(
        "services.soil_humidity_prediction_service.os.path.exists", return_value=False
    ):
        metrics = service.get_model_metrics()
        assert metrics["model_type"] == "fallback"
