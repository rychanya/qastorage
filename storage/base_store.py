import abc
from typing import Optional, Union
from uuid import UUID

from storage.db_models import DBDTO, QAEmptyGroup, QAGroup
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO


class AbstractStore(abc.ABC):
    # Base
    def get_or_create_base(self, dto: Union[QABaseDTO, UUID], db_dto: DBDTO = None, **kwargs) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.base
        if isinstance(dto, UUID):
            self.get_base_by_id(dto, db_dto, **kwargs)
        else:
            self.get_base(dto, db_dto, **kwargs)
            if not db_dto.is_base_loaded:
                self.create_base(dto, db_dto, **kwargs)
        db_dto.validate_base()
        return db_dto

    @abc.abstractmethod
    def get_base_by_id(self, base_id: UUID, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_base(self, dto: QABaseDTO, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def create_base(self, dto: QABaseDTO, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    # Group
    def get_or_create_group(self, dto: Union[QAGroupDTO, UUID, None], db_dto: DBDTO = None, **kwargs) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.group
        if isinstance(dto, UUID):
            self.get_group_by_id(dto, db_dto=db_dto, **kwargs)
            if isinstance(db_dto.group, QAGroup) and not db_dto.is_base_loaded:
                self.get_base_by_id(db_dto.group.base_id, db_dto=db_dto, **kwargs)
        else:
            self.get_group(dto, db_dto=db_dto, **kwargs)
            if not db_dto.is_group_loaded and dto:
                self.create_group(dto, db_dto=db_dto, **kwargs)
        db_dto.validate_group()
        return db_dto

    @abc.abstractmethod
    def get_group_by_id(self, group_id: UUID, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_group(self, dto: Optional[QAGroupDTO], db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def create_group(self, dto: QAGroupDTO, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    # Answer
    def get_or_create_answer(self, dto: Union[UUID, QAAnswerDTO], db_dto: DBDTO = None, **kwargs) -> DBDTO:
        if db_dto is None:
            db_dto = DBDTO()
        else:
            del db_dto.answer
        if isinstance(dto, UUID):
            self.get_answer_by_id(dto, db_dto=db_dto, **kwargs)
            if not db_dto.is_group_loaded:
                if db_dto.answer.group_id:
                    self.get_group_by_id(db_dto.answer.group_id, db_dto=db_dto, **kwargs)
                else:
                    db_dto.group = QAEmptyGroup()
            if not db_dto.is_base_loaded:
                self.get_base_by_id(db_dto.answer.base_id, db_dto=db_dto, **kwargs)
        else:
            self.get_answer(dto, db_dto=db_dto, **kwargs)
            if not db_dto.is_answer_loaded:
                self.create_answer(dto, db_dto=db_dto, **kwargs)
        db_dto.validate_answer()
        return db_dto

    @abc.abstractmethod
    def get_answer_by_id(self, answer_id: UUID, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_answer(self, dto: QAAnswerDTO, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def create_answer(self, dto: QAAnswerDTO, db_dto: DBDTO = None, **kwargs) -> DBDTO:  # pragma: no cover
        ...
