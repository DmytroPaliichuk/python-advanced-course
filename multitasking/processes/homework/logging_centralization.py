"""
Завдання:
    Під час використання multiprocessing кожен процес має власний logging-модуль
    та власні хендлери. Тому якщо просто робити logger.info() у кількох процесах -
    логи плутаються, відображаються у неправильному порядку, або різні процеси
    починають одночасно писати у один і той самий файл, пошкоджуючи його.

    У реальних системах цю проблему вирішують за допомогою 'централізації логів':
    всі дочірні процеси не пишуть логи напряму, а передають їх у головний процес,
    який уже безпечно і послідовно виконує логування.

    У цьому завданні вам потрібно реалізувати саме таку систему.

    Структура програми:
        - QueueLogHandler - хендлер, який не виводить логи, а надсилає LogRecord у multiprocessing.Queue.
        - LogListenerThread - потік у головному процесі, який зчитує LogRecord з черги та передає їх у handler.handle().
        - MPLogManager - менеджер, який:
            - замінює хендлери у logger на QueueLogHandler;
            - запускає LogListenerThread;
            - після завершення повертає оригінальні хендлери.
        Іншими словами, в головному процесі є окремий спеціальний потік, що 'слухає' логи,
        які передають інші процеси, передача логів відбувається за допомогою multiprocessing.Queue.

    Основне завдання - реалізувати логіку всередині класів:
        1. QueueLogHandler._prepare(record)
            - привести LogRecord до pickle-safe вигляду;
            - очистити args та exc_info.

        2. LogListenerThread.run()
            - основний цикл читання черги;
            - обробка записів через logger.handle();
            - завершення при отриманні SENTINEL.

        3. MPLogManager.start()
            - прибрати оригінальні хендлери;
            - встановити QueueLogHandler;
            - запустити потік-слухач.

        4. MPLogManager.stop()
            - послати SENTINEL у чергу;
            - зупинити потік-слухач;
            - повернути оригінальні хендлери;
            - закрити чергу.

    Після реалізації програма має працювати так:
        - усі дочірні процеси надсилають LogRecord у чергу;
        - потік у головному процесі приймає ці записи;
        - усі логи акуратно та послідовно виводяться тим самим logger-ом, незалежно від кількості процесів.

Актуальність:
    Це завдання моделює реальний сценарій у багатьох продакшен-проєктах,
    де сервер або сервіс запускає підпроцеси для обробки даних, рендерингу,
    ML-моделей, роботи з відео, ETL-операцій чи CPU-інтенсивних задач.

    У таких системах виникає типова проблема:
        - якщо підпроцеси пишуть у лог-файл одночасно, файл псується або отримує змішані записи (англ. interleaving);
        - якщо всі процеси друкують у stdout - логи перетинаються, порядок втрачається, дебаг ускладнюється;
        - якщо різні процеси використовують різні логери, немає централізованого аудиту, важко відтворити події.

    Передавання LogRecord через multiprocessing.Queue дозволяє:
        - централізувати логування у головному процесі;
        - уникнути гонок за файловий дескриптор;
        - зберігати правильний порядок логів (FIFO);
        - безпечно записувати у один файл або консоль;
        - ізолювати логіку логування від логіки роботи процесів.

    Так працюють:
        - worker-пули у бекенд-сервісах;
        - multiprocessing ETL-платформи;
        - ML-pipeline з паралельною обробкою;
        - системи, які працюють із великими файлами або відео;
        - інструменти, які запускають багато CPU-процесів.
"""

from __future__ import annotations

import logging
import multiprocessing
import random
import threading
import time

SENTINEL = ('__LOGGING_SENTINEL__',)


class QueueLogHandler(logging.Handler):
    """
    Хендлер, який не пише логи напряму, а складає LogRecord у multiprocessing.Queue.

    У цьому класі більша частина реалізації вже готова, але все ще потрібно
    дописати метод _prepare(), який приводить LogRecord до pickle-safe вигляду.
    """

    def __init__(self, queue: multiprocessing.Queue):
        super().__init__()
        self.queue = queue

    def emit(self, record: logging.LogRecord) -> None:
        """
        Кожен LogRecord передається в чергу.

        1. Підготувати LogRecord через self._prepare(record)
        2. Помістити у queue.put_nowait(record)
        3. У разі помилки викликати self.handleError(record)
        """
        try:
            prepared = self._prepare(record)
            self.queue.put_nowait(prepared)
        except Exception:
            self.handleError(record)

    def _prepare(self, record: logging.LogRecord) -> logging.LogRecord:
        """
        Привести LogRecord до стану, придатного для передачі між процесами.

        Потрібно зробити:
        - якщо record.args не порожні - підставити їх у record.msg та очистити args
        - якщо є record.exc_info - відформатувати запис (self.format(record)),
          після чого встановити record.exc_info = None

        Повернути модифікований record.
        """
        # TODO: implement solution
        ...


