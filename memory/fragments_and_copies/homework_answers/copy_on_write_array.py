from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass
class Storage:
    data: list[Any]
    refcount: int = 1


class CopyOnWriteArray:
    def __init__(self, items: Iterable[Any] | None = None) -> None:
        self._storage = Storage(data=list(items or []))

    def _ensure_own_copy(self) -> None:
        if self._storage.refcount > 1:
            self._storage.refcount -= 1
            self._storage = Storage(data=self._storage.data.copy())

    def cow_copy(self) -> CopyOnWriteArray:
        new = CopyOnWriteArray.__new__(CopyOnWriteArray)
        new._storage = self._storage
        self._storage.refcount += 1
        return new

    def __len__(self) -> int:
        return len(self._storage.data)

    def __getitem__(self, index: int) -> Any:
        return self._storage.data[index]

    def __setitem__(self, index: int, value: Any) -> None:
        self._ensure_own_copy()
        self._storage.data[index] = value

    def __delitem__(self, index: int) -> None:
        self._ensure_own_copy()
        del self._storage.data[index]

    def insert(self, index: int, value: Any) -> None:
        self._ensure_own_copy()
        self._storage.data.insert(index, value)

    def append(self, value: Any) -> None:
        self._ensure_own_copy()
        self._storage.data.append(value)

    def to_list(self) -> list[Any]:
        return self._storage.data.copy()

    def __repr__(self) -> str:
        return f'CopyOnWriteArray(data={self._storage.data}, refcount={self._storage.refcount})'
