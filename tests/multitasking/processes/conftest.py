import logging
import multiprocessing

from typing import Generator
from unittest.mock import MagicMock

import pytest

from multitasking.processes.homework.shared_cache import (
    SharedCacheStorage,
    SharedPrimeCache,
)


@pytest.fixture
def logger() -> logging.Logger:
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.INFO)

    # чистимо існуючі хендлери
    for h in list(logger.handlers):
        logger.removeHandler(h)

    return logger


@pytest.fixture
def mock_handler() -> logging.StreamHandler:
    """Простий мок-хендлер, який лише фіксує виклики emit()."""
    handler = logging.StreamHandler()
    handler.emit = MagicMock()
    return handler


@pytest.fixture
def cache() -> Generator[SharedPrimeCache, None, None]:
    storage = SharedCacheStorage(capacity=8)
    desc = storage.descriptor()
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    cache = SharedPrimeCache(*desc, lock)
    yield cache

    cache.close()
    storage.close()
