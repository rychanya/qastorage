from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from storage.dto import ConStr, QATypeEnum


class QABase(BaseModel):
    question: ConStr
    type: QATypeEnum
    id: UUID


class QAGroup(BaseModel):
    all_answers: list[ConStr]
    all_extra: list[ConStr] = []
    base_id: UUID
    id: UUID


class QAAnswer(BaseModel):
    id: UUID
    base_id: UUID
    group_id: Optional[UUID]
    answer: list[ConStr]
    is_correct: bool
