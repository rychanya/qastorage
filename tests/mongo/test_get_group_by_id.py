from typing import Optional
from uuid import uuid4

import pytest

from storage import StoreType
from storage.db_models import DBDTO, QAEmptyGroup, QAGroup
from storage.mongo_store import MongoStore


def test_if_not_in_db(db_dto_fixture_or_none: Optional[DBDTO], get_store):
    store: MongoStore = get_store(StoreType.Mongo)

    dto = store.get_group_by_id(uuid4(), db_dto=db_dto_fixture_or_none)

    assert dto.is_group_loaded is False
    with pytest.raises(ValueError):
        dto.group


def test_if_in_db(db_dto_fixture_or_none: Optional[DBDTO], get_store):
    store: MongoStore = get_store(StoreType.Mongo)
    if (
        db_dto_fixture_or_none
        and db_dto_fixture_or_none.is_group_loaded
        and not isinstance(db_dto_fixture_or_none.group, QAEmptyGroup)
    ):
        doc = db_dto_fixture_or_none.group.dict()
    else:
        doc = {
            "id": uuid4(),
            "base_id": db_dto_fixture_or_none.base.id
            if db_dto_fixture_or_none and db_dto_fixture_or_none.is_base_loaded
            else uuid4(),
            "all_answers": ["answer", "answer2"],
            "all_extra": [],
        }
    store._groups_collection.insert_one(doc)

    dto = store.get_group_by_id(doc["id"], db_dto=db_dto_fixture_or_none)

    assert dto.is_group_loaded is True
    assert isinstance(dto.group, QAGroup)
    assert dto.group.id == doc["id"]
    assert QAGroup.parse_obj(doc) == dto.group
