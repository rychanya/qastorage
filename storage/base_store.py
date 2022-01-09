import abc
from typing import Optional, Tuple, Union
from uuid import UUID

from storage.db_models import QAAnswer, QABase, QAGroup
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO, QATypeEnum


class QAStoreException(Exception):
    ...


class QABaseNotExist(Exception):
    ...


class QAGroupNotExist(Exception):
    ...


class QAAnswerNotExist(Exception):
    ...


class QAAnswerValidation(Exception):
    ...


class QABasesDoNotMatch(Exception):
    ...


class AbstractStore(abc.ABC):
    @abc.abstractmethod
    def get_or_create_base(
        self, dto: Union[QABaseDTO, UUID], **kwargs
    ) -> QABase:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_or_create_group(
        self, dto: Union[QAGroupDTO, UUID, None], base_id: UUID, **kwargs
    ) -> QAGroup:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_or_create_qa(
        self, dto: QAAnswerDTO, **kwargs
    ) -> Tuple[QAAnswer, bool]:  # pragma: no cover
        ...

    @abc.abstractmethod
    def add_group_to_answer(
        self, answer_id: UUID, group_id: UUID, **kwargs
    ):  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_answer_by_id(
        self, answer_id: UUID, **kwargs
    ) -> QAAnswer:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_group_by_id(self, group_id: UUID, **kwargs) -> QAGroup:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_base_by_id(self, base_id: UUID, **kwargs) -> QABase:  # pragma: no cover
        ...

    def validate_answer_in_group(
        self,
        base: QABase,
        answer: Union[QAAnswer, QAAnswerDTO],
        group: Optional[QAGroup],
    ):
        if group is None:
            return

        if base.type == QATypeEnum.OnlyChoice:
            if len(answer.answer) != 1 or answer.answer[0] not in group.all_answers:
                raise QAAnswerValidation

        if base.type == QATypeEnum.MultipleChoice:
            if not set(answer.answer).issubset(group.all_answers):
                raise QAAnswerValidation

        if (
            base.type == QATypeEnum.RangingChoice
            or base.type == QATypeEnum.MatchingChoice
        ):
            if set(answer.answer) != set(group.all_answers):
                raise QAAnswerValidation
