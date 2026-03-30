from typing import Any
from unittest.mock import MagicMock, patch

from memory.fragments_and_copies.homework.event_aggregator import (
    EventAggregator,
)


def _get_field(obj: Any, name: str) -> Any:
    try:
        return getattr(obj, name)
    except AttributeError:
        pass

    try:
        return obj[name]
    except (KeyError, TypeError):
        raise AssertionError(f'Object has no field {name} as attribute or as dict key.')


class TestEventAggregator:
    @patch('memory.fragments_and_copies.homework_answers.event_aggregator.fake_boto3.client')
    def test_run_structure(self, mock_client: MagicMock, mock_s3: MagicMock):
        mock_client.return_value = mock_s3

        aggr = EventAggregator('bucket', 'data/')
        result = list(aggr.run())

        assert isinstance(result, list)
        assert len(result) == 2

        for rec in result:
            user = _get_field(rec, 'user')
            count = _get_field(rec, 'count')
            events = list(_get_field(rec, 'events'))

            assert isinstance(user, str), f'user must be string, got {type(user).__name__}'
            assert isinstance(count, int), f'count must be int, got {type(count).__name__}'

            assert count > 0, f'count must be > 0, got {count}'
            assert len(events) == count, f'events length ({len(events)}) must match count ({count})'

    @patch('memory.fragments_and_copies.homework_answers.event_aggregator.fake_boto3.client')
    def test_users_are_aggregated(self, mock_client: MagicMock, mock_s3: MagicMock, test_files: dict[str, list]):
        mock_client.return_value = mock_s3

        aggr = EventAggregator('bucket', 'data/')
        result = {_get_field(rec, 'user'): rec for rec in aggr.run()}

        assert set(result) == {'u1', 'u2'}
        assert _get_field(_get_field(result, 'u1'), 'count') == len(test_files['data/file1.json'])
        assert _get_field(_get_field(result, 'u1'), 'count') == len(test_files['data/file2.json'])

    @patch('memory.fragments_and_copies.homework_answers.event_aggregator.fake_boto3.client')
    def test_timestamp_normalized(self, mock_client: MagicMock, mock_s3: MagicMock):
        mock_client.return_value = mock_s3

        aggr = EventAggregator('bucket', 'data/')
        result = list(aggr.run())

        for rec in result:
            for event in _get_field(rec, 'events'):
                assert not isinstance(_get_field(event, 'timestamp'), str)
                assert isinstance(_get_field(event, 'timestamp'), (float, int))
