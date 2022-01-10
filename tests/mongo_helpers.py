from typing import Optional
from uuid import UUID

from pymongo import MongoClient
from pymongo.client_session import ClientSession
from testcontainers.mongodb import MongoDbContainer

from storage.mongo_store import MongoStore


class StoreContext:
    def __init__(self) -> None:
        self.TEST_DB_NAME = "test"
        self.mongo = MongoDbContainer().start()
        self.client = MongoClient(
            host=self.mongo.get_connection_url(), uuidRepresentation="standard"
        )
        self.client.drop_database(self.TEST_DB_NAME)

    def __enter__(self):
        return MongoStore(self.client, self.TEST_DB_NAME)

    def __exit__(self, xc_type, exc_value, traceback):  # noqa
        self.client.close()
        self.mongo.stop()


def insert_base_row(store: MongoStore, data: dict, session: ClientSession = None):
    store._bases_collection.insert_one(data, session=session)


def find_base_row(store: MongoStore, session: ClientSession = None):
    return store._bases_collection.find_one({}, session=session)


def count_base(store: MongoStore, session: ClientSession = None) -> int:
    return store._bases_collection.count_documents({}, session=session)


def insert_group_row(store: MongoStore, data: dict, session: ClientSession = None):
    store._groups_collection.insert_one(data, session=session)


def find_group_row(store: MongoStore, session: ClientSession = None):
    return store._groups_collection.find_one({}, session=session)


def count_group(store: MongoStore, session: ClientSession = None) -> int:
    return store._groups_collection.count_documents({}, session=session)


def insert_answer_raw(
    store: MongoStore,
    data: dict,
    group_id: Optional[UUID],
    base_id: UUID,
    session: ClientSession = None,
):
    store._answers_collection.insert_one(
        {
            "id": data["id"],
            "base_id": base_id,
            "group_id": group_id,
            "answer": data["answer"],
            "is_correct": data["is_correct"],
        },
        session=session,
    )


def find_answer_raw(store: MongoStore, session: ClientSession = None):
    return store._answers_collection.find_one({}, session=session)


def count_answer(store: MongoStore, session: ClientSession = None) -> int:
    return store._answers_collection.count_documents({}, session=session)
