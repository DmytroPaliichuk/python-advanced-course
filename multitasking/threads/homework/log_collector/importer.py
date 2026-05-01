"""
Завдання:
    Реалізувати багатопотоковий імпортер логів на основі черги, worker-потоків
    та пулу потоків, який буде надсилати записи на локальний HTTP-сервер.

    Працювати лише з файлом importer.py.
    Файли support.py та server.py - повністю готові й змінювати їх не потрібно.

    Частина 1 - LogWorker:
        - Реалізувати клас worker-потоку, який:
            - отримує елементи з черги;
            - відправляє логи через LogSender;
            - коректно завершується;
            - викликає task_done() для кожного обробленого запису.

    Частина 2 - LogWorkerPool:
        - Реалізувати пул потоків, який:
            - створює визначену кількість worker-ів;
            - запускає всі worker-и;
            - приймає задачі через submit();
            - коректно завершує виконання;
            - очікує завершення всіх задач і потоків через wait().

    Частина 3 - LogImporter:
        - Реалізувати два способи імпорту логів:
            1) send_single_thread - послідовна відправка.
            2) send_multi_thread - багатопотокова відправка через LogWorkerPool.
        - Обидва методи мають бути коректно реалізовані та працювати з даними,
          згенерованими за допомогою LogGenerator.

Вимоги:
    - Не змінювати сигнатури класів і методів;
    - Не змінювати файли support.py та server.py;
    - Усі реалізації мають бути потокобезпечними;
    - Має бути використана queue.Queue та threading.Thread;
    - Обов’язкове коректне завершення потоків;
    - Код має бути чистим, інкапсульованим, без глобальних змінних.

Актуальність:
    У реальних системах логування, моніторингу та ETL-процесів великий потік
    даних часто обробляється у багатопотокових конвеєрах. Це дозволяє значно
    збільшити пропускну здатність та зменшити загальний час обробки.

    Це завдання дозволяє:
        - зрозуміти, як побудувати producer–consumer pipeline;
        - попрактикуватись із чергою та коректним завершенням потоків;
        - побачити різницю між однопотоковим та багатопотоковим виконанням;
        - оцінити реальний виграш у швидкості при I/O-bound навантаженні;
        - отримати навички побудови конкурентних імпортних систем.
"""

import queue
import threading
import time

from multitasking.threads.homework.log_collector.support import (
    LogGenerator,
    LogRecord,
)

_SENTINEL = object()


class LogWorker(threading.Thread):
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
        """
        Основний цикл worker-потоку.

        Треба реалізувати:
        - нескінченний цикл читання з черги;
        - правильну обробку завершення роботи;
        - відправку логів через LogSender.send;
        - коректну обробку помилок;
        - позначення задач у черзі (task_done) у всіх випадках.
        """
        # TODO: implement solution
        ...


class LogWorkerPool:
    """
    Пул потоків.

    Треба реалізувати:
    - створення і запуск усіх worker-ів;
    - подачу задач до черги (метод submit);
    - коректне завершення (метод close);
    - очікування завершення всіх задач і потоків (метод wait).
    """

    def __init__(self, server_url: str, workers: int, max_queue_size: int = 10_000):
        self.server_url = server_url
        self.workers = workers
        self.queue: 'queue.Queue[LogRecord | object]' = queue.Queue(maxsize=max_queue_size)

        self.threads: list[LogWorker] = [
            LogWorker(
                name=f'worker-{i}',
                server_url=server_url,
                log_queue=self.queue,
            )
            for i in range(workers)
        ]

    def start(self) -> None:
        """Запуск кожного потоку."""
        # TODO: implement solution
        ...

    def submit(self, record: LogRecord) -> None:
        """
        Додає новий лог у чергу. Має працювати потокобезпечно та не блокувати програму.
        """
        # TODO: implement solution
        ...

    def close(self) -> None:
        """
        Коректно завершити роботу worker-ів.
        """
        # TODO: implement solution
        ...

    def wait(self) -> None:
        """
        Очікує завершення:
            - опрацювання всіх задач у черзі,
            - завершення всіх потоків.
        """
        # TODO: implement solution
        ...


class LogImporter:
    """
    Клас верхнього рівня для роботи з імпортом логів.

    Треба реалізувати:
        - однопотокову відправку (метод send_single_thread);
        - багатопотокову відправку через LogWorkerPool (метод send_multi_thread).
    """

    def __init__(self, server_url: str):
        self.server_url = server_url

    def send_single_thread(self, logs: list[LogRecord]):
        """Відправляє всі логи послідовно."""
        # TODO: implement solution
        ...

    def send_multi_thread(
        self,
        logs: list[LogRecord],
        workers: int = 8,
        max_queue_size: int = 10_000,
    ):
        """
        Реалізує багатопотокову відправку логів.
        Створити та запустити LogWorkerPool, надіслати логи, закрити пул, дочекатися виконання всіх задач.
        """
        # TODO: implement solution
        ...


def main() -> None:
    """Допоміжна функція для тестування."""
    importer = LogImporter(server_url='http://127.0.0.1:8000/logs')

    total_logs = 500_000
    workers = ...  # виріши скільки

    print(f'Generating {total_logs} log records...')
    logs = LogGenerator.generate(total_logs, payload_size=800)

    print('Running single-thread sender...')
    start = time.perf_counter()
    importer.send_single_thread(logs)
    single_thread_time = time.perf_counter() - start
    print(f'Single-thread: {single_thread_time:.3f} s')

    print(f'Running multi-thread sender with {workers} workers...')
    start = time.perf_counter()
    importer.send_multi_thread(logs, workers=workers)
    multi_thread_time = time.perf_counter() - start
    print(f'Multi-thread: {multi_thread_time:.3f} s')

    print(f'Speedup: {single_thread_time / multi_thread_time:.2f}x')


if __name__ == '__main__':
    main()
