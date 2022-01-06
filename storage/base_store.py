import abc
from typing import Tuple, Union
from uuid import UUID

from storage.db_models import QAAnswer, QABase, QAGroup
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO


class QABaseNotExist(Exception):
    ...


class QAGroupNotExist(Exception):
    ...


class QAAnswerValidation(Exception):
    ...


class AbstractStore(abc.ABC):
    @abc.abstractmethod
    def get_or_create_base(self, dto: Union[QABaseDTO, UUID], **kwargs) -> QABase:
        ...

    @abc.abstractmethod
    def get_or_create_group(
        self, dto: Union[QAGroupDTO, UUID], base_id: UUID, **kwargs
    ) -> QAGroup:
        ...

    @abc.abstractmethod
    def get_or_create_qa(self, dto: QAAnswerDTO, **kwargs) -> Tuple[QAAnswer, bool]:
        ...
