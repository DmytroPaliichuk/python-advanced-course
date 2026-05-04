import time

from dataclasses import asdict, dataclass

import requests


@dataclass(slots=True)
class LogRecord:
    timestamp: float
    level: str
    source: str
    message: str
    extra: dict


class LogGenerator:
    """Генерує синтетичні log-records."""

    @staticmethod
    def generate(count: int, payload_size: int = 500) -> list[LogRecord]:
        logs: list[LogRecord] = []
        payload = 'x' * payload_size

        for i in range(count):
            logs.append(
                LogRecord(
                    timestamp=time.time(),
                    level='INFO',
                    source='importer',
                    message=f'Log message #{i}',
                    extra={'index': i, 'payload': payload},
                )
            )
        return logs


class LogSender:
    """HTTP-клієнт для відправки одного лога."""

    @staticmethod
    def send(server_url: str, record: LogRecord, timeout: float = 2.0) -> None:
        resp = requests.post(
            server_url,
            json=asdict(record),
            timeout=timeout,
        )
        resp.raise_for_status()
