import pytest
from pymongo import MongoClient
from testcontainers.mongodb import MongoDbContainer

from storage.mongo_store import MongoStore

TEST_DB_NAME = "test"


@pytest.fixture
def mongo_client():
    with MongoDbContainer() as mongo:
        url = mongo.get_connection_url()
        client = MongoClient(host=url, uuidRepresentation="standard")
        yield client
        client.close()


@pytest.fixture
def store(mongo_client: MongoClient) -> MongoStore:
    _store = MongoStore(mongo_client, TEST_DB_NAME)
    _store._client.drop_database(TEST_DB_NAME)
    return _store
