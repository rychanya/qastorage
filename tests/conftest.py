import random
import subprocess
from tempfile import TemporaryDirectory
from typing import Optional, Union

import pytest

from storage import StoreType
from storage import get_store as get_storage
from storage.base_store import AbstractStore
from storage.db_models import DBDTO, QAAnswer, QABase, QAEmptyGroup, QAGroup, QATypeEnum
from storage.dto import QAAnswerDTO, QABaseDTO, QAGroupDTO
from storage.mongo_store import MongoStore


@pytest.fixture(scope="session", autouse=True)
def mongo_client():
    with TemporaryDirectory() as tempdir:
        with subprocess.Popen(
            [
                "mongod",
                "--replSet",
                "rs0",
                "--dbpath",
                tempdir,
                "--bind_ip",
                "localhost",
            ],
            stdout=subprocess.DEVNULL,
        ) as mongo:
            subprocess.run(["mongosh", "--eval", "rs.initiate()"], stdout=subprocess.DEVNULL)

            yield

            mongo.terminate()
            mongo.wait()


@pytest.fixture
def get_store(monkeypatch):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
            monkeypatch.setenv("qa_storage_db_name", db_name)
            _store = get_storage()
            if not isinstance(_store, MongoStore):
                raise ValueError
            _store._client.drop_database(db_name)
            return _store
        else:
            raise ValueError

    return _get_store


@pytest.fixture
def set_store_settings(monkeypatch):
    def _get_store(store_name: str):
        if store_name == StoreType.Mongo:
            db_name = "test"
            monkeypatch.setenv("qa_storage_type", StoreType.Mongo)
            monkeypatch.setenv("qa_storage_db_name", db_name)
        else:
            monkeypatch.setenv("qa_storage_type", store_name)

    return _get_store


class _TypesFixtureRequest(pytest.FixtureRequest):
    param: Optional[str]


class _GroupFixtureRequest(pytest.FixtureRequest):
    param: Optional[bool]


class _AnswerFixtureRequest(pytest.FixtureRequest):
    param: bool


@pytest.fixture(params=[None, *QATypeEnum])
def types_or_none(request: _TypesFixtureRequest):
    return request.param


@pytest.fixture(params=[*QATypeEnum])
def types(request: _TypesFixtureRequest):
    return request.param


@pytest.fixture
def base_or_none(types_or_none):
    if types_or_none is None:
        return None
    return QABase(type=types_or_none, question="question")


@pytest.fixture
def base(types):
    return QABase(type=types, question="question")


@pytest.fixture(params=[True, False])
def group_or_none(request: _GroupFixtureRequest, base_or_none: Optional[QABase]):
    if request.param:
        if base_or_none is None:
            return
        if base_or_none.type == QATypeEnum.MatchingChoice:
            extra = ["extra_1", "extra_2", "extra_3", "extra_4"]
        else:
            extra = []
        return QAGroup(
            base_id=base_or_none.id,
            all_answers=[
                "answer_1",
                "answer_2",
                "answer_3",
                "answer_4",
            ],
            all_extra=extra,
        )
    else:
        return QAEmptyGroup()


@pytest.fixture(params=[True, False])
def group(request: _GroupFixtureRequest, base: QABase):
    if request.param:
        if base.type == QATypeEnum.MatchingChoice:
            extra = ["extra_1", "extra_2", "extra_3", "extra_4"]
        else:
            extra = []
        return QAGroup(
            base_id=base.id,
            all_answers=[
                "answer_1",
                "answer_2",
                "answer_3",
                "answer_4",
            ],
            all_extra=extra,
        )
    else:
        return QAEmptyGroup()


@pytest.fixture
def answer_list(types: str, group: Union[QAGroup, QAEmptyGroup]):
    if isinstance(group, QAEmptyGroup):
        all_answers = ["1", "2", "3", "4"]
    else:
        all_answers = group.all_answers
    if types == QATypeEnum.OnlyChoice:
        return random.choices(all_answers, k=1)
    elif types == QATypeEnum.MultipleChoice:
        return random.choices(all_answers, k=random.randint(1, len(all_answers)))
    elif types == QATypeEnum.MatchingChoice or types == QATypeEnum.RangingChoice:
        answer = all_answers.copy()
        random.shuffle(answer)
        return answer
    else:
        raise ValueError


@pytest.fixture(params=[False, True])
def answer(request: _AnswerFixtureRequest, base: QABase, group: Union[QAGroup, QAEmptyGroup], answer_list):
    group_id = group.id if isinstance(group, QAGroup) else None
    assert request.param is not None
    return QAAnswer(base_id=base.id, group_id=group_id, is_correct=request.param, answer=answer_list)


@pytest.fixture(params=[False, True])
def answer_or_none(
    request: _AnswerFixtureRequest,
    base_or_none: Optional[QABase],
    group_or_none: Union[QAGroup, QAEmptyGroup, None],
    answer_list,
):
    if base_or_none is None or group_or_none is None:
        return None
    group_id = group_or_none.id if isinstance(group_or_none, QAGroup) else None
    return QAAnswer(base_id=base_or_none.id, group_id=group_id, is_correct=request.param, answer=answer_list)


@pytest.fixture
def db_dto_fixture_or_none(base_or_none, group_or_none, answer_or_none):
    if base_or_none is None and group_or_none is None and answer_or_none is None:
        return None
    return DBDTO(base=base_or_none, group=group_or_none)


@pytest.fixture
def db_dto_fixture(base, group, answer):
    return DBDTO(base=base, group=group, answer=answer)


@pytest.fixture
def save_base(base: QABase):
    def _save_base(store: AbstractStore, _db_dto: DBDTO):
        store.create_base(QABaseDTO(question=base.question, type=base.type), db_dto=_db_dto)
        return _db_dto

    return _save_base


@pytest.fixture
def save_group(group: QAGroup):
    def _save_group(store: AbstractStore, _db_dto: DBDTO):
        if isinstance(group, QAGroup):
            store.create_group(
                QAGroupDTO(all_answers=group.all_answers, all_extra=group.all_extra),
                db_dto=_db_dto,
            )
        else:
            _db_dto.group = QAEmptyGroup()
        return _db_dto

    return _save_group


@pytest.fixture
def save_answer(answer: QAAnswer):
    def _save_answer(store: AbstractStore, _db_dto: DBDTO):
        store.create_answer(QAAnswerDTO(answer=answer.answer, is_correct=answer.is_correct), db_dto=_db_dto)
        return _db_dto

    return _save_answer


@pytest.fixture
def save_db_dto(save_base, save_group, save_answer):
    def _save_db_dto(store: AbstractStore):
        _db_dto = DBDTO()
        save_base(store, _db_dto)
        save_group(store, _db_dto)
        save_answer(store, _db_dto)
        return _db_dto

    return _save_db_dto
