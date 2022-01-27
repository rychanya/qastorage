import subprocess
from tempfile import TemporaryDirectory
from typing import Optional

import pytest

from storage import StoreType
from storage import get_store as get_storage
from storage.db_models import DBDTO, QABase, QAEmptyGroup, QAGroup, QATypeEnum
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
def db_dto_fixture_or_none(base_or_none, group_or_none):
    if base_or_none is None and group_or_none is None:
        return None
    return DBDTO(base=base_or_none, group=group_or_none)


@pytest.fixture
def db_dto_fixture(base, group):
    return DBDTO(base=base, group=group)
