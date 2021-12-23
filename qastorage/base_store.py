import abc
from uuid import UUID

from qastorage.dto import BaseDTO


class AbstractStore(abc.ABC):
    @abc.abstractmethod
    def get_or_create_base(self, dto: BaseDTO, **kwargs) -> UUID:
        ...
