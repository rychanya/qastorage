from typing import Optional, Union
from uuid import UUID, uuid4

import pytest
from _pytest.monkeypatch import MonkeyPatch

from storage import StoreType
from storage.base_store import AbstractStore
from storage.db_models import DBDTO, QABase, QATypeEnum
from storage.dto import QABaseDTO


@pytest.mark.parametrize("store_type", list(StoreType))
@pytest.mark.parametrize("dto", [QABaseDTO(question="question", type=QATypeEnum.OnlyChoice), uuid4()])
@pytest.mark.parametrize("db_dto", [None, DBDTO()])
def test_get_or_create(
    monkeypatch: MonkeyPatch, get_store, store_type, dto: Union[UUID, QABaseDTO], db_dto: Optional[DBDTO]
):
    store: AbstractStore = get_store(store_type)
    if isinstance(dto, UUID):

        def fake_get_by_id(base_id: UUID, db_dto: DBDTO = None, **kwargs):
            fake_base = QABase(id=base_id, type=QATypeEnum.OnlyChoice, question="question")
            if db_dto is None:
                db_dto = DBDTO()
            db_dto.base = fake_base
            return db_dto

        monkeypatch.setattr(store, "get_base_by_id", fake_get_by_id)
    result = store.get_or_create_base(dto, db_dto=db_dto)

    by_id = store.get_base_by_id(result.base.id)

    assert result.base == by_id.base
