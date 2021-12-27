from enum import Enum
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, constr

ConStr = constr(min_length=1, max_length=200)


class QATypeEnum(str, Enum):
    OnlyChoice = "Выберите один правильный вариант"
    MultipleChoice = "Выберите все правильные варианты"
    RangingChoice = "Перетащите варианты так, чтобы они оказались в правильном порядке"
    MatchingChoice = "Соедините соответствия справа с правильными вариантами"


class QABaseDTO(BaseModel):
    question: ConStr
    type: QATypeEnum


class QAGroupDTO(BaseModel):
    all_answers: list[ConStr]
    all_extra: list[ConStr] = []
    base_id: Optional[UUID]


class QAAnswerDTO(QABaseDTO):
    group: Union[None, UUID, QAGroupDTO]
    answer: list[ConStr]
    is_correct: bool
