from .s3 import FakeS3Client

FAKE_S3_DATA = {
    'events/file1.json': '[{"user_id": "u1", "timestamp": "2024-01-01T09:00:00", "event": "click"}]',
    'events/file2.json': '[{"user_id": "u1", "timestamp": "2024-01-01T10:00:00", "event": "scroll"}]',
    'events/file3.json': '[{"user_id": "u2", "timestamp": "2024-01-01T10:00:00", "event": "scroll"}]',
}


def client(service_name: str):
    if service_name == 's3':
        return FakeS3Client(FAKE_S3_DATA)
    raise ValueError('Only S3 is supported in fake boto3')
