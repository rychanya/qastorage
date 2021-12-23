import pytest

from qastorage.dto import BaseDTO, QATypeEnum
from qastorage.mongo_srore import MongoStore


@pytest.fixture
def fake_dto():
    return BaseDTO(question="question", type=QATypeEnum.OnlyChoice)


def test_mongo(store: MongoStore, fake_dto: BaseDTO):
    def count_documents():
        return store._base_collection.count_documents({})

    assert count_documents() == 0
    id = store.get_or_create_base(fake_dto)
    assert count_documents() == 1
    id2 = store.get_or_create_base(fake_dto)
    assert count_documents() == 1
    assert id == id2
