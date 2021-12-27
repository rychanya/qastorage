import random
from uuid import uuid4

import pytest

from qastorage.dto import QABaseDTO, QAGroupDTO, QATypeEnum
from qastorage.mongo_srore import MongoStore


@pytest.fixture
def fake_base_dto():
    return QABaseDTO(question="question", type=QATypeEnum.OnlyChoice)


@pytest.fixture
def fake_group_dto():
    return QAGroupDTO(all_answers=["1", "2", "3", "4"])


def test_gorc_base(store: MongoStore, fake_base_dto: QABaseDTO):
    def count_documents():
        return store._bases_collection.count_documents({})

    assert count_documents() == 0
    id = store.get_or_create_base(fake_base_dto)
    assert count_documents() == 1
    id2 = store.get_or_create_base(fake_base_dto)
    assert count_documents() == 1
    assert id == id2


def test_gorc_group(store: MongoStore, fake_group_dto: QAGroupDTO):
    def count_documents():
        return store._groups_collection.count_documents({})

    base_id = uuid4()
    assert count_documents() == 0
    id = store.get_or_create_group(fake_group_dto, base_id)
    assert count_documents() == 1
    id2 = store.get_or_create_group(fake_group_dto, base_id)
    assert count_documents() == 1
    assert id == id2
    new_dto = fake_group_dto.copy()
    while new_dto.all_answers != fake_group_dto.all_answers:
        random.shuffle(new_dto.all_answers)
    id3 = store.get_or_create_group(new_dto, base_id)
    assert count_documents() == 1
    assert id3 == id
