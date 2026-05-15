from __future__ import annotations

import json
import time

from pathlib import Path

import pytest

from memory.caching.homework.smart_file_parse_cache.parse_cache import (
    FileParseCache,
)


def parse_json_file(path: Path) -> dict:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


class TestFileParseCache:
    def test_first_get_is_miss(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        result = cache.get(path)

        assert result == {'version': 1}
        assert cache.stats.hits == 0
        assert cache.stats.misses == 1
        assert cache.stats.refreshes == 0
        assert cache.size == 1

    def test_second_get_is_hit(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        first = cache.get(path)
        second = cache.get(path)

        assert first == {'version': 1}
        assert second == {'version': 1}
        assert cache.stats.hits == 1
        assert cache.stats.misses == 1
        assert cache.stats.refreshes == 0
        assert cache.size == 1

    def test_refresh_after_file_change(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        first = cache.get(path)
        assert first == {'version': 1}

        time.sleep(0.01)
        path.write_text('{"version": 2}', encoding='utf-8')

        second = cache.get(path)

        assert second == {'version': 2}
        assert cache.stats.hits == 0
        assert cache.stats.misses == 1
        assert cache.stats.refreshes == 1
        assert cache.size == 1

    def test_contains(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        assert cache.contains(path) is False

        cache.get(path)

        assert cache.contains(path) is True

    def test_invalidate(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        cache.get(path)
        assert cache.contains(path) is True

        cache.invalidate(path)

        assert cache.contains(path) is False
        assert cache.size == 0

        cache.get(path)

        assert cache.stats.hits == 0
        assert cache.stats.misses == 2
        assert cache.stats.refreshes == 0

    def test_clear(self, tmp_path: Path):
        path1 = tmp_path / 'config1.json'
        path2 = tmp_path / 'config2.json'

        path1.write_text('{"version": 1}', encoding='utf-8')
        path2.write_text('{"version": 2}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        cache.get(path1)
        cache.get(path2)

        assert cache.size == 2

        cache.clear()

        assert cache.size == 0
        assert cache.contains(path1) is False
        assert cache.contains(path2) is False

    def test_hit_rate(self, tmp_path: Path):
        path = tmp_path / 'config.json'
        path.write_text('{"version": 1}', encoding='utf-8')

        cache = FileParseCache(parser=parse_json_file)

        cache.get(path)  # miss
        cache.get(path)  # hit
        cache.get(path)  # hit

        assert cache.stats.hits == 2
        assert cache.stats.misses == 1
        assert cache.stats.total_requests == 3
        assert cache.stats.hit_rate == pytest.approx(2 / 3)

    def test_nonexistent_file_raises(self, tmp_path: Path):
        path = tmp_path / 'missing.json'

        cache = FileParseCache(parser=parse_json_file)

        with pytest.raises(FileNotFoundError):
            cache.get(path)
