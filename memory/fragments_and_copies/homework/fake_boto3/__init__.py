import json
import random

from datetime import datetime

from .s3 import FakeS3Client


def generate_events(n: int):
    events = []
    for _ in range(n):
        events.append(
            {
                'user_id': f'user{random.randint(1, 200)}',
                'timestamp': datetime.now().isoformat(),
                'event': random.choice(['click', 'scroll', 'open']),
                'value': random.randint(1, 10),
            }
        )
    return events


FAKE_S3_DATA = {
    'events/big_file.json': json.dumps(generate_events(200_000)),
}


def client(service_name: str):
    if service_name == 's3':
        return FakeS3Client(FAKE_S3_DATA)
    raise ValueError('Only S3 is supported in fake boto3')
