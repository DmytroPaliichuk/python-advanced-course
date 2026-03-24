"""
Допоміжний модуль для генерації тестового лог-файлу.

Цей файл наданий як частина домашнього завдання для підготовки вхідних даних. Змінювати його не потрібно.
"""

from __future__ import annotations

import random
import time

from pathlib import Path
from typing import Iterable


class LogFileGenerator:
    """Генерує тестовий лог-файл у форматі `timestamp;service;duration`."""

    DEFAULT_DURATION_MIN = 1
    DEFAULT_DURATION_MAX = 200
    DEFAULT_BUFFER_SIZE = 1024 * 1024

    __slots__ = (
        '_services',
        '_duration_min',
        '_duration_max',
    )

    def __init__(
        self,
        services: Iterable[str],
        duration_min: int = DEFAULT_DURATION_MIN,
        duration_max: int = DEFAULT_DURATION_MAX,
    ):
        if duration_min > duration_max:
            raise ValueError('duration_min не може бути більшим за duration_max.')

        self._services = tuple(services)

        if not self._services:
            raise ValueError('Список сервісів не може бути порожнім.')

        self._duration_min = duration_min
        self._duration_max = duration_max

    def generate(self, path: Path, rows: int, start_timestamp: int | None = None) -> None:
        if start_timestamp is None:
            start_timestamp = int(time.time())

        if rows < 0:
            raise ValueError('Кількість рядків не може бути від’ємною.')

        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open('w', encoding='utf-8', buffering=self.DEFAULT_BUFFER_SIZE) as file:
            for _ in range(rows):
                service = random.choice(self._services)
                duration = random.randint(self._duration_min, self._duration_max)

                file.write(f'{start_timestamp};{service};{duration}\n')

                start_timestamp += 1
