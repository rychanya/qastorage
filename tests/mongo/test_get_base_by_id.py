from uuid import uuid4

import pytest

from storage import StoreType
from storage.db_models import DBDTO, QABase, QATypeEnum
from storage.mongo_store import MongoStore


@pytest.mark.parametrize(
    "base_dto",
    [
        None,
        DBDTO(base=QABase(id=uuid4(), type=QATypeEnum.OnlyChoice, question="question")),
    ],
)
@pytest.mark.parametrize("type", list(QATypeEnum))
def test_if_in_db(type: str, base_dto: DBDTO, get_store):
    store: MongoStore = get_store(StoreType.Mongo)
    doc = {"id": uuid4(), "type": type, "question": "question"}
    store._bases_collection.insert_one(doc)

    dto = store.get_base_by_id(base_id=doc["id"], db_dto=base_dto)

    assert dto.is_base_loaded
    assert dto.base.id == doc["id"]
    assert QABase.parse_obj(doc) == dto.base


@pytest.mark.parametrize(
    "base_dto",
    [
        None,
        DBDTO(base=QABase(id=uuid4(), type=QATypeEnum.OnlyChoice, question="question")),
    ],
)
def test_if_not_in_db(base_dto: DBDTO, get_store):
    store: MongoStore = get_store(StoreType.Mongo)
    id = uuid4()

    dto = store.get_base_by_id(base_id=id, db_dto=base_dto)

    assert dto.is_base_loaded is False
    with pytest.raises(ValueError):
        print(dto.base)
