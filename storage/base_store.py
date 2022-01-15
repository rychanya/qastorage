import abc
from typing import Optional, Tuple, Union
from uuid import UUID

from storage.db_models import DBDTO, QAAnswer, QABase, QAGroup
from storage.dto import QADTO, QAAnswerDTO, QABaseDTO, QAGroupDTO, QATypeEnum


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
    # Base
    def get_or_create_base(
        self, dto: Union[QABaseDTO, UUID], db_dto: DBDTO = None, **kwargs
    ) -> DBDTO:
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
    def get_base_by_id(
        self, base_id: UUID, db_dto: DBDTO = None, **kwargs
    ) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def get_base(
        self, dto: QABaseDTO, db_dto: DBDTO = None, **kwargs
    ) -> DBDTO:  # pragma: no cover
        ...

    @abc.abstractmethod
    def create_base(
        self, dto: QABaseDTO, db_dto: DBDTO = None, **kwargs
    ) -> DBDTO:  # pragma: no cover
        ...

    # Group
    # def get_or_create_group(
    #     self,
    #     dto: Union[QAGroupDTO, UUID, None],
    #     base_id: UUID,
    #     db_dto: DBDTO = None,
    #     **kwargs
    # ) -> DBDTO:
    #     if db_dto is None:
    #         db_dto = DBDTO()
    #     if not db_dto.is_base_loaded:
    #         self.get_base_by_id(base_id=base_id, db_dto=db_dto, *kwargs)
    #     if dto is None:
    #         db_dto.group = None
    #         return db_dto
    #     if isinstance(dto, UUID):
    #         self.get_group_by_id(dto, db_dto, **kwargs)
    #         if db_dto.base and db_dto.base.id != base_id:
    #             raise QABasesDoNotMatch
    #         return db_dto
    #     self.get_group(dto, base_id, db_dto, **kwargs)
    #     if db_dto.is_group_loaded:
    #         return db_dto
    #     else:
    #         return self.create_group(dto, base_id, db_dto, **kwargs)

    # @abc.abstractmethod
    # def get_group_by_id(
    #     self, group_id: Optional[UUID], db_dto: DBDTO = None, **kwargs
    # ) -> DBDTO:  # pragma: no cover
    #     ...

    # @abc.abstractmethod
    # def get_group(
    #     self, dto: QAGroupDTO, base_id: UUID, db_dto: DBDTO = None, **kwargs
    # ) -> DBDTO:  # pragma: no cover
    #     ...

    # @abc.abstractmethod
    # def create_group(
    #     self, dto: QAGroupDTO, base_id: UUID, db_dto: DBDTO = None, **kwargs
    # ) -> DBDTO:  # pragma: no cover
    #     ...

    # # Answer
    # def get_or_create_answer(
    #     self,
    #     dto: Union[UUID, QAAnswer],
    #     base_id: UUID,
    #     group_id: Optional[UUID],
    #     db_dto:DBDTO=None,
    #     **kwargs
    # ) -> DBDTO:
    #     if db_dto is None:
    #         db_dto = DBDTO()
    #     if not db_dto.is_base_loaded:
    #         self.get_base_by_id(base_id, db_dto, **kwargs)
    #     if not db_dto.is_group_loaded:
    #         self.get_group_by_id(group_id, db_dto, **kwargs)
    #     if isinstance(dto, UUID):
    #         self.get_answer_by_id(dto, db_dto, **kwargs)

    # @abc.abstractmethod
    # def get_answer_by_id(
    #     self, answer_id: UUID, db_dto:DBDTO=None, **kwargs
    # ) -> DBDTO:  # pragma: no cover
    #     ...

    # @abc.abstractmethod
    # def get_answer(
    #     self,
    #     dto: QAAnswerDTO,
    #     base_id: UUID,
    #     group_id: Optional[UUID],
    #     db_dto:DBDTO=None,
    #     **kwargs
    # ) -> DBDTO:  # pragma: no cover
    #     ...

    # @abc.abstractmethod
    # def create_answer(
    #     self,
    #     dto: QAAnswerDTO,
    #     base_id: UUID,
    #     group_id: Optional[UUID],
    #     db_dto:DBDTO=None,
    #     **kwargs
    # ) -> QAAnswer:  # pragma: no cover
    #     ...

    # # qa
    # @abc.abstractmethod
    # def get_or_create_qa(
    #     self, dto: QAAnswerDTO, **kwargs
    # ) -> Tuple[QAAnswer, bool]:  # pragma: no cover
    #     ...

    # @abc.abstractmethod
    # def add_group_to_answer(
    #     self, answer_id: UUID, group_id: UUID, **kwargs
    # ):  # pragma: no cover
    #     ...

    # def validate_answer_in_group(
    #     self,
    #     base: QABase,
    #     answer: Union[QAAnswer, QAAnswerDTO],
    #     group: Optional[QAGroup],
    # ):
    #     if group is None:
    #         return

    #     if base.type == QATypeEnum.OnlyChoice:
    #         if len(answer.answer) != 1 or answer.answer[0] not in group.all_answers:
    #             raise QAAnswerValidation

    #     if base.type == QATypeEnum.MultipleChoice:
    #         if not set(answer.answer).issubset(group.all_answers):
    #             raise QAAnswerValidation

    #     if (
    #         base.type == QATypeEnum.RangingChoice
    #         or base.type == QATypeEnum.MatchingChoice
    #     ):
    #         if set(answer.answer) != set(group.all_answers):
    #             raise QAAnswerValidation
