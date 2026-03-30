import io

from memory.fragments_and_copies.homework.brc.aggregator import MeasurementsAggregator, StationStats


class TestStationStats:
    def test_create(self):
        stats = StationStats.create(10.0)

        assert stats.min_value == 10.0
        assert stats.max_value == 10.0
        assert stats.sum_value == 10.0
        assert stats.count == 1

    def test_add_updates_stats(self):
        stats = StationStats.create(10.0)

        stats.add(5.0)
        stats.add(20.0)

        assert stats.min_value == 5.0
        assert stats.max_value == 20.0
        assert stats.sum_value == 35.0
        assert stats.count == 3

    def test_mean(self):
        stats = StationStats.create(10.0)
        stats.add(20.0)

        assert stats.mean() == 15.0


class TestMeasurementsAggregator:
    def test_single_station(self):
        data = """Hamburg;10.0
Hamburg;20.0
Hamburg;30.0
"""

        stream = io.StringIO(data)

        agg = MeasurementsAggregator()
        agg._process_stream(stream)

        result = agg.render_sorted()

        assert result == {'Hamburg': '10.0/20.0/30.0'}

    def test_multiple_stations(self):
        data = """Hamburg;10.0
Kyiv;5.0
Hamburg;20.0
Kyiv;15.0
"""

        stream = io.StringIO(data)

        agg = MeasurementsAggregator()
        agg._process_stream(stream)

        result = agg.render_sorted()

        assert result == {
            'Hamburg': '10.0/15.0/20.0',
            'Kyiv': '5.0/10.0/15.0',
        }

    def test_negative_values(self):
        data = """Kyiv;-5.0
Kyiv;-3.0
Kyiv;-10.0
"""

        stream = io.StringIO(data)

        agg = MeasurementsAggregator()
        agg._process_stream(stream)

        result = agg.render_sorted()

        assert result == {'Kyiv': '-10.0/-6.0/-3.0'}

    def test_single_measurement(self):
        data = """Berlin;7.2
"""

        stream = io.StringIO(data)

        agg = MeasurementsAggregator()
        agg._process_stream(stream)

        result = agg.render_sorted()

        assert result == {'Berlin': '7.2/7.2/7.2'}

    def test_sorted_output(self):
        data = """Zurich;5.0
Amsterdam;3.0
Berlin;10.0
"""

        stream = io.StringIO(data)

        agg = MeasurementsAggregator()
        agg._process_stream(stream)

        result = agg.render_sorted()

        assert list(result) == [
            'Amsterdam',
            'Berlin',
            'Zurich',
        ]
