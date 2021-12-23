import pytest
from pymongo import MongoClient

from qastorage.mongo_srore import MongoStore

TEST_DB_NAME = "test"


@pytest.fixture
def mongo_client():
    client = MongoClient(host="mongo", uuidRepresentation="standard")
    yield client
    client.close()


@pytest.fixture
def store(mongo_client: MongoClient) -> MongoStore:
    _store = MongoStore(mongo_client, TEST_DB_NAME)
    _store._client.drop_database(TEST_DB_NAME)
    return _store
