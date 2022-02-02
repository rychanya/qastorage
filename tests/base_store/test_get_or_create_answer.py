import pytest

from storage import StoreType
from storage.base_store import AbstractStore
from storage.db_models import DBDTO, QAEmptyGroup, QAGroup
from storage.dto import QAAnswerDTO


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_if_in_db(get_store, store_type, save_db_dto):
    store: AbstractStore = get_store(store_type)
    db_dto = save_db_dto(store)

    dto = store.get_or_create_answer(
        QAAnswerDTO(answer=db_dto.answer.answer, is_correct=db_dto.answer.is_correct),
        db_dto=DBDTO(
            base=db_dto.base.copy(), group=db_dto.group.copy() if isinstance(db_dto.group, QAGroup) else QAEmptyGroup()
        ),
    )

    assert dto.answer == db_dto.answer


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_by_id_if_in_db(get_store, store_type, save_db_dto):
    store: AbstractStore = get_store(store_type)
    db_dto = save_db_dto(store)

    dto = store.get_or_create_answer(
        db_dto.answer.id,
        db_dto=None,
    )

    assert dto.answer == db_dto.answer


@pytest.mark.parametrize("store_type", list(StoreType))
def test_get_or_create_if_not_in_db(get_store, store_type, db_dto_fixture: DBDTO):
    store: AbstractStore = get_store(store_type)

    dto = store.get_or_create_answer(
        QAAnswerDTO(answer=db_dto_fixture.answer.answer, is_correct=db_dto_fixture.answer.is_correct),
        db_dto=DBDTO(
            base=db_dto_fixture.base.copy(),
            group=db_dto_fixture.group.copy() if isinstance(db_dto_fixture.group, QAGroup) else QAEmptyGroup(),
        ),
    )

    assert dto.is_answer_loaded is True
    assert dto.answer == store.get_answer_by_id(dto.answer.id).answer
