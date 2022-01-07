from typing import Optional

import pytest

from storage.dto import QAAnswerDTO

from . import mongo_helpers
from .helpers import CountRaw, FindRaw, GetStore, InsertRaw, QAAnswerDTOs


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


@pytest.mark.parametrize("fake_answer_tuple", QAAnswerDTOs)
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
    fake_answer_tuple: tuple[dict, dict, Optional[dict]],
    insert_answer_raw: InsertRaw,
    count_answer: CountRaw,
    find_answer_raw: FindRaw,
):
    with get_store() as store:
        assert count_answer(store) == 0
        insert_answer_raw(store, fake_answer_tuple)
        assert count_answer(store) == 1

        # to do
