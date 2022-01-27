from typing import Union

import pytest

from storage import StoreType
from storage.base_store import AbstractStore
from storage.db_models import DBDTO, QABase, QAEmptyGroup, QAGroup
from storage.dto import QABaseDTO, QAGroupDTO


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_if_in_db(get_store, store_type, base: QABase, group: Union[QAGroup, QAEmptyGroup]):
    store: AbstractStore = get_store(store_type)
    db_dto = DBDTO()
    store.create_base(QABaseDTO(question=base.question, type=base.type), db_dto=db_dto)
    if isinstance(group, QAGroup):
        dto_in = QAGroupDTO(all_answers=group.all_answers, all_extra=group.all_extra)
        store.create_group(QAGroupDTO(all_answers=group.all_answers, all_extra=group.all_extra), db_dto=db_dto)
    else:
        dto_in = None

    dto = store.get_or_create_group(dto_in, db_dto=db_dto)

    assert dto.is_group_loaded is True
    assert dto.is_base_loaded is True
    if dto_in is not None:
        assert isinstance(dto.group, QAGroup)
        assert dto.group == store.get_group_by_id(dto.group.id).group
    else:
        assert isinstance(dto.group, QAEmptyGroup)


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_by_id(get_store, store_type, base: QABase, group: Union[QAGroup, QAEmptyGroup]):
    if isinstance(group, QAEmptyGroup):
        return
    store: AbstractStore = get_store(store_type)
    db_dto = DBDTO()
    store.create_base(QABaseDTO(question=base.question, type=base.type), db_dto=db_dto)
    store.create_group(QAGroupDTO(all_answers=group.all_answers, all_extra=group.all_extra), db_dto=db_dto)

    assert isinstance(db_dto.group, QAGroup)

    dto = store.get_or_create_group(db_dto.group.id, db_dto=None)

    assert dto.is_group_loaded is True
    assert dto.is_base_loaded is True
    assert isinstance(dto.group, QAGroup)
    assert dto.group == store.get_group_by_id(dto.group.id).group


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_if_not_in_db(get_store, store_type, base: QABase, group: Union[QAGroup, QAEmptyGroup]):
    store: AbstractStore = get_store(store_type)
    db_dto = DBDTO()
    store.create_base(QABaseDTO(question=base.question, type=base.type), db_dto=db_dto)
    if isinstance(group, QAGroup):
        dto_in = QAGroupDTO(all_answers=group.all_answers, all_extra=group.all_extra)
    else:
        dto_in = None

    dto = store.get_or_create_group(dto_in, db_dto=db_dto)

    assert dto.is_group_loaded is True
    assert dto.is_base_loaded is True
    if dto_in is not None:
        assert isinstance(dto.group, QAGroup)
        assert dto.group == store.get_group_by_id(dto.group.id).group
    else:
        assert isinstance(dto.group, QAEmptyGroup)
