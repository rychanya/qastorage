import subprocess
from tempfile import TemporaryDirectory

import pytest

from storage import StoreType
from storage import get_store as get_storage
from storage.mongo_store import MongoStore


@pytest.fixture(scope="session", autouse=True)
def mongo_client():
    with TemporaryDirectory() as tempdir:
        with subprocess.Popen(
            [
                "mongod",
                "--replSet",
                "rs0",
                "--dbpath",
                tempdir,
                "--bind_ip",
                "localhost",
            ],
            stdout=subprocess.DEVNULL,
        ) as mongo:
            subprocess.run(["mongosh", "--eval", "rs.initiate()"], stdout=subprocess.DEVNULL)

            yield

            mongo.terminate()
            mongo.wait()


@pytest.fixture
def get_store(monkeypatch):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
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
def set_store_settings(monkeypatch):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
            monkeypatch.setenv("qa_storage_db_name", db_name)
        else:
            monkeypatch.setenv("qa_storage_type", store_name)

    return _get_store
