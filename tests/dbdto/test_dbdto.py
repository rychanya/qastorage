from typing import Union
from uuid import uuid4

import pytest

from storage.db_models import DBDTO, QAAnswer, QABase, QAEmptyGroup, QAGroup, QATypeEnum

base_id = uuid4()


def test_create_db_dto(base_or_none, group_or_none, answer_or_none):
    dto = DBDTO(base=base_or_none, group=group_or_none, answer=answer_or_none)
    if base_or_none is None:
        assert dto.is_base_loaded is False
        with pytest.raises(ValueError):
            dto.base
    else:
        assert dto.is_base_loaded is True
        assert dto.base == base_or_none
        del dto.base
        assert dto.is_base_loaded is False
        with pytest.raises(ValueError):
            dto.base

    if group_or_none is None:
        assert dto.is_group_loaded is False
        with pytest.raises(ValueError):
            dto.group
    else:
        assert dto.is_group_loaded is True
        assert dto.group == group_or_none
        del dto.group
        assert dto.is_group_loaded is False
        with pytest.raises(ValueError):
            dto.group

    if answer_or_none is None:
        assert dto.is_answer_loaded is False
        with pytest.raises(ValueError):
            dto.answer
    else:
        assert dto.is_answer_loaded is True
        assert dto.answer == answer_or_none
        del dto.answer
        assert dto.is_answer_loaded is False
        with pytest.raises(ValueError):
            dto.answer


def test_base_setter(base_or_none):
    dto = DBDTO()

    if base_or_none is None:
        with pytest.raises(ValueError):
            dto.base = base_or_none
    else:
        assert dto.is_base_loaded is False
        dto.base = base_or_none
        assert dto.is_base_loaded is True


def test_group_setter(group_or_none):
    dto = DBDTO()

    if group_or_none is None:
        with pytest.raises(ValueError):
            dto.group = group_or_none
    else:
        assert dto.is_group_loaded is False
        dto.group = group_or_none
        assert dto.is_group_loaded is True


def test_answer_setter(answer_or_none):
    dto = DBDTO()

    if answer_or_none is None:
        with pytest.raises(ValueError):
            dto.answer = answer_or_none
    else:
        assert dto.is_answer_loaded is False
        dto.answer = answer_or_none
        assert dto.is_answer_loaded is True


def test_base_validate():
    db_dto = DBDTO()
    with pytest.raises(ValueError):
        db_dto.validate_base()

    db_dto.base = QABase(type=QATypeEnum.OnlyChoice, question="question")
    assert db_dto.validate_base()


@pytest.mark.parametrize(
    "group_dict, type, raised",
    [
        ({"all_answers": ["1", "2"], "all_extra": []}, QATypeEnum.OnlyChoice, False),
        ({"all_answers": ["1", "2"], "all_extra": ["5"]}, QATypeEnum.OnlyChoice, True),
        ({"all_answers": ["1", "2"], "all_extra": ["5", "6"]}, QATypeEnum.MatchingChoice, False),
        ({"all_answers": ["1", "2"], "all_extra": ["5", "6", "7"]}, QATypeEnum.MatchingChoice, True),
    ],
)
def test_group_validate(group_dict: dict, type: QATypeEnum, raised: bool):
    db_dto = DBDTO()
    db_dto.base = QABase(type=type, question="question")
    group = QAGroup(base_id=db_dto.base.id, **group_dict)
    db_dto.group = group

    if raised:
        with pytest.raises(ValueError):
            db_dto.validate_group()
    else:
        assert db_dto.validate_group()


def test_empty_group_validate():
    db_dto = DBDTO()
    db_dto.base = QABase(type=QATypeEnum.OnlyChoice, question="question")
    db_dto.group = QAEmptyGroup()

    assert isinstance(db_dto.validate_group(), QAEmptyGroup)


def test_incorrect_id_group_validate():
    db_dto = DBDTO()
    db_dto.base = QABase(type=QATypeEnum.OnlyChoice, question="question")
    db_dto.group = QAGroup(base_id=uuid4(), all_answers=["1", "2"])
    assert db_dto.base.id != db_dto.group.base_id

    with pytest.raises(ValueError):
        db_dto.validate_group()


def test_normal_validate(base: QABase, group: Union[QAGroup, QAEmptyGroup], answer: QAAnswer):
    dto = DBDTO(base=base, group=group, answer=answer)
    dto.validate_base()
    dto.validate_group()
    dto.validate_answer()


def test_answer_validate_base_id_not_equals(base: QABase, group: Union[QAGroup, QAEmptyGroup], answer: QAAnswer):
    dto = DBDTO(base=base, group=group, answer=answer)
    dto.base.id = uuid4()
    assert dto.base.id != dto.answer.base_id
    with pytest.raises(ValueError):
        dto.validate_answer()


def test_answer_validate_incorrect(base: QABase, group: Union[QAGroup, QAEmptyGroup], answer: QAAnswer):
    dto0 = DBDTO(
        base=base.copy(), group=group.copy() if isinstance(group, QAGroup) else QAEmptyGroup(), answer=answer.copy()
    )
    if dto0.base.type == QATypeEnum.OnlyChoice:
        dto0.answer.answer.append("wrong answer1")
        assert len(dto0.answer.answer) != 1
        with pytest.raises(ValueError):
            print(dto0.base, dto0.group, dto0.answer)
            dto0.validate_answer()
    if dto0.base.type == QATypeEnum.RangingChoice or dto0.base.type == QATypeEnum.MatchingChoice:
        dto0.answer.answer = ["wrong answer1"]
        assert len(dto0.answer.answer)
        with pytest.raises(ValueError):
            print(dto0.base, dto0.group, dto0.answer)
            dto0.validate_answer()

    if isinstance(group, QAEmptyGroup):
        return

    dto1 = DBDTO(base=base.copy(), group=group.copy(), answer=answer.copy())
    assert isinstance(dto1.group, QAGroup)
    dto1.group.id = uuid4()
    assert dto1.group.id != dto1.answer.group_id
    with pytest.raises(ValueError):
        dto1.validate_answer()

    dto2 = DBDTO(base=base.copy(), group=QAEmptyGroup(), answer=answer.copy())
    assert isinstance(dto2.group, QAEmptyGroup)
    assert dto2.answer.group_id
    with pytest.raises(ValueError):
        dto2.validate_answer()

    dto3 = DBDTO(base=base.copy(), group=group.copy(), answer=answer.copy())
    dto3.answer.group_id = None
    assert not isinstance(dto3.group, QAEmptyGroup)
    with pytest.raises(ValueError):
        dto3.validate_answer()

    dto4 = DBDTO(base=base.copy(), group=group.copy(), answer=answer.copy())
    assert isinstance(dto4.group, QAGroup)
    if dto4.base.type == QATypeEnum.OnlyChoice or dto4.base.type == QATypeEnum.MultipleChoice:
        dto4.answer.answer = ["wrong answer1"]
        assert not set(dto4.answer.answer).issubset(dto4.group.all_answers)
    if dto4.base.type == QATypeEnum.MatchingChoice or dto4.base.type == QATypeEnum.RangingChoice:
        dto4.answer.answer.append("wrong answer1")
        assert set(dto4.answer.answer) != set(dto4.group.all_answers)
    with pytest.raises(ValueError):
        dto4.validate_answer()
