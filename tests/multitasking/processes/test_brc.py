from pathlib import Path

from multitasking.processes.homework.brc.aggregator import (
    ParallelMeasurementsAggregator,
    StationStats,
)


class TestStationStats:
    def test_create(self):
        stats = StationStats.create(10.0)

        assert stats.min_value == 10.0
        assert stats.max_value == 10.0
        assert stats.sum_value == 10.0
        assert stats.count == 1

    def test_add_updates_values(self):
        stats = StationStats.create(10.0)

        stats.add(5.0)
        stats.add(15.0)

        assert stats.min_value == 5.0
        assert stats.max_value == 15.0
        assert stats.count == 3
        assert stats.sum_value == 30.0

    def test_mean(self):
        stats = StationStats.create(10.0)
        stats.add(20.0)

        assert stats.mean() == 15.0

    def test_merge(self):
        a = StationStats.create(10.0)
        a.add(20.0)

        b = StationStats.create(5.0)
        b.add(30.0)

        a.merge(b)

        assert a.min_value == 5.0
        assert a.max_value == 30.0
        assert a.count == 4
        assert a.sum_value == 65.0


class TestParallelMeasurementsAggregator:
    def test_process_partition_single_worker(self, tmp_path: Path):
        file_path = tmp_path / 'data.txt'

        file_path.write_text('Kyiv;10.0\nKyiv;20.0\nBerlin;5.0\n')

        file_size = file_path.stat().st_size

        result = ParallelMeasurementsAggregator._process_partition(file_path, 0, file_size)

        assert result[b'Kyiv'].min_value == 10.0
        assert result[b'Kyiv'].max_value == 20.0
        assert result[b'Kyiv'].count == 2

        assert result[b'Berlin'].min_value == 5.0
        assert result[b'Berlin'].count == 1

    def test_process_file_small_dataset(self, tmp_path: Path):
        file_path = tmp_path / 'measurements.txt'

        file_path.write_text('Kyiv;10.0\nKyiv;20.0\nBerlin;5.0\nBerlin;15.0\n')

        aggregator = ParallelMeasurementsAggregator(workers=2)

        stats = aggregator.process_file(file_path)

        assert stats[b'Kyiv'].min_value == 10.0
        assert stats[b'Kyiv'].max_value == 20.0
        assert stats[b'Kyiv'].count == 2

        assert stats[b'Berlin'].min_value == 5.0
        assert stats[b'Berlin'].max_value == 15.0
        assert stats[b'Berlin'].count == 2

    def test_render_sorted(self):
        stats = {
            b'Berlin': StationStats(5.0, 15.0, 20.0, 2),
            b'Kyiv': StationStats(10.0, 20.0, 30.0, 2),
        }

        result = ParallelMeasurementsAggregator.render_sorted(stats)

        assert result['Berlin'] == '5.0/10.0/15.0'
        assert result['Kyiv'] == '10.0/15.0/20.0'

        assert list(result) == ['Berlin', 'Kyiv']
