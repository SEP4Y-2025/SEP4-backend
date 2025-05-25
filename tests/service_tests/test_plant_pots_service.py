from bson import ObjectId
import pytest
from unittest.mock import MagicMock, patch
from services.plant_pots_service import PlantPotsService
from models.plant_pot import AddPlantPotRequest

@pytest.fixture
def service():
    with patch("services.plant_pots_service.EnvironmentsRepository") as MockEnvRepo, \
         patch("services.plant_pots_service.ArduinosRepository") as MockArduinoRepo, \
         patch("services.plant_pots_service.PlantTypesRepository") as MockPlantTypeRepo, \
         patch("services.plant_pots_service.SensorReadingsRepository") as MockSensorRepo, \
         patch("services.plant_pots_service.AuthService") as MockAuth:
        env_repo = MockEnvRepo.return_value
        arduino_repo = MockArduinoRepo.return_value
        plant_type_repo = MockPlantTypeRepo.return_value
        sensor_repo = MockSensorRepo.return_value
        auth = MockAuth.return_value
        s = PlantPotsService()
        s.environments_repo = env_repo
        s.arduinos_repo = arduino_repo
        s.plant_types_repo = plant_type_repo
        s.sensor_readings_repo = sensor_repo
        s.auth_service = auth
        return s

def test_add_plant_pot_success(service):
    req = AddPlantPotRequest(
        pot_id="pot_1",
        plant_pot_label="My Pot",
        plant_type_id=str(ObjectId())
    )
    service.auth_service.check_user_permissions.return_value = True
    service.arduinos_repo.is_registered.return_value = True
    service.plant_types_repo.get_plant_type_by_id.return_value = {
        "watering_frequency": 7,
        "water_dosage": 100,
        "name": "Tomato"
    }
    service.environments_repo.insert_pot.return_value = None
    service.arduinos_repo.mark_active.return_value = None

    resp = service.add_plant_pot("env_1", req, "user_1")
    assert resp.pot_id == "pot_1"
    assert resp.plant_pot_label == "My Pot"
    assert resp.plant_type_name == "Tomato"
    assert resp.watering_frequency == 7
    assert resp.water_dosage == 100

def test_add_plant_pot_permission_denied(service):
    req = AddPlantPotRequest(
        pot_id="pot_1",
        plant_pot_label="My Pot",
        plant_type_id="plant_type_1"
    )
    service.auth_service.check_user_permissions.return_value = False
    with pytest.raises(ValueError):
        service.add_plant_pot("env_1", req, "user_1")

def test_add_plant_pot_invalid_label(service):
    req = AddPlantPotRequest(
        pot_id="pot_1",
        plant_pot_label="   ",
        plant_type_id="plant_type_1"
    )
    service.auth_service.check_user_permissions.return_value = True
    with pytest.raises(ValueError):
        service.add_plant_pot("env_1", req, "user_1")

def test_add_plant_pot_unregistered_arduino(service):
    req = AddPlantPotRequest(
        pot_id="pot_1",
        plant_pot_label="My Pot",
        plant_type_id="plant_type_1"
    )
    service.auth_service.check_user_permissions.return_value = True
    service.arduinos_repo.is_registered.return_value = False
    with pytest.raises(ValueError):
        service.add_plant_pot("env_1", req, "user_1")

def test_add_plant_pot_invalid_plant_type(service):
    req = AddPlantPotRequest(
        pot_id="pot_1",
        plant_pot_label="My Pot",
        plant_type_id="plant_type_1"
    )
    service.auth_service.check_user_permissions.return_value = True
    service.arduinos_repo.is_registered.return_value = True
    service.plant_types_repo.get_plant_type_by_id.return_value = None
    with pytest.raises(ValueError):
        service.add_plant_pot("env_1", req, "user_1")

def test_get_plant_pot_by_id_success(service):
    service.auth_service.check_user_permissions.return_value = True
    service.environments_repo.find_pot_by_id.return_value = {
        "pot_id": "pot_1",
        "label": "My Pot",
        "plant_type_id": "plant_type_1",
        "state": {
            "soil_humidity": 10,
            "air_humidity": 20,
            "temperature": 21,
            "light_intensity": 100,
            "water_tank_capacity": 500,
            "water_level": 80,
            "measured_at": "2024-01-01 00:00:00"
        }
    }
    service.plant_types_repo.get_plant_type_by_id.return_value = {
        "name": "Tomato",
        "watering_frequency": 7,
        "water_dosage": 100
    }
    resp = service.get_plant_pot_by_id("env_1", "pot_1", "user_1")
    assert resp.pot_id == "pot_1"
    assert resp.plant_pot_label == "My Pot"
    assert resp.plant_type_name == "Tomato"

def test_get_plant_pot_by_id_not_found(service):
    service.auth_service.check_user_permissions.return_value = True
    service.environments_repo.find_pot_by_id.return_value = None
    with pytest.raises(ValueError):
        service.get_plant_pot_by_id("env_1", "pot_1", "user_1")

def test_delete_plant_pot_success(service):
    service.auth_service.check_user_permissions.return_value = True
    service.arduinos_repo.is_registered.return_value = True
    service.environments_repo.find_pot_by_id.return_value = {"pot_id": "pot_1"}
    service.sensor_readings_repo.delete_by_pot.return_value = 1
    service.environments_repo.delete_pot.return_value = True
    service.arduinos_repo.mark_inactive.return_value = None
    assert service.delete_plant_pot("pot_1", "env_1", "user_1") is True

def test_delete_plant_pot_permission_denied(service):
    service.auth_service.check_user_permissions.return_value = False
    with pytest.raises(ValueError):
        service.delete_plant_pot("pot_1", "env_1", "user_1")

def test_get_pots_by_environment_success(service):
    service.auth_service.check_user_permissions.return_value = True
    service.environments_repo.get_environment_by_id.return_value = {"_id": "env_1"}
    service.environments_repo.get_pots_by_environment.return_value = [{"pot_id": "pot_1"}]
    pots = service.get_pots_by_environment("env_1", "user_1")
    assert pots == [{"pot_id": "pot_1"}]

def test_get_pots_by_environment_permission_denied(service):
    service.auth_service.check_user_permissions.return_value = False
    service.environments_repo.get_environment_by_id.return_value = {"_id": "env_1"}
    with pytest.raises(ValueError):
        service.get_pots_by_environment("env_1", "user_1")

def test_get_historical_data_success(service):
    service.auth_service.check_user_permissions.return_value = True
    service.arduinos_repo.is_registered.return_value = True
    service.environments_repo.find_pot_by_id.return_value = {"pot_id": "pot_1"}
    service.sensor_readings_repo.get_historical_data.return_value = [{"data": 1}]
    data = service.get_historical_data("pot_1", "env_1", "user_1")
    assert data == [{"data": 1}]

def test_get_historical_data_permission_denied(service):
    service.auth_service.check_user_permissions.return_value = False
    with pytest.raises(ValueError):
        service.get_historical_data("pot_1", "env_1", "user_1")