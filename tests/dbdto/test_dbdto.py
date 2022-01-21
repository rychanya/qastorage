import random
from typing import Optional, Union
from uuid import uuid4

import pytest
from _pytest.fixtures import FixtureRequest as _FixtureRequest

from storage.db_models import (
    DBDTO,
    ConStr,
    QAAnswer,
    QABase,
    QAEmptyGroup,
    QAGroup,
    QATypeEnum,
)

base_id = uuid4()


class FixtureRequest(_FixtureRequest):
    param: Union[QAEmptyGroup, None, str, list[ConStr], bool]


@pytest.fixture(params=[None, *list(QATypeEnum)])
def base(request: FixtureRequest):
    if request.param is None:
        return None
    else:
        assert isinstance(request.param, QATypeEnum)
        return QABase(type=request.param, question="question")


@pytest.fixture(params=[None, QAEmptyGroup(), ["1", "2", "3"]])
def group(request: FixtureRequest, base: Optional[QABase]):
    if base is None:
        return None
    if request.param is None:
        return None
    elif isinstance(request.param, QAEmptyGroup):
        return request.param
    else:
        assert isinstance(request.param, list)
        QAGroup(base_id=base.id, all_answers=request.param)


@pytest.fixture(params=[False, True])
def answer(
    request: FixtureRequest,
    base: Optional[QABase],
    group: Union[QAGroup, QAEmptyGroup, None],
):
    if base is None:
        return None
    if group is None or isinstance(group, QAEmptyGroup):
        group_id = None
    else:
        group_id = group.id
    if base.type == QATypeEnum.OnlyChoice:
        if isinstance(group, QAGroup):
            answer = [random.choice(group.all_answers)]
        else:
            answer = ["1"]
    elif base.type == QATypeEnum.MultipleChoice:
        if isinstance(group, QAGroup):
            answer = random.choices(
                group.all_answers, k=random.randint(1, len(group.all_answers))
            )
        else:
            answer = ["1", "2"]
    else:
        if isinstance(group, QAGroup):
            answer = group.all_answers.copy()
            random.shuffle(answer)
        else:
            answer = ["1", "2", "3", "4"]
    assert isinstance(request.param, bool)
    return QAAnswer(
        base_id=base.id, group_id=group_id, is_correct=request.param, answer=answer
    )


def test_create_db_dto(base, group, answer):
    dto = DBDTO(base=base, group=group, answer=answer)
    if base is None:
        assert dto.is_base_loaded == False
        with pytest.raises(ValueError):
            dto.base
    else:
        assert dto.is_base_loaded == True
        assert dto.base == base
        del dto.base
        assert dto.is_base_loaded == False
        with pytest.raises(ValueError):
            dto.base

    if group is None:
        assert dto.is_group_loaded == False
        with pytest.raises(ValueError):
            dto.group
    else:
        assert dto.is_group_loaded == True
        assert dto.group == group
        del dto.group
        assert dto.is_group_loaded == False
        with pytest.raises(ValueError):
            dto.group

    if answer is None:
        assert dto.is_answer_loaded == False
        with pytest.raises(ValueError):
            dto.answer
    else:
        assert dto.is_answer_loaded == True
        assert dto.answer == answer
        del dto.answer
        assert dto.is_answer_loaded == False
        with pytest.raises(ValueError):
            dto.answer


# def test_incorrect_set():
#     dto = DBDTO()
#     with pytest.raises(ValueError):
#         dto.base = None  # type: ignore
#     with pytest.raises(ValueError):
#         dto.group = None  # type: ignore
#     with pytest.raises(ValueError):
#         dto.answer = None  # type: ignore


def test_base_setter(base):
    dto = DBDTO()

    if base is None:
        with pytest.raises(ValueError):
            dto.base = base
    else:
        assert dto.is_base_loaded == False
        dto.base = base
        assert dto.is_base_loaded == True


def test_group_setter(group):
    dto = DBDTO()

    if group is None:
        with pytest.raises(ValueError):
            dto.group = group
    else:
        assert dto.is_group_loaded == False
        dto.group = group
        assert dto.is_group_loaded == True


def test_answer_setter(answer):
    dto = DBDTO()

    if answer is None:
        with pytest.raises(ValueError):
            dto.answer = answer
    else:
        assert dto.is_answer_loaded == False
        dto.answer = answer
        assert dto.is_answer_loaded == True
