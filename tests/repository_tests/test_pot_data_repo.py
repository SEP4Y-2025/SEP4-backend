import pytest
from unittest.mock import patch, MagicMock
from repositories.plant_data_repository import PlantDataRepository
from bson import ObjectId

@pytest.fixture
def repo():
    with patch("repositories.plant_data_repository.MongoClient") as MockClient:
        mock_client = MockClient.return_value
        mock_db = mock_client.__getitem__.return_value
        mock_collection = mock_db.__getitem__.return_value
        repo = PlantDataRepository()
        repo.collection = mock_collection
        return repo

def test_get_latest_data_with_id(repo):
    repo.collection.find.return_value.sort.return_value.limit.return_value = [{"plant_pot_id": "pot1"}]
    data = repo.get_latest_data("pot1")
    assert data == [{"plant_pot_id": "pot1"}]
    repo.collection.find.assert_called_with({"plant_pot_id": "pot1"})

def test_get_latest_data_without_id(repo):
    repo.collection.find.return_value.sort.return_value.limit.return_value = [{"plant_pot_id": "pot1"}]
    data = repo.get_latest_data()
    assert data == [{"plant_pot_id": "pot1"}]
    repo.collection.find.assert_called_with()

def test_get_latest_data_exception(repo):
    repo.collection.find.side_effect = Exception("fail")
    data = repo.get_latest_data("pot1")
    assert data == []

def test_get_all_data_success(repo):
    oid = ObjectId()
    repo.collection.find.return_value = [
        {"_id": oid, "plant_pot_id": "pot1"},
        {"_id": "already_str", "plant_pot_id": "pot2"}
    ]
    data = repo.get_all_data()
    assert data[0]["_id"] == str(oid)
    assert data[1]["_id"] == "already_str"

def test_get_all_data_empty(repo):
    repo.collection.find.return_value = []
    data = repo.get_all_data()
    assert data == []

def test_get_all_data_exception(repo):
    repo.collection.find.side_effect = Exception("fail")
    data = repo.get_all_data()
    assert data == []