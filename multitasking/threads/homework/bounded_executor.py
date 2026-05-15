"""
Завдання:
    Реалізувати обмежений executor для потоків (BoundedExecutor), який дозволяє контролювати кількість задач,
    що знаходяться у черзі ThreadPoolExecutor.

    Стандартний ThreadPoolExecutor дозволяє додавати необмежену кількість задач через метод submit(). Якщо producer
    генерує задачі швидше, ніж worker-потоки їх виконують, то внутрішня черга executor починає швидко зростати.

    Це може призвести до того, що у пам'яті накопичується велика кількість Future-об'єктів разом з аргументами задач,
    що у підсумку призводить до значного росту використання RAM або навіть помилки Out Of Memory.

Вимоги:
    - Клас повинен використовувати ThreadPoolExecutor для виконання задач;
    - Перед додаванням нової задачі потрібно перевіряти, чи не перевищено ліміт задач у черзі;
    - Якщо ліміт досягнуто, виклик submit() повинен блокуватися до завершення однієї з задач;
    - Після завершення задачі необхідно звільнити слот, щоб можна було додати нову задачу.

Технічні обмеження:
    - Для обмеження кількості задач потрібно використати Semaphore.
    - Semaphore має контролювати кількість задач у стані:
        - pending
        - running
    - Необхідно уникнути втрати permit семафора, якщо submit() завершується помилкою.
    - Після завершення задачі semaphore повинен  звільнятися через callback.

Актуальність:
    Подібні механізми контролю навантаження використовуються у багатьох високонавантажених системах, де важливо
    контролювати швидкість producer.

    Без такого обмеження система може накопичувати тисячі або мільйони задач у черзі, що призводить до:
        - неконтрольованого росту використання пам'яті;
        - деградації продуктивності;
        - нестабільності системи.

    BoundedExecutor демонструє важливий принцип конкурентного програмування: контроль швидкості producer, а не лише
    кількості worker-потоків.
"""

import time

from concurrent.futures import Future
from typing import Any, Callable


class BoundedExecutor:
    """
    Executor з обмеженням кількості задач у черзі.
    Використовує Semaphore для контролю кількості задач, які можуть одночасно бути у стані pending або running.
    """

    __slots__ = ('_executor', '_semaphore')

    def __init__(self, max_workers: int, max_pending: int) -> None:
        """
        Ініціалізує executor.

        max_workers: кількість потоків worker.
        max_pending: максимальна кількість задач, які можуть бути одночасно у черзі.
        """
        # TODO: implement solution
        ...

    def submit(self, fn: Callable[..., Any], *args, **kwargs) -> Future:
        """
        Додає задачу у executor.

        Якщо ліміт pending задач досягнуто, виклик буде блокуватись, поки одна з задач не завершиться.
        """
        # TODO: implement solution
        ...

    def shutdown(self, wait: bool = True) -> None:
        """
        Завершує роботу executor.
        """
        # TODO: implement solution
        ...

    def _release_callback(self, _: Future) -> None:
        """
        Callback, який викликається післязавершення задачі.
        Звільняє один permit семафора.
        """
        # TODO: implement solution
        ...


def example_task(task_id: int) -> int:
    """
    Імітує повільну задачу.
    Кожна задача "працює" 1 секунду, щоб було видно, як executor поступово звільняє місце для нових задач.
    """
    print(f'[worker] start task {task_id}')
    time.sleep(1)
    print(f'[worker] finish task {task_id}')
    return task_id * task_id


def main():
    """
    Демонстрація роботи BoundedExecutor.

    У цьому прикладі:
        - є 2 worker-потоки;
        - максимум 4 задачі можуть бути одночасно у стані pending або running.

    Тому після додавання 4 задач submit() почне блокуватись, поки одна з задач не завершиться.
    """

    executor = BoundedExecutor(
        max_workers=2,
        max_pending=4,
    )

    futures = []

    for i in range(10):
        print(f'[producer] submitting task {i}')
        future = executor.submit(example_task, i)
        futures.append(future)
        print(f'[producer] submitted task {i}')

    executor.shutdown()
    print('All tasks finished')


if __name__ == '__main__':
    main()
