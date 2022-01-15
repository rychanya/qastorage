from uuid import uuid4

import pytest

from storage import StoreType
from storage.db_models import DBDTO, QABase, QATypeEnum
from storage.dto import QABaseDTO
from storage.mongo_store import MongoStore


@pytest.mark.parametrize(
    "base_dto",
    [
        None,
        DBDTO(base=QABase(id=uuid4(), type=QATypeEnum.OnlyChoice, question="question")),
    ],
)
@pytest.mark.parametrize("type", list(QATypeEnum))
def test_create(type: str, base_dto: DBDTO, get_store):
    store: MongoStore = get_store(StoreType.Mongo)

    doc = {"type": type, "question": "question"}

    dto = store.create_base(QABaseDTO.parse_obj(doc), base_dto)
    doc_from_db = store._bases_collection.find_one({})

    assert dto.is_base_loaded
    assert doc_from_db
    assert dto.base.id == doc_from_db["id"]
    assert dto.base == QABase.parse_obj(doc_from_db)
