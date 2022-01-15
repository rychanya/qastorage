import pytest
from testcontainers.mongodb import MongoDbContainer

from storage import StoreType
from storage import get_store as get_storage
from storage.mongo_store import MongoStore


@pytest.fixture(scope="session")
def mongo_connection_url():
    _mongo = MongoDbContainer().start()
    yield _mongo.get_connection_url()
    _mongo.stop()


# @pytest.fixture
# def mongo_settings(monkeypatch, mongo_connection_url):
#     monkeypatch.setenv("qa_storage_url", mongo_connection_url)
#     monkeypatch.setenv("qa_storage_db_name", "test")


@pytest.fixture
def get_store(monkeypatch, mongo_connection_url):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
            monkeypatch.setenv("qa_storage_url", mongo_connection_url)
            monkeypatch.setenv("qa_storage_db_name", db_name)
            _store = get_storage()
            if not isinstance(_store, MongoStore):
                raise ValueError
            _store._client.drop_database(db_name)
            return _store
        else:
            raise ValueError

    return _get_store


@pytest.fixture
def set_store_settings(monkeypatch, mongo_connection_url):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
            monkeypatch.setenv("qa_storage_url", mongo_connection_url)
            monkeypatch.setenv("qa_storage_db_name", db_name)
        else:
            monkeypatch.setenv("qa_storage_type", store_name)

    return _get_store
