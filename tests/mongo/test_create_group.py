from typing import Optional, Union

import pytest

from storage import StoreType
from storage.db_models import DBDTO, QABase, QAEmptyGroup, QAGroup
from storage.dto import QAGroupDTO
from storage.mongo_store import MongoStore


def test_create(
    db_dto_fixture_or_none: Optional[DBDTO],
    get_store,
    base_or_none: Optional[QABase],
    group_or_none: Union[None, QAGroup, QAEmptyGroup],
):
    store: MongoStore = get_store(StoreType.Mongo)
    if base_or_none:
        store._bases_collection.insert_one(base_or_none.dict())
    if not isinstance(group_or_none, QAGroup):
        return

    dto = store.create_group(
        QAGroupDTO(all_answers=group_or_none.all_answers, all_extra=group_or_none.all_extra),
        db_dto=db_dto_fixture_or_none,
    )

    assert dto.is_group_loaded is True
    assert dto.is_base_loaded is True
    assert isinstance(dto.group, QAGroup)
    assert dto.base.id == dto.group.base_id
    assert QAGroup.parse_obj(store._groups_collection.find_one({"id": dto.group.id})) == dto.group


def test_create_without_base(
    get_store, group_or_none: Union[None, QAGroup, QAEmptyGroup], db_dto_fixture_or_none: Optional[DBDTO]
):
    store: MongoStore = get_store(StoreType.Mongo)
    if not isinstance(group_or_none, QAGroup):
        return

    with pytest.raises(ValueError):
        store.create_group(
            QAGroupDTO(all_answers=group_or_none.all_answers, all_extra=group_or_none.all_extra),
            db_dto=db_dto_fixture_or_none,
        )

    with pytest.raises(ValueError):
        store.create_group(
            QAGroupDTO(all_answers=group_or_none.all_answers, all_extra=group_or_none.all_extra), db_dto=None
        )
