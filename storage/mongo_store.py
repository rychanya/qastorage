from typing import Optional, Tuple, Union
from uuid import UUID, uuid4

from pymongo import MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from storage.base_store import (
    AbstractStore,
    QAAnswerNotExist,
    QABaseNotExist,
    QABasesDoNotMatch,
    QAGroupNotExist,
    QAStoreException,
)
from storage.db_models import QAAnswer, QABase, QAGroup
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO, QATypeEnum


class MongoStore(AbstractStore):

    BASES_COLLECTION_NAME = "Bases"
    GROUPS_COLLECTION_NAME = "Groups"
    ANSWERS_COLLECTION_NAME = "Answers"

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

    @property
    def _answers_collection(self) -> Collection:
        return self._db.get_collection(self.ANSWERS_COLLECTION_NAME)

    def get_or_create_base(
        self, dto: Union[QABaseDTO, UUID], session: ClientSession = None
    ) -> QABase:
        if isinstance(dto, UUID):
            return self.get_base_by_id(dto, session)
        doc = self._bases_collection.find_one_and_update(
            filter={"question": dto.question, "type": dto.type},
            update={"$setOnInsert": {"id": uuid4()}},
            upsert=True,
            return_document=ReturnDocument.AFTER,
            session=session,
        )
        return QABase.parse_obj(doc)

    def get_or_create_group(
        self,
        dto: Union[QAGroupDTO, UUID, None],
        base_id: UUID,
        session: ClientSession = None,
    ) -> Optional[QAGroup]:
        if dto is None:
            return None
        if isinstance(dto, UUID):
            return self.get_group_by_id(dto, session=session)

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
            return QAGroup.parse_obj(doc[0])
        else:
            group = QAGroup(
                all_answers=dto.all_answers,
                all_extra=dto.all_extra,
                base_id=base_id,
            )
            self._groups_collection.insert_one(
                group.dict(),
                session=session,
            )
            return group

    def get_or_create_qa(
        self, dto: QAAnswerDTO, session: ClientSession = None
    ) -> Tuple[QAAnswer, bool]:
        base = self.get_or_create_base(dto.base, session=session)
        group = self.get_or_create_group(dto.group, base.id, session=session)
        self.validate_answer_in_group(base, dto, group)

        doc = list(
            self._answers_collection.aggregate(
                pipeline=[
                    {
                        "$match": {
                            "base_id": base.id,
                            "group_id": group.id if group else None,
                            "is_correct": dto.is_correct,
                        }
                    },
                    (
                        {"$match": {"$expr": {"$setEquals": ["$answer", dto.answer]}}}
                        if base.type == QATypeEnum.MultipleChoice
                        else {"$match": {"answer": dto.answer}}
                    ),
                ],
                session=session,
            )
        )
        if doc:
            return (QAAnswer.parse_obj(doc[0]), False)
        else:
            id = uuid4()
            self._answers_collection.insert_one(
                {
                    "id": id,
                    "base_id": base.id,
                    "group_id": group.id if group else None,
                    "answer": dto.answer,
                    "is_correct": dto.is_correct,
                },
                session=session,
            )
            return (
                QAAnswer(
                    id=id,
                    base_id=base.id,
                    group_id=group.id if group else None,
                    answer=dto.answer,
                    is_correct=dto.is_correct,
                ),
                True,
            )

    def add_group_to_answer(
        self, answer_id: UUID, group_id: UUID, session: ClientSession = None
    ):
        answer = self.get_answer_by_id(answer_id, session)
        group = self.get_group_by_id(group_id, session)
        if answer.base_id != group.base_id:
            raise QABasesDoNotMatch
        base = self.get_base_by_id(answer.base_id, session)
        self.validate_answer_in_group(base, answer, group)
        res = self._answers_collection.update_one(
            {"id": answer.id}, {"$set": {"group_id": group.id}}
        )
        if res.matched_count != 1 or res.modified_count != 1:
            raise QAStoreException

    def get_answer_by_id(
        self, answer_id: UUID, session: ClientSession = None
    ) -> QAAnswer:
        doc = self._answers_collection.find_one({"id": answer_id}, session=session)
        if doc is None:
            raise QAAnswerNotExist
        return QAAnswer.parse_obj(doc)

    def get_group_by_id(
        self, answer_id: UUID, session: ClientSession = None
    ) -> QAGroup:
        doc = self._groups_collection.find_one({"id": answer_id}, session=session)
        if doc is None:
            raise QAGroupNotExist
        return QAGroup.parse_obj(doc)

    def get_base_by_id(self, base_id: UUID, session: ClientSession = None) -> QABase:
        doc = self._bases_collection.find_one({"id": base_id}, session)
        if doc is None:
            raise QABaseNotExist
        return QABase.parse_obj(doc)
