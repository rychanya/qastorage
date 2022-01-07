from typing import Any, ContextManager, Optional, Protocol, Union
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
    def __call__(
        self,
        store: AbstractStore,
        data: Union[dict, tuple[dict, dict, Optional[dict]]],
        **kwds: Any
    ) -> None:
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
        {"question": "question", "type": QATypeEnum.OnlyChoice},
        None,
    )
]
