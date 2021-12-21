from pydantic import BaseModel, constr
from enum import Enum

ConStr = constr(min_length=1, max_length=200)

class QATypeEnum(str, Enum):
    OnlyChoice = "Выберите один правильный вариант"
    MultipleChoice = "Выберите все правильные варианты"
    RangingChoice = "Перетащите варианты так, чтобы они оказались в правильном порядке"
    MatchingChoice = "Соедините соответствия справа с правильными вариантами"

class BaseDTO(BaseModel):
    question: ConStr
    type: QATypeEnum