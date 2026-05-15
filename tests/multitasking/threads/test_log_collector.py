import queue
import time

from typing import Generator

from multitasking.threads.homework.log_collector.importer import (
    LogImporter,
    LogWorker,
    LogWorkerPool,
)
from multitasking.threads.homework.log_collector.support import (
    LogGenerator,
    LogRecord,
)
from tests.multitasking.threads.conftest import DummyResponse

_SENTINEL = object()


class TestLogImporter:
    TEST_SERVER_URL = 'http://example.com/logs'

    def test_worker_sends_logs(self, fake_post: Generator[DummyResponse, None, None]):
        q = queue.Queue()
        worker = LogWorker(name='test-worker', server_url=self.TEST_SERVER_URL, log_queue=q)
        worker.start()

        record = LogRecord(
            timestamp=time.time(),
            level='INFO',
            source='test',
            message='msg',
            extra={},
        )
        q.put(record)
        q.put(_SENTINEL)

        worker.join(timeout=2)

        assert fake_post.call_count == 1

    def test_worker_stops_on_sentinel(self, fake_post: Generator[DummyResponse, None, None]):
        q = queue.Queue()
        worker = LogWorker(name='worker', server_url=self.TEST_SERVER_URL, log_queue=q)
        worker.start()

        q.put(_SENTINEL)
        worker.join(timeout=2)

        assert fake_post.call_count == 0

    def test_pool_processes_all_logs(self, fake_post: Generator[DummyResponse, None, None], logs: list[LogRecord]):
        pool = LogWorkerPool(server_url=self.TEST_SERVER_URL, workers=3)
        pool.start()

        for log in logs:
            pool.submit(log)

        pool.close()
        pool.wait()

        assert fake_post.call_count == len(logs)

    def test_pool_joins_threads(self, fake_post: Generator[DummyResponse, None, None]):
        pool = LogWorkerPool(server_url=self.TEST_SERVER_URL, workers=2)
        pool.start()

        pool.close()
        pool.wait()

        for t in pool.threads:
            assert not t.is_alive()

    def test_importer_single_thread(self, fake_post: Generator[DummyResponse, None, None], logs: list[LogRecord]):
        imp = LogImporter(self.TEST_SERVER_URL)

        imp.send_single_thread(logs)

        assert fake_post.call_count == len(logs)

    def test_importer_multi_thread(self, fake_post: Generator[DummyResponse, None, None], logs: list[LogRecord]):
        imp = LogImporter(self.TEST_SERVER_URL)

        imp.send_multi_thread(logs, workers=4)

        assert fake_post.call_count == len(logs)

    def test_large_batch_multi_thread(self, fake_post: Generator[DummyResponse, None, None]):
        logs = LogGenerator.generate(200, payload_size=50)
        imp = LogImporter(self.TEST_SERVER_URL)

        imp.send_multi_thread(logs, workers=6)

        assert fake_post.call_count == 200
