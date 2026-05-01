import threading
import time

from concurrent.futures import Future

from multitasking.threads.homework.bounded_executor import BoundedExecutor


class TestBoundedExecutor:
    def test_submit_returns_future(self):
        executor = BoundedExecutor(max_workers=2, max_pending=2)
        future = executor.submit(lambda: 42)

        assert isinstance(future, Future)
        assert future.result() == 42

        executor.shutdown()

    def test_tasks_are_executed(self):
        executor = BoundedExecutor(max_workers=2, max_pending=4)
        futures = [executor.submit(lambda x: x * x, i) for i in range(5)]
        results = [f.result() for f in futures]

        assert results == [0, 1, 4, 9, 16]

        executor.shutdown()

    def test_pending_limit_blocks_submit(self):
        executor = BoundedExecutor(max_workers=1, max_pending=1)
        started = threading.Event()

        def slow_task():
            started.set()
            time.sleep(0.5)

        # перша задача займе worker
        executor.submit(slow_task)
        started.wait()
        start_time = time.perf_counter()

        # друга задача займе pending слот
        executor.submit(lambda: time.sleep(0.5))

        # третя повинна чекати звільнення semaphore
        executor.submit(lambda: 1)

        elapsed = time.perf_counter() - start_time

        # submit має блокуватись приблизно ~0.5s
        assert elapsed >= 0.4

        executor.shutdown()

    def test_shutdown_waits_for_tasks(self):
        executor = BoundedExecutor(max_workers=2, max_pending=4)

        results = []

        def task():
            time.sleep(0.1)
            results.append(1)

        for _ in range(5):
            executor.submit(task)

        executor.shutdown(wait=True)
        assert len(results) == 5
