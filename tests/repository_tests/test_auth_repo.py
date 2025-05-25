import pytest
from unittest.mock import MagicMock, patch
from repositories.auth_repository import AuthRepository

@pytest.fixture
def repo():
    with patch("repositories.auth_repository.MongoClient") as MockClient:
        mock_client = MockClient.return_value
        mock_db = mock_client.__getitem__.return_value
        mock_collection = mock_db.__getitem__.return_value
        repo = AuthRepository()
        repo.collection = mock_collection
        return repo

def test_find_user_by_email_found(repo):
    repo.collection.find_one.return_value = {"email": "a@b.com"}
    user = repo.find_user_by_email("a@b.com")
    assert user == {"email": "a@b.com"}

def test_find_user_by_email_not_found(repo):
    repo.collection.find_one.return_value = None
    user = repo.find_user_by_email("notfound@b.com")
    assert user is None

def test_find_user_by_email_exception(repo):
    repo.collection.find_one.side_effect = Exception("DB error")
    user = repo.find_user_by_email("fail@b.com")
    assert user is None

def test_find_user_by_id_found(repo):
    repo.collection.find_one.return_value = {"_id": "someid"}
    user = repo.find_user_by_id("507f1f77bcf86cd799439011")
    assert user == {"_id": "someid"}

def test_find_user_by_id_exception(repo):
    repo.collection.find_one.side_effect = Exception("DB error")
    user = repo.find_user_by_id("507f1f77bcf86cd799439011")
    assert user is None

def test_create_user_success(repo):
    mock_result = MagicMock()
    mock_result.inserted_id = "507f1f77bcf86cd799439011"
    repo.collection.insert_one.return_value = mock_result
    user_id = repo.create_user({"username": "test"})
    assert user_id == "507f1f77bcf86cd799439011"

def test_create_user_exception(repo):
    repo.collection.insert_one.side_effect = Exception("Insert error")
    user_id = repo.create_user({"username": "fail"})
    assert user_id is None

def test_update_user_password_success(repo):
    mock_result = MagicMock()
    mock_result.modified_count = 1
    repo.collection.update_one.return_value = mock_result
    assert repo.update_user_password("507f1f77bcf86cd799439011", "newpass") is True

def test_update_user_password_failure(repo):
    mock_result = MagicMock()
    mock_result.modified_count = 0
    repo.collection.update_one.return_value = mock_result
    assert repo.update_user_password("507f1f77bcf86cd799439011", "newpass") is False

def test_update_user_password_exception(repo):
    repo.collection.update_one.side_effect = Exception("Update error")
    assert repo.update_user_password("507f1f77bcf86cd799439011", "newpass") is False