__version__ = "0.2.0"

from enum import Enum

from pydantic import BaseSettings

from storage.base_store import AbstractStore


class StoreType(str, Enum):
    Mongo = "Mongo"


class StoreSettings(BaseSettings):
    type: str = StoreType.Mongo

    class Config:
        env_prefix = "qa_storage_"


def get_store() -> AbstractStore:
    settings = StoreSettings()
    if settings.type == StoreType.Mongo:
        from storage.mongo_store import MongoSettings, MongoStore

        return MongoStore(MongoSettings())
    else:
        raise ValueError
