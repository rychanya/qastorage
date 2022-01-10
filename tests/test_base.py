from uuid import uuid4

import pytest

from storage.base_store import QABaseNotExist
from storage.dto import QABaseDTO

from . import mongo_helpers
from .helpers import CountRaw, FindRaw, GetStore, InsertRaw, QABaseDicts, QABaseDTOs


@pytest.mark.parametrize("fake_base_dto", QABaseDTOs)
@pytest.mark.parametrize(
    "get_store, count_base", [(mongo_helpers.StoreContext, mongo_helpers.count_base)]
)
def test_if_not_in_db(
    get_store: GetStore, count_base: CountRaw, fake_base_dto: QABaseDTO
):
    with get_store() as store:
        assert count_base(store) == 0

        store.get_or_create_base(fake_base_dto)

        assert count_base(store) == 1


@pytest.mark.parametrize("fake_base_dict", QABaseDicts)
@pytest.mark.parametrize(
    "get_store, insert_base_row, find_base_row, count_base",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_base_row,
            mongo_helpers.find_base_row,
            mongo_helpers.count_base,
        )
    ],
)
def test_if_in_db(
    get_store: GetStore,
    insert_base_row: InsertRaw,
    find_base_row: FindRaw,
    count_base: CountRaw,
    fake_base_dict: dict,
):
    with get_store() as store:
        assert count_base(store) == 0
        insert_base_row(store, fake_base_dict)
        assert count_base(store) == 1
        doc = find_base_row(store)
        assert doc is not None

        base = store.get_or_create_base(QABaseDTO.parse_obj(fake_base_dict))

        assert count_base(store) == 1
        assert base.id == doc["id"]


@pytest.mark.parametrize("fake_base_dict", QABaseDicts)
@pytest.mark.parametrize(
    "get_store, insert_base_row, find_base_row, count_base",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_base_row,
            mongo_helpers.find_base_row,
            mongo_helpers.count_base,
        )
    ],
)
def test_id(
    get_store: GetStore,
    insert_base_row: InsertRaw,
    find_base_row: FindRaw,
    count_base: CountRaw,
    fake_base_dict: dict,
):
    with get_store() as store:
        assert count_base(store) == 0
        insert_base_row(store, fake_base_dict)
        assert count_base(store) == 1
        doc = find_base_row(store)
        assert doc is not None

        with pytest.raises(QABaseNotExist):
            store.get_or_create_base(uuid4())

        base = store.get_or_create_base(fake_base_dict["id"])

        assert base.id == fake_base_dict["id"]
        assert count_base(store) == 1


@pytest.mark.parametrize("fake_base_dict", QABaseDicts)
@pytest.mark.parametrize(
    "get_store, insert_base_row, find_base_row, count_base",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_base_row,
            mongo_helpers.find_base_row,
            mongo_helpers.count_base,
        )
    ],
)
def test_many(
    get_store: GetStore,
    insert_base_row: InsertRaw,
    find_base_row: FindRaw,
    count_base: CountRaw,
    fake_base_dict: dict,
):
    with get_store() as store:
        assert count_base(store) == 0
        insert_base_row(store, fake_base_dict)
        assert count_base(store) == 1
        doc = find_base_row(store)
        assert doc is not None

        dto = QABaseDTO.parse_obj(fake_base_dict)
        base = store.get_or_create_base(dto)
        store.get_or_create_base(dto)
        base2 = store.get_or_create_base(base.id)
        store.get_or_create_base(base.id)

        assert base.id == base2.id
        assert count_base(store) == 1
