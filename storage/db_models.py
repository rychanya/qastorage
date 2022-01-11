from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from storage.dto import ConStr, QATypeEnum


class QABase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: QATypeEnum
    question: ConStr


class QAGroup(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    base_id: UUID
    all_answers: list[ConStr]
    all_extra: list[ConStr] = []


class QAAnswer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    base_id: UUID
    group_id: Optional[UUID]
    answer: list[ConStr]
    is_correct: bool
