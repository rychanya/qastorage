from enum import Enum
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, conlist, constr

ConStr = constr(min_length=1, max_length=200)
ConStrList = conlist(ConStr, min_items=1)


class QATypeEnum(str, Enum):
    OnlyChoice = "Выберите один правильный вариант"
    MultipleChoice = "Выберите все правильные варианты"
    RangingChoice = "Перетащите варианты так, чтобы они оказались в правильном порядке"
    MatchingChoice = "Соедините соответствия справа с правильными вариантами"


class QABaseDTO(BaseModel):
    question: ConStr
    type: QATypeEnum


class QAGroupDTO(BaseModel):
    all_answers: ConStrList
    all_extra: list[ConStr] = []
    base_id: Optional[UUID]


class QAAnswerDTO(BaseModel):
    base: Union[UUID, QABaseDTO]
    group: Union[None, UUID, QAGroupDTO]
    answer: ConStrList
    is_correct: bool
