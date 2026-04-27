from typing import Generator, Sequence
from unittest.mock import patch

import pytest

from multitasking.threads.homework.downloader import ThreadDownloader
from multitasking.threads.homework.log_collector.support import (
    LogGenerator,
    LogRecord,
)


@pytest.fixture
def urls() -> Sequence[str]:
    return (
        'https://example.com/a.txt',
        'https://example.com/b.txt',
        'https://example.com/c.txt',
    )


@pytest.fixture
def tmp_dirs(tmp_path: str) -> tuple[str, str]:
    series = tmp_path / 'series'
    concurrent = tmp_path / 'concurrent'
    return str(series), str(concurrent)


@pytest.fixture
def downloader(urls: Sequence[str], tmp_dirs: Sequence[str]) -> ThreadDownloader:
    series_dir, concurrent_dir = tmp_dirs
    return ThreadDownloader(
        urls=urls,
        series_dir=series_dir,
        concurrent_dir=concurrent_dir,
        workers=4,
    )


class DummyResponse:
    def __init__(self, status: int = 200):
        self.status = status

    def raise_for_status(self):
        if self.status != 200:
            raise Exception('HTTP error')


@pytest.fixture
def fake_post() -> Generator[DummyResponse, None, None]:
    path = 'multitasking.threads.homework_answers.log_collector.support.requests.post'
    with patch(path, return_value=DummyResponse(200)) as m:
        yield m


@pytest.fixture
def logs() -> list[LogRecord]:
    return LogGenerator.generate(5, payload_size=20)
