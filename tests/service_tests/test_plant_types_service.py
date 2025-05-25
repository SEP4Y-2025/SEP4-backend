import pytest
from unittest.mock import MagicMock, patch
from services.plant_types_service import PlantTypesService

@pytest.fixture
def service():
    with patch("services.plant_types_service.PlantTypesRepository") as MockRepo, \
         patch("services.plant_types_service.AuthService") as MockAuth, \
         patch("services.plant_types_service.EnvironmentsRepository"), \
         patch("services.plant_types_service.ArduinosRepository"):
        repo = MockRepo.return_value
        auth = MockAuth.return_value
        service = PlantTypesService()
        service.repository = repo
        service.auth_service = auth
        return service

def test_get_all_plant_types_permission_granted(service):
    service.auth_service.check_user_permissions.return_value = True
    service.repository.get_plant_types_by_environment.return_value = [{"name": "Tomato"}]
    result = service.get_all_plant_types("env_id", "user_id")
    assert result == [{"name": "Tomato"}]

def test_get_all_plant_types_permission_denied(service):
    service.auth_service.check_user_permissions.return_value = False
    service.repository.get_plant_types_by_environment.return_value = []
    with pytest.raises(ValueError):
        service.get_all_plant_types("env_id", "user_id")

def test_add_plant_type_success(service):
    plant_type = {
        "name": "Tomato",
        "environment_id": "env_id",
        "water_dosage": 10,
        "watering_frequency": 2
    }
    service.repository.get_environment_by_id.return_value = {"_id": "env_id"}
    service.repository.post_plant_type.return_value = "new_id"
    result = service.add_plant_type(plant_type)
    assert result == "new_id"

def test_add_plant_type_missing_fields(service):
    with pytest.raises(ValueError):
        service.add_plant_type({"name": "Tomato"})

def test_add_plant_type_invalid_water(service):
    plant_type = {
        "name": "Tomato",
        "environment_id": "env_id",
        "water_dosage": 0,
        "watering_frequency": 2
    }
    with pytest.raises(ValueError):
        service.add_plant_type(plant_type)