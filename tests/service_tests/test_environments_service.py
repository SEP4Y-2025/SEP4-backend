from bson import ObjectId
import pytest
from unittest.mock import MagicMock, patch
from services.environments_service import EnvironmentsService
from models.environment import AddEnvironmentRequest

@pytest.fixture
def service():
    with patch("services.environments_service.EnvironmentsRepository") as MockEnvRepo, \
         patch("services.environments_service.PlantPotsService") as MockPlantPotsService, \
         patch("services.environments_service.UsersRepository") as MockUsersRepo:
        env_repo = MockEnvRepo.return_value
        plant_pots_service = MockPlantPotsService.return_value
        users_repo = MockUsersRepo.return_value
        s = EnvironmentsService()
        s.environments_repository = env_repo
        s.plant_pots_service = plant_pots_service
        s.user_repository = users_repo
        return s

def test_get_environments(service):
    service.environments_repository.get_environments.return_value = [{"name": "env1"}]
    result = service.get_environments()
    assert result == [{"name": "env1"}]

def test_get_environment_by_id_owner(service):
    env = {"owner_id": "user1"}
    service.environments_repository.get_environment_by_id.return_value = env
    result = service.get_environment_by_id("env1", "user1")
    assert result == env

def test_get_environment_by_id_plant_assistant(service):
    env = {
        "owner_id": "user2",
        "access_control": [{"user_id": "user1", "role": "Plant Assistant"}]
    }
    service.environments_repository.get_environment_by_id.return_value = env
    result = service.get_environment_by_id("env1", "user1")
    assert result == env

def test_get_environment_by_id_no_permission(service):
    env = {
        "owner_id": "user2",
        "access_control": [{"user_id": "user1", "role": "Viewer"}]
    }
    service.environments_repository.get_environment_by_id.return_value = env
    with pytest.raises(ValueError):
        service.get_environment_by_id("env1", "user1")

def test_get_environment_by_id_not_found(service):
    service.environments_repository.get_environment_by_id.return_value = None
    assert service.get_environment_by_id("env1", "user1") is None

def test_add_environment_success(service):
    req = AddEnvironmentRequest(name="env1")
    service.environments_repository.environment_name_exists.return_value = False
    service.environments_repository.add_environment.return_value = "env_id"
    service.user_repository.add_environment_to_user.return_value = None
    user_id = str(ObjectId())
    resp = service.add_environment(req, user_id)
    assert resp.environment_id == "env_id"
    assert resp.name == "env1"

def test_add_environment_duplicate_name(service):
    req = AddEnvironmentRequest(name="env1")
    service.environments_repository.environment_name_exists.return_value = True
    with pytest.raises(ValueError):
        service.add_environment(req, "user1")

def test_delete_environment_success(service):
    env = {
        "owner_id": "user1",
        "plant_pots": [{"pot_id": "pot1"}, {"pot_id": "pot2"}]
    }
    service.environments_repository.get_environment_by_id.return_value = env
    service.plant_pots_service.delete_plant_pot.return_value = True
    service.user_repository.remove_environment_from_user.return_value = None
    service.environments_repository.delete_environment.return_value = True
    assert service.delete_environment("env1", "user1") is True

def test_delete_environment_not_owner(service):
    env = {"owner_id": "user2"}
    service.environments_repository.get_environment_by_id.return_value = env
    with pytest.raises(ValueError):
        service.delete_environment("env1", "user1")

def test_delete_environment_not_found(service):
    service.environments_repository.get_environment_by_id.return_value = None
    assert service.delete_environment("env1", "user1") is False

def test_get_environments_by_user(service):
    service.user_repository.get_user_environment_ids.return_value = ["env1", "env2"]
    result = service.get_environments_by_user("user1")
    assert result == ["env1", "env2"]