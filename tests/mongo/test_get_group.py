from typing import Optional, Union
from uuid import uuid4

import pytest

from storage import StoreType
from storage.db_models import DBDTO, QABase, QAEmptyGroup, QAGroup
from storage.dto import QAGroupDTO, QATypeEnum
from storage.mongo_store import MongoStore


def test_if_not_in_db(db_dto_fixture_or_none: Optional[DBDTO], get_store):
    store: MongoStore = get_store(StoreType.Mongo)
    if (
        db_dto_fixture_or_none
        and db_dto_fixture_or_none.is_group_loaded
        and isinstance(db_dto_fixture_or_none.group, QAGroup)
    ):
        dto_in = QAGroupDTO.parse_obj(db_dto_fixture_or_none.group.dict())
    else:
        dto_in = QAGroupDTO(all_answers=["answer", "answer2"])

    dto = store.get_group(dto_in, db_dto=db_dto_fixture_or_none)

    assert dto.is_group_loaded is False
    with pytest.raises(ValueError):
        dto.group


def test_if_in_db(
    db_dto_fixture_or_none: Optional[DBDTO],
    get_store,
    base_or_none: Optional[QABase],
    group_or_none: Union[None, QAGroup, QAEmptyGroup],
):
    store: MongoStore = get_store(StoreType.Mongo)
    if base_or_none:
        base_id = base_or_none.id
        store._bases_collection.insert_one(base_or_none.dict())
    else:
        base_id = uuid4()
        store._bases_collection.insert_one({"id": base_id, "type": QATypeEnum.OnlyChoice, "question": "question"})

    if isinstance(group_or_none, QAGroup):
        dto_in = QAGroupDTO(all_answers=group_or_none.all_answers, all_extra=group_or_none.all_extra)
        store._groups_collection.insert_one(group_or_none.dict())
    else:
        dto_in = None

    dto = store.get_group(dto=dto_in, db_dto=db_dto_fixture_or_none)

    if dto_in:
        assert dto.is_group_loaded is True
        assert isinstance(dto.group, QAGroup)
        assert dto.group.base_id == base_id
        assert dto.is_base_loaded is True
        assert dto.base.id == base_id
    else:
        assert dto.is_group_loaded is True
        assert isinstance(dto.group, QAEmptyGroup)


def test_if_in_db_base_in_dto_not_set(
    db_dto_fixture_or_none: Optional[DBDTO],
    get_store,
    base_or_none: Optional[QABase],
    group_or_none: Union[None, QAGroup, QAEmptyGroup],
):
    store: MongoStore = get_store(StoreType.Mongo)
    if base_or_none:
        base_id = base_or_none.id
        store._bases_collection.insert_one(base_or_none.dict())
    else:
        base_id = uuid4()
        store._bases_collection.insert_one({"id": base_id, "type": QATypeEnum.OnlyChoice, "question": "question"})

    if isinstance(group_or_none, QAGroup):
        dto_in = QAGroupDTO(all_answers=group_or_none.all_answers, all_extra=group_or_none.all_extra)
        store._groups_collection.insert_one(group_or_none.dict())
    else:
        dto_in = None

    if db_dto_fixture_or_none:
        del db_dto_fixture_or_none.base

    dto = store.get_group(dto=dto_in, db_dto=db_dto_fixture_or_none)

    if dto_in:
        assert dto.is_group_loaded is True
        assert isinstance(dto.group, QAGroup)
        assert dto.group.base_id == base_id
        assert dto.is_base_loaded is True
        assert dto.base.id == base_id
    else:
        assert dto.is_group_loaded is True
        assert isinstance(dto.group, QAEmptyGroup)