class LogListenerThread(threading.Thread):
    """
    Потік у головному процесі, який:

    - постійно читає LogRecord з multiprocessing.Queue;
    - якщо отримано SENTINEL, завершує роботу;
    - передає логові записи у logger.handle(record), де вже працюють оригінальні хендлери.

    Залишилося реалізувати метод run().
    """

    def __init__(
        self,
        queue: multiprocessing.Queue,
        handlers: list[logging.Handler],
        logger_name: str,
    ):
        super().__init__(name='mp-log-listener', daemon=True)
        self.queue = queue
        self.handlers = handlers
        self.logger_name = logger_name
        self._closed = False

        # Логер, який використовуватиме оригінальні хендлери
        self._logger = logging.getLogger(f'{logger_name}.listener')
        self._logger.setLevel(logging.INFO)

        for handler in handlers:
            self._logger.addHandler(handler)

    def close(self) -> None:
        """Позначає завершення: надсилає SENTINEL у чергу."""
        self._closed = True
        self.queue.put_nowait(SENTINEL)

    def run(self) -> None:
        """
        Реалізувати основний цикл:
            while True:
                отримати запис з queue.get()
                якщо запис == SENTINEL:
                    break
                обробляємо список оригінальних хендлерів,
                передати в кожен запис handler.handle(record)
        У разі помилки - використовувати self._logger.exception()

        Після завершення:
        - прибрати оригінальні хендлери з self._logger
        """
        # TODO: implement solution
        ...


class MPLogManager:
    """
    Головний менеджер multiprocessing-логування.

    Він:
    - замінює хендлери у logger на QueueLogHandler;
    - запускає LogListenerThread;
    - після завершення відновлює оригінальні хендлери.

    Залишилося реалізувати start() і stop() - основні операції менеджера.
    """

    def __init__(self, logger: logging.Logger | None = None):
        self.logger = logger or logging.getLogger()
        self.queue = multiprocessing.Queue(-1)

        self.original_handlers: list[logging.Handler] = list(self.logger.handlers)

        self.listener = LogListenerThread(
            queue=self.queue,
            handlers=self.original_handlers,
            logger_name=self.logger.name,
        )

        # Queue handler, який замінить оригінальні
        self.queue_handler = QueueLogHandler(self.queue)

        self._started = False

    def start(self) -> None:
        """
        Увімкнути multiprocessing-safe логування:

        1. Прибрати всі original_handlers у self.logger.removeHandler(...)
        2. Додати self.queue_handler у logger.addHandler(...)
        3. Запустити self.listener.start()
        4. Поставити self._started = True
        """
        # TODO: implement solution
        ...

    def stop(self) -> None:
        """
        Коректно вимкнути multiprocessing логування:

        1. Викликати self.listener.close()
        2. Зачекати на завершення listener: self.listener.join(...)
        3. Забрати queue_handler з logger.removeHandler(...)
        4. Повернути всі original_handlers назад у logger.addHandler(...)
        5. Закрити чергу (queue.close(), queue.join_thread())
        6. Поставити self._started = False
        """
        # TODO: implement solution
        ...

    def __enter__(self) -> 'MPLogManager':
        """Контекстний менеджер: автоматично викликає start()."""
        self.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Контекстний менеджер: автоматично викликає stop()."""
        self.stop()


# -------------------------------
# Подивитися на роботу програми:
# -------------------------------


def worker_task(worker_id: int, queue: multiprocessing.Queue) -> None:
    """
    Функція, яку виконуватимуть дочірні процеси.
    Спочатку налаштовуємо логування в підпроцесі (через QueueLogHandler),
    а потім пишемо логи як зазвичай.
    """
    init_worker_logging(queue)
    logger = logging.getLogger()

    for i in range(5):
        sleep_time = round(random.uniform(0.1, 0.5), 2)
        logger.info(f'[Worker {worker_id}] iteration {i}, sleeping {sleep_time}s')
        time.sleep(sleep_time)

    logger.info(f'[Worker {worker_id}] completed')


def init_worker_logging(queue) -> None:
    """
    Налаштовує логування у підпроцесі.
    Кожен підпроцес має власний root logger, тому ми вручну
    підключаємо QueueLogHandler, щоб записи потрапляли у чергу.
    """
    logger = logging.getLogger()
    logger.handlers = []  # очищаємо стандартні хендлери підпроцесу
    logger.setLevel(logging.INFO)
    logger.addHandler(QueueLogHandler(queue))


if __name__ == '__main__':
    # 1. Налаштовуємо стандартний логер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        fmt='%(asctime)s | %(processName)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S',
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # 2. Вмикаємо multiprocessing-safe логування
    with MPLogManager(logger) as mp_log_manager:
        # 3. Створюємо та запускаємо процеси
        processes = [
            multiprocessing.Process(
                target=worker_task,
                args=(i, mp_log_manager.queue),
                name=f'WorkerProcess-{i}',
            )
            for i in range(5)
        ]

        for p in processes:
            p.start()

        for p in processes:
            p.join()

    # Після виходу з контекстного менеджера MPLogManager:
    # - listener thread зупинено
    # - оригінальні хендлери повернено
    # - чергу закрито
    # - логи знову працюють у звичайному режимі

    logger.info('All worker processes completed.')
