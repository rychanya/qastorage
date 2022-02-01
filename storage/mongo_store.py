from functools import wraps
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseSettings
from pymongo import MongoClient
from pymongo.client_session import ClientSession
from pymongo.collection import Collection

from storage.base_store import AbstractStore
from storage.db_models import DBDTO, QAAnswer, QABase, QAEmptyGroup, QAGroup, QATypeEnum
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO


def session_decorator(func):
    @wraps(func)
    def _session_decorator(self, *args, **kwargs):
        session = kwargs.get("session")
        if session is not None:
            return func(self, *args, **kwargs)
        else:
            with self._client.start_session() as session:
                with session.start_transaction():
                    return func(self, *args, session=session, **kwargs)

    return _session_decorator


class MongoSettings(BaseSettings):
    url: Optional[str] = None
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

    @session_decorator
    def get_or_create_base(
        self,
        dto: Union[QABaseDTO, UUID],
        db_dto: DBDTO = None,
        session: ClientSession = None,
    ) -> DBDTO:
        return super().get_or_create_base(dto, db_dto, session=session)

    @session_decorator
    def get_base_by_id(self, base_id: UUID, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        doc = self._bases_collection.find_one({"id": base_id}, session=session)
        if doc:
            db_dto.base = QABase.parse_obj(doc)
        return db_dto

    @session_decorator
    def get_base(self, dto: QABaseDTO, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        doc = self._bases_collection.find_one({"question": dto.question, "type": dto.type}, session=session)
        if doc:
            db_dto.base = QABase.parse_obj(doc)
        return db_dto

    @session_decorator
    def create_base(self, dto: QABaseDTO, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
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
    GROUPS_COLLECTION_NAME = "Groups"

    @property
    def _groups_collection(self) -> Collection:
        return self._db.get_collection(self.GROUPS_COLLECTION_NAME)

    @session_decorator
    def get_or_create_group(
        self, dto: Union[QAGroupDTO, UUID, None], db_dto: DBDTO = None, session: ClientSession = None
    ) -> DBDTO:
        return super().get_or_create_group(dto, db_dto, session=session)

    @session_decorator
    def get_group_by_id(self, group_id: UUID, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.group
        doc = self._groups_collection.find_one({"id": group_id}, session=session)
        if doc:
            db_dto.group = QAGroup.parse_obj(doc)
        return db_dto

    @session_decorator
    def get_group(self, dto: Optional[QAGroupDTO], db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.group
        if dto is None:
            db_dto.group = QAEmptyGroup()
            return db_dto
        pipeline = [
            {"$match": {"$expr": {"$setEquals": ["$all_answers", dto.all_answers]}}},
            {"$match": {"$expr": {"$setEquals": ["$all_extra", dto.all_extra]}}}
            if dto.all_extra
            else {"$match": {"all_extra": dto.all_extra}},
        ]
        if db_dto.is_base_loaded:
            pipeline = [{"$match": {"base_id": db_dto.base.id}}, *pipeline]
        docs = list(self._groups_collection.aggregate(pipeline=pipeline, session=session))
        if docs:
            db_dto.group = QAGroup.parse_obj(docs[0])
        if db_dto.is_group_loaded and isinstance(db_dto.group, QAGroup) and not db_dto.is_base_loaded:
            self.get_base_by_id(db_dto.group.base_id, db_dto=db_dto, session=session)
        return db_dto

    @session_decorator
    def create_group(self, dto: QAGroupDTO, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.group
        db_dto.validate_base()
        group = QAGroup(base_id=db_dto.base.id, all_answers=dto.all_answers, all_extra=dto.all_extra)
        db_dto.group = group
        db_dto.validate_group()
        if self._bases_collection.count_documents(db_dto.base.dict(), session=session) != 1:
            raise ValueError
        self._groups_collection.insert_one(db_dto.group.dict(), session=session)
        return db_dto

    # Answer
    ANSWERS_COLLECTION_NAME = "Answers"

    @property
    def _answers_collection(self) -> Collection:
        return self._db.get_collection(self.ANSWERS_COLLECTION_NAME)

    @session_decorator
    def get_or_create_answer(
        self, dto: Union[UUID, QAAnswerDTO], db_dto: DBDTO = None, session: ClientSession = None
    ) -> DBDTO:
        return super().get_or_create_answer(dto, db_dto, session=session)

    @session_decorator
    def get_answer_by_id(self, answer_id: UUID, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.answer
        doc = self._answers_collection.find_one({"id": answer_id}, session=session)
        if doc:
            db_dto.answer = QAAnswer.parse_obj(doc)
        return db_dto

    @session_decorator
    def get_answer(self, dto: QAAnswerDTO, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.answer
        doc = list(
            self._answers_collection.aggregate(
                [
                    {
                        "$match": {
                            "base_id": db_dto.base.id,
                            "group_id": db_dto.group.id if isinstance(db_dto.group, QAGroup) else None,
                            "is_correct": dto.is_correct,
                        }
                    },
                    (
                        {"$match": {"$expr": {"$setEquals": ["$answer", dto.answer]}}}
                        if db_dto.base.type == QATypeEnum.MultipleChoice
                        else {"$match": {"answer": dto.answer}}
                    ),
                ],
                session=session,
            )
        )
        if doc:
            db_dto.answer = QAAnswer.parse_obj(doc[0])
        return db_dto

    @session_decorator
    def create_answer(self, dto: QAAnswerDTO, db_dto: DBDTO = None, session: ClientSession = None) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.answer
        answer = QAAnswer(
            base_id=db_dto.base.id,
            group_id=db_dto.group.id if isinstance(db_dto.group, QAGroup) else None,
            answer=dto.answer,
            is_correct=dto.is_correct,
        )
        self._answers_collection.insert_one(answer.dict(), session=session)
        db_dto.answer = answer
        return db_dto
