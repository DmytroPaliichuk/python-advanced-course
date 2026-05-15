from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import dask.dataframe as dd


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    def mean(self) -> float:
        return self.sum_value / self.count


class DaskMeasurementsAggregator:
    __slots__ = ('_stats', '_chunk_size')

    def __init__(self, chunk_size: str = '128MB'):
        if not chunk_size:
            raise ValueError('chunk_size не може бути порожнім.')
        self._stats: dict[str, StationStats] = {}
        self._chunk_size = chunk_size

    def process_file(self, path: Path) -> None:
        dataframe = dd.read_csv(
            path,
            sep=';',
            header=None,
            names=['station', 'temperature'],
            dtype={
                'station': 'string',
                'temperature': 'float64',
            },
            engine='pyarrow',
            blocksize=self._chunk_size,
        )

        temperature_by_station = dataframe.groupby('station')['temperature']
        grouped_stats = temperature_by_station.agg(['min', 'max', 'sum', 'count'])

        final_stats = grouped_stats.compute()

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
