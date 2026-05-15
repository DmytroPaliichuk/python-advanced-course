from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    @classmethod
    def create(cls, value: float) -> 'StationStats':
        return cls(min_value=value, max_value=value, sum_value=value, count=1)

    def add(self, value: float) -> None:
        if value < self.min_value:
            self.min_value = value
        if value > self.max_value:
            self.max_value = value
        self.sum_value += value
        self.count += 1

    def mean(self) -> float:
        return self.sum_value / self.count


class MeasurementsAggregator:
    __slots__ = ('_stats',)

    def __init__(self) -> None:
        self._stats: dict[str, StationStats] = {}

    def process_file(self, path: str, encoding: str = 'utf-8') -> None:
        with open(path, 'r', encoding=encoding, newline='') as file:
            self._process_stream(file)

    def _process_stream(self, stream: TextIO) -> None:
        for line in stream:
            if line == '\n':
                continue

            station, temp_str = line.split(';', 1)
            value = float(temp_str)

            station_stats = self._stats.get(station)
            if station_stats is None:
                self._stats[station] = StationStats.create(value)
            else:
                station_stats.add(value)

    def render_sorted(self) -> dict[str, str]:
        return {
            station: f'{station_stats.min_value:.1f}/{station_stats.mean():.1f}/{station_stats.max_value:.1f}'
            for station, station_stats in sorted(self._stats.items())
        }
