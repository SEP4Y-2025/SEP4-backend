import pytest
from unittest.mock import patch, MagicMock
from services.auth_service import AuthService


@pytest.fixture
def service():
    with patch("services.auth_service.AuthRepository") as MockAuthRepo, patch(
        "services.auth_service.UsersRepository"
    ) as MockUsersRepo:
        auth_repo = MockAuthRepo.return_value
        users_repo = MockUsersRepo.return_value
        s = AuthService()
        s.auth_repository = auth_repo
        s.users_repository = users_repo
        return s


def test_verify_password(service):
    with patch("services.auth_service.pwd_context.verify") as mock_verify:
        mock_verify.return_value = True
        assert service.verify_password("plain", "hashed") is True


def test_get_password_hash(service):
    with patch("services.auth_service.pwd_context.hash") as mock_hash:
        mock_hash.return_value = "hashed"
        assert service.get_password_hash("plain") == "hashed"


def test_authenticate_user_success(service):
    service.auth_repository.find_user_by_email.return_value = {"password": "hashed"}
    with patch.object(service, "verify_password", return_value=True):
        user = service.authenticate_user("a@b.com", "pw")
        assert user == {"password": "hashed"}


def test_authenticate_user_no_user(service):
    service.auth_repository.find_user_by_email.return_value = None
    assert service.authenticate_user("a@b.com", "pw") is False


def test_authenticate_user_wrong_password(service):
    service.auth_repository.find_user_by_email.return_value = {"password": "hashed"}
    with patch.object(service, "verify_password", return_value=False):
        assert service.authenticate_user("a@b.com", "pw") is False


def test_create_access_token(service):
    data = {"sub": "user"}
    token = service.create_access_token(data)
    assert "access_token" in token
    assert token["token_type"] == "bearer"
    assert token["expires_in"] == 1800


def test_create_user_success(service):
    service.auth_repository.find_user_by_email.return_value = None
    service.auth_repository.create_user.return_value = "user_id"
    with patch.object(service, "get_password_hash", return_value="hashed"):
        user_id = service.create_user("user", "pw", "a@b.com")
        assert user_id == "user_id"


def test_create_user_already_exists(service):
    service.auth_repository.find_user_by_email.return_value = {"email": "a@b.com"}
    assert service.create_user("user", "pw", "a@b.com") is None


def test_create_user_exception(service):
    service.auth_repository.find_user_by_email.side_effect = Exception("fail")
    assert service.create_user("user", "pw", "a@b.com") is None


def test_change_password_success(service):
    service.auth_repository.find_user_by_id.return_value = {"password": "old_hashed"}
    with patch.object(service, "verify_password", return_value=True), patch.object(
        service, "get_password_hash", return_value="new_hashed"
    ):
        service.auth_repository.update_user_password.return_value = True
        assert service.change_password("uid", "old", "new") is True


def test_change_password_user_not_found(service):
    service.auth_repository.find_user_by_id.return_value = None
    assert service.change_password("uid", "old", "new") is False


def test_change_password_wrong_old(service):
    service.auth_repository.find_user_by_id.return_value = {"password": "old_hashed"}
    with patch.object(service, "verify_password", return_value=False):
        assert service.change_password("uid", "old", "new") is False


def test_check_user_permissions_owner(service):
    service.users_repository.get_user_role.return_value = "Owner"
    assert service.check_user_permissions("uid", "eid") is True


def test_check_user_permissions_assistant(service):
    service.users_repository.get_user_role.return_value = "Plant Assistant"
    assert service.check_user_permissions("uid", "eid") is True


def test_check_user_permissions_none(service):
    service.users_repository.get_user_role.return_value = "Viewer"
    assert service.check_user_permissions("uid", "eid") is False
