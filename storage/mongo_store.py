from typing import Optional, Tuple
from uuid import UUID, uuid4

from pydantic import BaseSettings
from pymongo import MongoClient
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
from storage.db_models import DBDTO, QAAnswer, QABase, QAGroup
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO, QATypeEnum


class MongoSettings(BaseSettings):
    url: str = ""
    db_name: str = ""

    class Config:
        env_prefix = "qa_storage_"


class MongoStore(AbstractStore):
    def __init__(self, settings: MongoSettings) -> None:
        self._client = MongoClient(host=settings.url, uuidRepresentation="standard")
        self._db_name = settings.db_name
        self._db = self._client.get_database(self._db_name)

    # Base
    BASES_COLLECTION_NAME = "Bases"

    @property
    def _bases_collection(self) -> Collection:
        return self._db.get_collection(self.BASES_COLLECTION_NAME)

    def get_base_by_id(
        self, base_id: UUID, db_dto: DBDTO = None, session: ClientSession = None
    ) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        doc = self._bases_collection.find_one({"id": base_id}, session)
        if doc:
            db_dto.base = QABase.parse_obj(doc)
        return db_dto

    def get_base(
        self, dto: QABaseDTO, db_dto: DBDTO = None, session: ClientSession = None
    ) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        doc = self._bases_collection.find_one(
            {"question": dto.question, "type": dto.type}, session=session
        )
        if doc:
            db_dto.base = QABase.parse_obj(doc)
        return db_dto

    def create_base(
        self, dto: QABaseDTO, db_dto: DBDTO = None, session: ClientSession = None
    ) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        base = QABase(question=dto.question, type=dto.type)
        db_dto.base = base
        db_dto.validate_base()
        self._bases_collection.insert_one(db_dto.base.dict(), session=session)
        return db_dto

    # Group
    # GROUPS_COLLECTION_NAME = "Groups"

    # @property
    # def _groups_collection(self) -> Collection:
    #     return self._db.get_collection(self.GROUPS_COLLECTION_NAME)

    # def get_group_by_id(self, group_id: UUID, session: ClientSession = None) -> QAGroup:
    #     doc = self._groups_collection.find_one({"id": group_id}, session=session)
    #     if doc is None:
    #         raise QAGroupNotExist
    #     return QAGroup.parse_obj(doc)

    # def get_group(
    #     self,
    #     dto: QAGroupDTO,
    #     base_id: UUID,
    #     base: QABase = None,
    #     session: ClientSession = None,
    # ) -> Optional[QAGroup]:
    #     if base is None:
    #         base = self.get_base_by_id(base_id, session=session)
    #     doc = list(
    #         self._groups_collection.aggregate(
    #             pipeline=[
    #                 {"$match": {"base_id": base_id}},
    #                 {
    #                     "$match": {
    #                         "$expr": {"$setEquals": ["$all_answers", dto.all_answers]}
    #                     }
    #                 },
    #                 {
    #                     "$match": {
    #                         "$expr": {"$setEquals": ["$all_extra", dto.all_extra]}
    #                     }
    #                 },
    #             ],
    #             session=session,
    #         )
    #     )
    #     if doc:
    #         return QAGroup.parse_obj(doc[0])
    #     else:
    #         return None

    # def create_group(
    #     self,
    #     dto: QAGroupDTO,
    #     base_id: UUID,
    #     base: QABase = None,
    #     session: ClientSession = None,
    # ) -> QAGroup:
    #     if base is None:
    #         base = self.get_base_by_id(base_id, session=session)
    #     group = QAGroup(
    #         all_answers=dto.all_answers, all_extra=dto.all_extra, base_id=base_id
    #     )
    #     self._groups_collection.insert_one(group.dict(), session=session)
    #     return group

    # def get_or_create_qa(
    #     self, dto: QAAnswerDTO, session: ClientSession = None
    # ) -> Tuple[QAAnswer, bool]:
    #     base = self.get_or_create_base(dto.base, session=session)
    #     group = self.get_or_create_group(dto.group, base.id, session=session)
    #     self.validate_answer_in_group(base, dto, group)

    #     doc = list(
    #         self._answers_collection.aggregate(
    #             pipeline=[
    #                 {
    #                     "$match": {
    #                         "base_id": base.id,
    #                         "group_id": group.id if group else None,
    #                         "is_correct": dto.is_correct,
    #                     }
    #                 },
    #                 (
    #                     {"$match": {"$expr": {"$setEquals": ["$answer", dto.answer]}}}
    #                     if base.type == QATypeEnum.MultipleChoice
    #                     else {"$match": {"answer": dto.answer}}
    #                 ),
    #             ],
    #             session=session,
    #         )
    #     )
    #     if doc:
    #         return (QAAnswer.parse_obj(doc[0]), False)
    #     else:
    #         id = uuid4()
    #         self._answers_collection.insert_one(
    #             {
    #                 "id": id,
    #                 "base_id": base.id,
    #                 "group_id": group.id if group else None,
    #                 "answer": dto.answer,
    #                 "is_correct": dto.is_correct,
    #             },
    #             session=session,
    #         )
    #         return (
    #             QAAnswer(
    #                 id=id,
    #                 base_id=base.id,
    #                 group_id=group.id if group else None,
    #                 answer=dto.answer,
    #                 is_correct=dto.is_correct,
    #             ),
    #             True,
    #         )

    # def add_group_to_answer(
    #     self, answer_id: UUID, group_id: UUID, session: ClientSession = None
    # ):
    #     answer = self.get_answer_by_id(answer_id, session)
    #     group = self.get_group_by_id(group_id, session)
    #     if answer.base_id != group.base_id:
    #         raise QABasesDoNotMatch
    #     base = self.get_base_by_id(answer.base_id, session)
    #     self.validate_answer_in_group(base, answer, group)
    #     res = self._answers_collection.update_one(
    #         {"id": answer.id}, {"$set": {"group_id": group.id}}
    #     )
    #     if res.matched_count != 1 or res.modified_count != 1:
    #         raise QAStoreException

    # # Answer
    # ANSWERS_COLLECTION_NAME = "Answers"

    # @property
    # def _answers_collection(self) -> Collection:
    #     return self._db.get_collection(self.ANSWERS_COLLECTION_NAME)

    # def get_answer_by_id(
    #     self, answer_id: UUID, session: ClientSession = None
    # ) -> QAAnswer:
    #     doc = self._answers_collection.find_one({"id": answer_id}, session=session)
    #     if doc is None:
    #         raise QAAnswerNotExist
    #     return QAAnswer.parse_obj(doc)

    # def get_answer(
    #     self,
    #     dto: QAAnswerDTO,
    #     base_id: UUID,
    #     group_id: Optional[UUID],
    #     base: QABase = None,
    #     group: Optional[QAGroup] = None,
    #     session: ClientSession = None,
    # ) -> Optional[QAAnswer]:
    #     if base is None:
    #         base = self.get_base_by_id(base_id, session=session)
    #     if group is None:
    #         if group_id is not None:
    #             group = self.get_group_by_id(group_id, session=session)
    #     doc = self._answers_collection.aggregate(
    #         [
    #             {
    #                 "$match": {
    #                     "base_id": base.id,
    #                     "group_id": group.id if group else None,
    #                     "is_correct": dto.is_correct,
    #                 }
    #             },
    #             (
    #                 {"$match": {"$expr": {"$setEquals": ["$answer", dto.answer]}}}
    #                 if base.type == QATypeEnum.MultipleChoice
    #                 else {"$match": {"answer": dto.answer}}
    #             ),
    #         ],
    #         session=session,
    #     )
    #     if doc:
    #         return QAAnswer.parse_obj(doc[0])
    #     else:
    #         return None

    # def create_answer(
    #     self,
    #     dto: QAAnswerDTO,
    #     base_id: UUID,
    #     group_id: Optional[UUID],
    #     base: QABase = None,
    #     group: Optional[QAGroup] = None,
    #     session: ClientSession = None,
    # ) -> QAAnswer:
    #     if base is None:
    #         base = self.get_base_by_id(base_id, session=session)
    #     if group is None:
    #         if group_id is not None:
    #             group = self.get_group_by_id(group_id, session=session)
    #     answer = QAAnswer(
    #         base_id=base_id,
    #         group_id=group_id,
    #         answer=dto.answer,
    #         is_correct=dto.is_correct,
    #     )
    #     self._answers_collection.insert_one(answer.dict(), session=session)
    #     return answer
