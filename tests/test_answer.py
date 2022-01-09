from typing import Optional
from uuid import uuid4

import pytest

from storage.base_store import QAAnswerNotExist, QAAnswerValidation
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO

from . import mongo_helpers
from .helpers import (
    CountRaw,
    FindRaw,
    GetStore,
    InsertRaw,
    QAAnswerDTOs,
    QAAnswerTuples,
    QAIncorrectAnswer,
    qa_answer_tuple_to_dto,
)


@pytest.mark.parametrize("fake_answer_dto", QAAnswerDTOs)
@pytest.mark.parametrize(
    "get_store, count_answer",
    [(mongo_helpers.StoreContext, mongo_helpers.count_answer)],
)
def test_if_not_in_db(
    get_store: GetStore, count_answer: CountRaw, fake_answer_dto: QAAnswerDTO
):
    with get_store() as store:
        assert count_answer(store) == 0

        _, is_new = store.get_or_create_qa(fake_answer_dto)

        assert count_answer(store) == 1
        assert is_new


@pytest.mark.parametrize("fake_answer_tuple", QAAnswerTuples)
@pytest.mark.parametrize(
    "get_store, count_answer, insert_answer_raw, find_answer_raw",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.count_answer,
            mongo_helpers.insert_answer_raw,
            mongo_helpers.find_answer_raw,
        )
    ],
)
def test_if_in_db(
    get_store: GetStore,
    fake_answer_tuple: tuple[dict, QABaseDTO, Optional[QAGroupDTO]],
    insert_answer_raw: InsertRaw,
    count_answer: CountRaw,
    find_answer_raw: FindRaw,
):
    with get_store() as store:
        answer, base, group = fake_answer_tuple
        base = store.get_or_create_base(base)
        group = store.get_or_create_group(group, base_id=base.id)
        group_id = group.id if group else None
        assert count_answer(store) == 0
        insert_answer_raw(store, answer, base_id=base.id, group_id=group_id)
        assert count_answer(store) == 1
        doc = find_answer_raw(store)
        assert doc

        dto = qa_answer_tuple_to_dto(fake_answer_tuple)
        answer, is_new = store.get_or_create_qa(dto)

        assert count_answer(store) == 1
        assert is_new is False
        assert answer.id == fake_answer_tuple[0]["id"]
        assert doc["id"] == answer.id


@pytest.mark.parametrize("fake_answer", QAIncorrectAnswer)
@pytest.mark.parametrize(
    "get_store, count_answer",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.count_answer,
        )
    ],
)
def test_incorrect(
    get_store: GetStore,
    fake_answer: QAAnswerDTO,
    count_answer: CountRaw,
):
    with get_store() as store:
        assert count_answer(store) == 0

        with pytest.raises(QAAnswerValidation):
            store.get_or_create_qa(fake_answer)

        assert count_answer(store) == 0


@pytest.mark.parametrize(
    "get_store, count_answer",
    [
        (
            mongo_helpers.StoreContext,
            mongo_helpers.count_answer,
        )
    ],
)
def test_get_by_id_if_not_in_db(
    count_answer: CountRaw,
    get_store: GetStore,
):
    with get_store() as store:
        assert count_answer(store) == 0

        with pytest.raises(QAAnswerNotExist):
            store.get_answer_by_id(uuid4())

        assert count_answer(store) == 0
