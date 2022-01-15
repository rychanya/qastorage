import pytest

from storage import StoreType, get_store
from storage.mongo_store import MongoStore


def test_mongo(set_store_settings):
    set_store_settings(StoreType.Mongo)
    store = get_store()
    assert isinstance(store, MongoStore)


def test_incorrect_storage_name(set_store_settings):
    incorrect_storage_name = "incrrect"
    assert incorrect_storage_name not in list(StoreType)
    set_store_settings(incorrect_storage_name)

    with pytest.raises(ValueError):
        get_store()
