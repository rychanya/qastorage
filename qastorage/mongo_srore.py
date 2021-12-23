from uuid import UUID, uuid4

from pymongo import MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from qastorage.base_store import AbstractStore
from qastorage.dto import BaseDTO


class MongoStore(AbstractStore):

    BASE_COLLECTION_NAME = "Base"

    def __init__(self, client: MongoClient, db_name: str) -> None:
        self._client = client
        self._db_name = db_name
        self._db = self._client.get_database(self._db_name)

    @property
    def _base_collection(self) -> Collection:
        return self._db.get_collection(self.BASE_COLLECTION_NAME)

    def get_or_create_base(self, dto: BaseDTO, session: ClientSession = None) -> UUID:
        doc = self._base_collection.find_one_and_update(
            filter={"question": dto.question, "type": dto.type},
            update={"$setOnInsert": {"id": uuid4()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        return doc["id"]
