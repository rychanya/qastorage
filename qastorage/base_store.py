import abc
from typing import Tuple, Union
from uuid import UUID

from qastorage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO


class QABaseNotExist(Exception):
    ...


class AbstractStore(abc.ABC):
    @abc.abstractmethod
    def get_or_create_base(self, dto: Union[QABaseDTO, UUID], **kwargs) -> UUID:
        ...

    @abc.abstractmethod
    def get_or_create_group(
        self, dto: Union[QAGroupDTO, UUID], base_id: UUID, **kwargs
    ) -> UUID:
        ...

    @abc.abstractmethod
    def get_or_create_qa(self, dto: QAAnswerDTO, **kwargs) -> Tuple[UUID, bool]:
        ...
