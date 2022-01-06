from typing import Any, ContextManager, Optional, Protocol

from storage.base_store import AbstractStore


class GetStore(Protocol):
    def __call__(self) -> ContextManager[AbstractStore]:
        ...


class FindRaw(Protocol):
    def __call__(self, store: AbstractStore, **kwds: Any) -> Optional[dict]:
        ...


class InsertRaw(Protocol):
    def __call__(self, store: AbstractStore, data: dict, **kwds: Any) -> None:
        ...


class CountRaw(Protocol):
    def __call__(self, store: AbstractStore, **kwds: Any) -> None:
        ...
