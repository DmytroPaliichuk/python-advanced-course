import queue
import threading

from multitasking.threads.homework_answers.log_collector.support import (
    LogRecord,
    LogSender,
)

_SENTINEL = object()


class LogWorker(threading.Thread):
    """Worker-потік, який бере записи з черги й надсилає їх на сервер."""

    def __init__(
        self,
        name: str,
        server_url: str,
        log_queue: 'queue.Queue[LogRecord | object]',
    ):
        super().__init__(name=name)
        self.server_url = server_url
        self.queue = log_queue

    def run(self) -> None:
        while True:
            item = self.queue.get()

            try:
                if item is _SENTINEL:
                    self.queue.task_done()
                    break

                assert isinstance(item, LogRecord)

                try:
                    LogSender.send(self.server_url, item)
                except Exception as e:
                    print(f'[{self.name}] Error sending log: {e}')
                finally:
                    self.queue.task_done()

            except Exception:
                self.queue.task_done()
                break


class LogWorkerPool:
    """Пул потоків: створює worker-и, приймає задачі, завершує роботу."""

    def __init__(self, server_url: str, workers: int, max_queue_size: int = 10_000):
        self.server_url = server_url
        self.workers = workers
        self.queue: 'queue.Queue[LogRecord | object]' = queue.Queue(maxsize=max_queue_size)

        self.threads: list[LogWorker] = [
            LogWorker(name=f'worker-{i}', server_url=server_url, log_queue=self.queue) for i in range(workers)
        ]

    def start(self) -> None:
        for t in self.threads:
            t.start()

    def submit(self, record: LogRecord) -> None:
        self.queue.put(record)

    def close(self) -> None:
        for _ in range(self.workers):
            self.queue.put(_SENTINEL)

    def wait(self) -> None:
        self.queue.join()
        for t in self.threads:
            t.join()


class LogImporter:
    """Генерувати логи, послідовно та багатопотоково їх надсилає."""

    def __init__(self, server_url: str):
        self.server_url = server_url

    def send_single_thread(self, logs: list[LogRecord]):
        for record in logs:
            LogSender.send(self.server_url, record)

    def send_multi_thread(
        self,
        logs: list[LogRecord],
        workers: int = 8,
        max_queue_size: int = 10_000,
    ):
        pool = LogWorkerPool(self.server_url, workers, max_queue_size)
        pool.start()

        for record in logs:
            pool.submit(record)

        pool.close()
        pool.wait()
