from concurrent.futures import Future, ThreadPoolExecutor
from threading import Semaphore
from typing import Any, Callable


class BoundedExecutor:
    __slots__ = ('_executor', '_semaphore')

    def __init__(self, max_workers: int, max_pending: int) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._semaphore = Semaphore(max_pending)

    def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        self._semaphore.acquire()

        try:
            future = self._executor.submit(fn, *args, **kwargs)
        except Exception:
            # важливо уникнути втрати permit семафора
            self._semaphore.release()
            raise

        future.add_done_callback(self._release_callback)

        return future

    def shutdown(self, wait: bool = True) -> None:
        self._executor.shutdown(wait=wait)

    def _release_callback(self, _: Future) -> None:
        self._semaphore.release()
