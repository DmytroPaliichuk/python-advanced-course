import json

from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def test_files() -> dict[str, list]:
    ts = datetime.now().isoformat()
    ts2 = (datetime.now() + timedelta(seconds=10)).isoformat()

    large_file1 = [{'user_id': 'u1', 'event': 'click', 'value': 1, 'timestamp': ts} for _ in range(500)]
    large_file2 = [{'user_id': 'u2', 'event': 'scroll', 'value': 3, 'timestamp': ts2} for _ in range(500)]

    return {
        'data/file1.json': large_file1,
        'data/file2.json': large_file2,
    }


@pytest.fixture
def mock_s3(test_files: dict[str, list]) -> MagicMock:
    s3 = MagicMock()

    s3.list_objects_v2.return_value = {'Contents': [{'Key': k} for k in test_files]}

    def get_object(Bucket: str, Key: str):
        return {
            'Body': MagicMock(
                read=lambda: json.dumps(test_files[Key]).encode(),
            ),
        }

    s3.get_object.side_effect = get_object

    return s3
