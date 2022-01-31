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
    if base is not None and group is not None and answer is not None:
        dto.validate_base()
        dto.validate_group()
        dto.validate_answer()
