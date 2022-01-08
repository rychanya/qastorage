from typing import Any, ContextManager, Optional, Protocol
from uuid import uuid4

from storage.base_store import AbstractStore
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO, QATypeEnum


class GetStore(Protocol):
    def __call__(self) -> ContextManager[AbstractStore]:
        ...


class FindRaw(Protocol):
    def __call__(self, store: AbstractStore, **kwds: Any) -> Optional[dict]:
        ...


class InsertRaw(Protocol):
    def __call__(self, store: AbstractStore, data: dict, **kwds: Any) -> None:
        ...


class CountRaw(Protocol):
    def __call__(self, store: AbstractStore, **kwds: Any) -> None:
        ...


QABaseDTOs = [QABaseDTO(question="question", type=QATypeEnum.OnlyChoice)]
QABaseDicts = [{"question": "question", "type": QATypeEnum.OnlyChoice, "id": uuid4()}]

QAGroupDTOs = [QAGroupDTO(all_answers=["1", "2", "3", "4"])]
QAGroupDicts = [
    {
        "all_answers": ["1", "2", "3", "4"],
        "all_extra": [],
        "base_id": uuid4(),
        "id": uuid4(),
    }
]

QAAnswerDTOs = [
    QAAnswerDTO(
        base=QABaseDTO(question="question", type=QATypeEnum.OnlyChoice),
        group=None,
        answer=["answer"],
        is_correct=True,
    )
]

QAAnswerTuples = [
    (
        {"answer": ["answer"], "is_correct": True, "id": uuid4()},
        QABaseDTO(question="question", type=QATypeEnum.OnlyChoice),
        None,
    )
]

QAIncorrectAnswer = [
    QAAnswerDTO(
        base=QABaseDTO(question="question", type=QATypeEnum.OnlyChoice),
        group=QAGroupDTO(all_answers=["answer1", "answer2"]),
        answer=["answer1", "answer2"],
        is_correct=True,
    ),
    QAAnswerDTO(
        base=QABaseDTO(question="question", type=QATypeEnum.MultipleChoice),
        group=QAGroupDTO(all_answers=["answer1", "answer2"]),
        answer=["answer1", "answer3"],
        is_correct=True,
    ),
    QAAnswerDTO(
        base=QABaseDTO(question="question", type=QATypeEnum.RangingChoice),
        group=QAGroupDTO(all_answers=["answer1", "answer2"]),
        answer=["answer1", "answer3"],
        is_correct=True,
    ),
]


def qa_answer_tuple_to_dto(
    data: tuple[dict, QABaseDTO, Optional[QAGroupDTO]]
) -> QAAnswerDTO:
    answer, base, group = data
    return QAAnswerDTO.parse_obj(
        {
            "base": base.dict(),
            "group": group.dict if group else None,
            "answer": answer["answer"],
            "is_correct": answer["is_correct"],
        }
    )
