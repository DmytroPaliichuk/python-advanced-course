"""Допоміжний файл для генерації тестового датасету до задачі Billion Row Challenge.

Цей код використовується лише для створення великого тестового файлу з
температурними вимірюваннями у форматі `<station>;<temperature>`.

Змінювати цей файл не потрібно. Основне завдання домашньої роботи —
реалізувати обробку та агрегацію вже згенерованого файлу.
"""

import random

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True)
class GeneratorConfig:
    """Конфігурація генерації датасету."""

    rows: int
    output_path: Path
    stations_csv: Path
    batch_size: int = 100_000
    seed: int = 42
    min_temp: float = -99.9
    max_temp: float = 99.9


class MeasurementsGenerator:
    """Генерує файл із синтетичними вимірюваннями температури."""

    __slots__ = ('_cfg', '_rng', '_stations')

    def __init__(self, cfg: GeneratorConfig) -> None:
        self._cfg = cfg
        self._rng = random.Random(cfg.seed)
        self._stations = self._load_stations(cfg.stations_csv)

    def generate(self) -> None:
        self._cfg.output_path.parent.mkdir(parents=True, exist_ok=True)

        remaining_rows = self._cfg.rows

        with open(self._cfg.output_path, 'w', encoding='utf-8', newline='') as file:
            while remaining_rows > 0:
                n = min(self._cfg.batch_size, remaining_rows)

                lines = '\n'.join(
                    f'{self._rng.choice(self._stations)};'
                    f'{self._rng.uniform(self._cfg.min_temp, self._cfg.max_temp):.1f}'
                    for _ in range(n)
                )

                file.write(lines)
                file.write('\n')

                remaining_rows -= n

    @staticmethod
    def _load_stations(path: Path) -> tuple[str, ...]:
        stations = set()

        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.rstrip('\n')

                if not line:
                    continue

                name, _, _ = line.partition(';')
                stations.add(name)

        # Перетворюємо один раз у tuple для ефективної роботи random.choice.
        return tuple(stations)
