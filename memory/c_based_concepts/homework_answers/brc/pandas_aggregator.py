from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    def mean(self) -> float:
        return self.sum_value / self.count


class PandasMeasurementsAggregator:
    __slots__ = ('_stats', '_chunk_size')

    def __init__(self, chunk_size: int = 1_000_000):
        if chunk_size <= 0:
            raise ValueError('chunk_size має бути більшим за 0.')
        self._stats: dict[str, StationStats] = {}
        self._chunk_size = chunk_size

    def process_file(self, path: Path) -> None:
        chunk_reader = pd.read_csv(
            path,
            sep=';',
            header=None,
            names=['station', 'temperature'],
            dtype={
                'station': 'string',
                'temperature': 'float64',
            },
            engine='c',
            chunksize=self._chunk_size,
        )

        partial_stats_frames = []

        for chunk in chunk_reader:
            temperature_by_station = chunk.groupby('station')['temperature']
            grouped_stats = temperature_by_station.agg(['min', 'max', 'sum', 'count'])
            partial_stats_frames.append(grouped_stats)

        combined_stats = pd.concat(partial_stats_frames)

        final_stats = combined_stats.groupby(level=0).agg(
            {
                'min': 'min',
                'max': 'max',
                'sum': 'sum',
                'count': 'sum',
            }
        )

        self._stats = {
            station: StationStats(
                min_value=row['min'],
                max_value=row['max'],
                sum_value=row['sum'],
                count=row['count'],
            )
            for station, row in final_stats.iterrows()
        }

    def render_sorted(self) -> dict[str, str]:
        return {
            station: f'{station_stats.min_value:.1f}/{station_stats.mean():.1f}/{station_stats.max_value:.1f}'
            for station, station_stats in sorted(self._stats.items())
        }
