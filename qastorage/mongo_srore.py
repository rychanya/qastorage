from typing import Tuple, Union
from uuid import UUID, uuid4

from pymongo import MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from qastorage.base_store import AbstractStore, QABaseNotExist
from qastorage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO


class MongoStore(AbstractStore):

    BASES_COLLECTION_NAME = "Bases"
    GROUPS_COLLECTION_NAME = "Groups"

    def __init__(self, client: MongoClient, db_name: str) -> None:
        self._client = client
        self._db_name = db_name
        self._db = self._client.get_database(self._db_name)

    @property
    def _bases_collection(self) -> Collection:
        return self._db.get_collection(self.BASES_COLLECTION_NAME)

    @property
    def _groups_collection(self) -> Collection:
        return self._db.get_collection(self.GROUPS_COLLECTION_NAME)

    def get_or_create_base(
        self, dto: Union[QABaseDTO, UUID], session: ClientSession = None
    ) -> UUID:
        if isinstance(dto, UUID):
            doc = self._bases_collection.find_one(
                filter={"id": dto},
                session=session,
                projection={"_id": False, "id": True},
            )
            if doc is None:
                raise QABaseNotExist
        else:
            doc = self._bases_collection.find_one_and_update(
                filter={"question": dto.question, "type": dto.type},
                update={"$setOnInsert": {"id": uuid4()}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
                session=session,
                projection={"_id": False, "id": True},
            )
        return doc["id"]

    def get_or_create_group(
        self, dto: Union[QAGroupDTO, UUID], base_id: UUID, session: ClientSession = None
    ) -> UUID:
        doc = list(
            self._groups_collection.aggregate(
                pipeline=[
                    {"$match": {"base_id": base_id}},
                    {
                        "$match": {
                            "$expr": {"$setEquals": ["$all_answers", dto.all_answers]}
                        }
                    },
                    {
                        "$match": {
                            "$expr": {"$setEquals": ["$all_extra", dto.all_extra]}
                        }
                    },
                ],
                session=session,
            )
        )
        if doc:
            return doc[0]["id"]
        else:
            id = uuid4()
            self._groups_collection.insert_one(
                {
                    "all_answers": dto.all_answers,
                    "all_extra": dto.all_extra,
                    "id": id,
                    "base_id": base_id,
                },
                session=session,
            )
            return id

    def get_or_create_qa(
        self, dto: QAAnswerDTO, session: ClientSession = None
    ) -> Tuple[UUID, bool]:
        base_id = self.get_or_create_base(dto, session=session)
        if dto.group is None:
            group_id = None
        elif isinstance(dto.group, UUID):
            group_id = dto.group
            group_doc = self._groups_collection.find_one({"id": group_id})
            dto.group = QAGroupDTO.parse_obj(group_doc)
            assert dto.group.base_id == base_id
        else:
            group_id = self.get_or_create_group(dto.group, base_id, session=session)

        return (uuid4(), False)
