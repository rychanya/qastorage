from uuid import uuid4

import pytest

from storage.base_store import QAGroupNotExist
from storage.dto import QAGroupDTO

from . import mongo_helpers
from .helpers import CountRaw, FindRaw, GetStore, InsertRaw, QAGroupDicts, QAGroupDTOs


@pytest.mark.parametrize("fake_group_dto", QAGroupDTOs)
@pytest.mark.parametrize(
    "get_store, count_group", [(mongo_helpers.StoreContext, mongo_helpers.count_group)]
)
def test_if_not_in_db(
    get_store: GetStore, count_group: CountRaw, fake_group_dto: QAGroupDTO
):
    with get_store() as store:
        assert count_group(store) == 0
        base_id = uuid4()

        store.get_or_create_group(fake_group_dto, base_id)

        assert count_group(store) == 1


@pytest.mark.parametrize("fake_group_dict", QAGroupDicts)
@pytest.mark.parametrize(
    "get_store, insert_group_row, find_group_row, count_group",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_group_row,
            mongo_helpers.find_group_row,
            mongo_helpers.count_group,
        )
    ],
)
def test_if_in_db(
    get_store: GetStore,
    insert_group_row: InsertRaw,
    find_group_row: FindRaw,
    count_group: CountRaw,
    fake_group_dict: dict,
):
    with get_store() as store:
        assert count_group(store) == 0
        insert_group_row(store, fake_group_dict)
        assert count_group(store) == 1
        doc = find_group_row(store)
        assert doc is not None
        base_id = fake_group_dict["base_id"]

        group = store.get_or_create_group(
            QAGroupDTO.parse_obj(fake_group_dict), base_id
        )

        assert count_group(store) == 1
        assert group.id == doc["id"]


@pytest.mark.parametrize("fake_group_dict", QAGroupDicts)
@pytest.mark.parametrize(
    "get_store, insert_group_row, find_group_row, count_group",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_group_row,
            mongo_helpers.find_group_row,
            mongo_helpers.count_group,
        )
    ],
)
def test_id(
    get_store: GetStore,
    insert_group_row: InsertRaw,
    find_group_row: FindRaw,
    count_group: CountRaw,
    fake_group_dict: dict,
):
    with get_store() as store:
        assert count_group(store) == 0
        insert_group_row(store, fake_group_dict)
        assert count_group(store) == 1
        doc = find_group_row(store)
        assert doc is not None
        base_id = fake_group_dict["base_id"]

        with pytest.raises(QAGroupNotExist):
            store.get_or_create_group(uuid4(), base_id)

        group = store.get_or_create_group(fake_group_dict["id"], base_id)

        assert group.id == fake_group_dict["id"]
        assert count_group(store) == 1


@pytest.mark.parametrize("fake_group_dict", QAGroupDicts)
@pytest.mark.parametrize(
    "get_store, insert_group_row, find_group_row, count_group",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.insert_group_row,
            mongo_helpers.find_group_row,
            mongo_helpers.count_group,
        )
    ],
)
def test_many(
    get_store: GetStore,
    insert_group_row: InsertRaw,
    find_group_row: FindRaw,
    count_group: CountRaw,
    fake_group_dict: dict,
):
    with get_store() as store:
        assert count_group(store) == 0
        insert_group_row(store, fake_group_dict)
        assert count_group(store) == 1
        doc = find_group_row(store)
        assert doc is not None
        base_id = fake_group_dict["base_id"]

        dto = QAGroupDTO.parse_obj(fake_group_dict)
        group = store.get_or_create_group(dto, base_id)
        store.get_or_create_group(dto, base_id)
        group2 = store.get_or_create_group(group.id, base_id)
        store.get_or_create_group(group.id, base_id)

        assert group.id == group2.id
        assert count_group(store) == 1


@pytest.mark.parametrize(
    "get_store, count_group", [(mongo_helpers.StoreContext, mongo_helpers.count_group)]
)
def test_if_dto_is_none(get_store: GetStore, count_group: CountRaw):
    with get_store() as store:
        assert count_group(store) == 0
        base_id = uuid4()

        group = store.get_or_create_group(None, base_id)

        assert count_group(store) == 0
        assert group is None
