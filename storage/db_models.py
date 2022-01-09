from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from storage.dto import ConStr, QATypeEnum


class QABase(BaseModel):
    question: ConStr
    type: QATypeEnum
    id: UUID = Field(default_factory=uuid4)


class QAGroup(BaseModel):
    all_answers: list[ConStr]
    all_extra: list[ConStr] = []
    base_id: UUID
    id: UUID = Field(default_factory=uuid4)


class QAAnswer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    base_id: UUID
    group_id: Optional[UUID]
    answer: list[ConStr]
    is_correct: bool
