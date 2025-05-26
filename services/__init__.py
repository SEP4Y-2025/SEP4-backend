__all__ = []

# Import the soil_humidity_prediction_service module by default
try:
    from services.soil_humidity_prediction_service import SoilHumidityPredictionService
    __all__.append('SoilHumidityPredictionService')
except ImportError:
    pass