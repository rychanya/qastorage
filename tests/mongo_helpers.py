from typing import Optional

from pymongo import MongoClient
from pymongo.client_session import ClientSession
from testcontainers.mongodb import MongoDbContainer

from storage.dto import QABaseDTO, QAGroupDTO
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
    data: tuple[dict, dict, Optional[dict]],
    session: ClientSession = None,
):
    answer_dict, base_dict, group_dict = data
    base_id = store.get_or_create_base(QABaseDTO.parse_obj(base_dict)).id
    if group_dict is None:
        group_id = None
    else:
        group = store.get_or_create_group(QAGroupDTO.parse_obj(group_dict), base_id)
        assert group
        group_id = group.id
    store._answers_collection.insert_one(
        {
            "id": answer_dict["id"],
            "base_id": base_id,
            "group_id": group_id,
            "answer": answer_dict["answer"],
            "is_correct": answer_dict["is_correct"],
        },
        session=session,
    )


def find_answer_raw(store: MongoStore, session: ClientSession = None):
    return store._answers_collection.find_one({}, session=session)


def count_answer(store: MongoStore, session: ClientSession = None) -> int:
    return store._answers_collection.count_documents({}, session=session)
