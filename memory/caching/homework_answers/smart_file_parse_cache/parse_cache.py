from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(slots=True, frozen=True)
class FileFingerprint:
    modified_ns: int
    size: int


@dataclass(slots=True)
class CacheStats:
    hits: int = 0
    misses: int = 0
    refreshes: int = 0

    @property
    def total_requests(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests


@dataclass(slots=True)
class _CacheEntry:
    fingerprint: FileFingerprint
    value: Any


class FileParseCache:
    """Кешує результати парсингу файлів за їхнім шляхом і fingerprint."""

    __slots__ = ('_parser', '_entries', '_stats')

    def __init__(self, parser: Callable[[Path], Any]) -> None:
        self._parser = parser
        self._entries: dict[Path, _CacheEntry] = {}
        self._stats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        return self._stats

    @property
    def size(self) -> int:
        return len(self._entries)

    def get(self, path: Path) -> Any:
        normalized_path = path.resolve()
        current_fingerprint = self._build_fingerprint(normalized_path)

        cache_entry = self._entries.get(normalized_path)

        if cache_entry is not None and cache_entry.fingerprint == current_fingerprint:
            self._stats.hits += 1
            return cache_entry.value

        parsed_value = self._parser(normalized_path)

        if cache_entry is None:
            self._stats.misses += 1
        else:
            self._stats.refreshes += 1

        self._entries[normalized_path] = _CacheEntry(
            fingerprint=current_fingerprint,
            value=parsed_value,
        )

        return parsed_value

    def contains(self, path: Path) -> bool:
        return path.resolve() in self._entries

    def invalidate(self, path: Path) -> None:
        self._entries.pop(path.resolve(), None)

    def clear(self) -> None:
        self._entries.clear()

    @staticmethod
    def _build_fingerprint(path: Path) -> FileFingerprint:
        file_stat = path.stat()

        return FileFingerprint(
            modified_ns=file_stat.st_mtime_ns,
            size=file_stat.st_size,
        )
