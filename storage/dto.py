from enum import Enum
from typing import Union
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


class QAEmptyGroupDTO:
    ...


class QAAnswerDTO(BaseModel):
    answer: ConStrList
    is_correct: bool


class QADTO(BaseModel):
    base: Union[UUID, QABaseDTO]
    group: Union[None, UUID, QAGroupDTO]
    answer: Union[UUID, QAAnswerDTO]
