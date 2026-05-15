from pathlib import Path

from memory.c_based_concepts.homework.brc.dask_aggregator import DaskMeasurementsAggregator, StationStats


class TestStationStats:
    def test_mean(self):
        stats = StationStats(
            min_value=1.0,
            max_value=5.0,
            sum_value=9.0,
            count=3,
        )

        assert stats.mean() == 3.0


class TestDaskMeasurementsAggregator:
    def test_process_file(self, sample_file: Path):
        aggregator = DaskMeasurementsAggregator()

        aggregator.process_file(sample_file)

        stats = aggregator._stats

        assert 'Kyiv' in stats
        assert 'Amsterdam' in stats

        kyiv = stats['Kyiv']
        assert kyiv.min_value == 1.0
        assert kyiv.max_value == 5.0
        assert kyiv.sum_value == 9.0
        assert kyiv.count == 3

        ams = stats['Amsterdam']
        assert ams.min_value == 7.0
        assert ams.max_value == 9.0
        assert ams.sum_value == 16.0
        assert ams.count == 2

    def test_render_sorted(self, sample_file: Path):
        aggregator = DaskMeasurementsAggregator()

        aggregator.process_file(sample_file)

        result = aggregator.render_sorted()

        assert list(result.keys()) == ['Amsterdam', 'Kyiv']

        assert result['Amsterdam'] == '7.0/8.0/9.0'
        assert result['Kyiv'] == '1.0/3.0/5.0'
