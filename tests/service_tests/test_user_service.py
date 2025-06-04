import pytest
from unittest.mock import MagicMock, patch
from services.users_service import UsersService


@pytest.fixture
def service():
    with patch("services.users_service.UsersRepository") as MockRepo, patch(
        "services.users_service.EnvironmentsService"
    ), patch("services.users_service.AuthService") as MockAuth:
        repo = MockRepo.return_value
        auth = MockAuth.return_value
        s = UsersService()
        s.repository = repo
        s.auth_service = auth
        return s


def test_get_all_users_success(service):
    service.repository.get_all_users.return_value = [{"email": "a@b.com"}]
    users = service.get_all_users()
    assert users == [{"email": "a@b.com"}]


def test_get_all_users_none(service):
    service.repository.get_all_users.return_value = []
    with pytest.raises(ValueError):
        service.get_all_users()


def test_add_permission_success(service):
    service.auth_service.check_user_permissions.return_value = True
    service.repository.add_permission.return_value = True
    user = {"user_email": "a@b.com"}
    assert service.add_permission("env1", user, "req_user") is True


def test_add_permission_no_email(service):
    user = {}
    with pytest.raises(ValueError):
        service.add_permission("env1", user, "req_user")


def test_add_permission_no_permission(service):
    service.auth_service.check_user_permissions.return_value = False
    user = {"user_email": "a@b.com"}
    with pytest.raises(ValueError):
        service.add_permission("env1", user, "req_user")


def test_get_user_environments(service):
    service.repository.get_user_environment_ids.return_value = ["env1", "env2"]
    envs = service.get_user_environments("user1")
    assert envs == ["env1", "env2"]


def test_get_user_success(service):
    service.repository.get_user.return_value = {"_id": "user1"}
    user = service.get_user("user1")
    assert user == {"_id": "user1"}


def test_get_user_invalid_id(service):
    with pytest.raises(ValueError):
        service.get_user("")


def test_get_user_not_found(service):
    service.repository.get_user.return_value = None
    with pytest.raises(ValueError):
        service.get_user("user1")


def test_delete_permission_success(service):
    service.repository.delete_permission.return_value = True
    user = {"user_email": "a@b.com"}
    assert service.delete_permission("env1", user) is True


def test_delete_permission_no_email(service):
    user = {}
    with pytest.raises(ValueError):
        service.delete_permission("env1", user)


def test_get_user_permissions_success(service):
    service.repository.get_user_permissions.return_value = ["perm1"]
    perms = service.get_user_permissions("env1")
    assert perms == ["perm1"]


def test_get_user_permissions_invalid_env(service):
    with pytest.raises(ValueError):
        service.get_user_permissions("")
