from typing import Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from storage.dto import ConStr, QATypeEnum


class QABase(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: QATypeEnum
    question: ConStr


class QAGroup(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    base_id: UUID
    all_answers: list[ConStr]
    all_extra: list[ConStr] = []


class QAEmptyGroup:
    ...


class QAAnswer(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    base_id: UUID
    group_id: Optional[UUID]
    answer: list[ConStr]
    is_correct: bool


class DBDTO:
    def __init__(
        self,
        base: QABase = None,
        group: Union[QAGroup, QAEmptyGroup] = None,
        answer: QAAnswer = None,
    ) -> None:
        if base is None:
            self._base = None
            self._base_loaded = False
        else:
            self._base = base
            self._base_loaded = True

        if group is None:
            self._group = None
            self._group_loaded = False
        else:
            self._group = group
            self._group_loaded = True

        if answer is None:
            self._answer = None
            self._answer_loaded = False
        else:
            self._answer = answer
            self._answer_loaded = True

    @property
    def is_base_loaded(self):
        return self._base_loaded

    @property
    def is_group_loaded(self):
        return self._group_loaded

    @property
    def is_answer_loaded(self):
        return self._answer_loaded

    @property
    def base(self) -> QABase:
        if self._base_loaded and self._base:
            return self._base
        else:
            raise ValueError

    @base.setter
    def base(self, v: QABase):
        if not isinstance(v, QABase):
            raise ValueError
        self._base = v
        self._base_loaded = True

    @base.deleter
    def base(self):
        self._base = None
        self._base_loaded = False

    @property
    def group(self) -> Union[QAGroup, QAEmptyGroup]:
        if self._group_loaded and self._group:
            return self._group
        else:
            raise ValueError

    @group.setter
    def group(self, v: Union[QAGroup, QAEmptyGroup]):
        if not isinstance(v, (QAGroup, QAEmptyGroup)):
            raise ValueError
        self._group = v
        self._group_loaded = True

    @group.deleter
    def group(self):
        self._group = None
        self._group_loaded = False

    @property
    def answer(self) -> QAAnswer:
        if self._answer_loaded and self._answer:
            return self._answer
        else:
            raise ValueError

    @answer.setter
    def answer(self, v: QAAnswer):
        if not isinstance(v, QAAnswer):
            raise ValueError
        self._answer = v
        self._answer_loaded = True

    @answer.deleter
    def answer(self):
        self._answer = None
        self._answer_loaded = False

    def validate_base(self) -> QABase:
        return self.base

    def validate_group(self) -> Union[QAGroup, QAEmptyGroup]:
        base = self.validate_base()
        group = self.group
        if isinstance(group, QAEmptyGroup):
            return group
        if base.id != group.base_id:
            raise ValueError
        if base.type != QATypeEnum.MatchingChoice and group.all_extra != []:
            raise ValueError
        if base.type == QATypeEnum.MatchingChoice and len(group.all_answers) != len(group.all_extra):
            raise ValueError
        return group

    def validate_answer(self) -> QAAnswer:
        self.validate_group()
        answer = self.answer
        if self.base.id != answer.base_id:
            raise ValueError
        if answer.group_id:
            if not isinstance(self.group, QAGroup) or self.group.id != answer.group_id:
                raise ValueError
        elif not isinstance(self.group, QAEmptyGroup):
            raise ValueError

        if self.base.type == QATypeEnum.OnlyChoice and len(answer.answer) != 1:
            raise ValueError
        if (self.base.type == QATypeEnum.MatchingChoice or self.base.type == QATypeEnum.RangingChoice) and len(
            answer.answer
        ) < 2:
            raise ValueError

        if isinstance(self.group, QAGroup):
            if self.base.type == QATypeEnum.OnlyChoice or self.base.type == QATypeEnum.MultipleChoice:
                if not set(answer.answer).issubset(self.group.all_answers):
                    raise ValueError
            if self.base.type == QATypeEnum.MatchingChoice or self.base.type == QATypeEnum.RangingChoice:
                if set(answer.answer) != set(self.group.all_answers):
                    raise ValueError

        return self.answer
