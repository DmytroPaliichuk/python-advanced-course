"""
Завдання:
    Реалізувати процесобезпечний кеш на основі спільної памʼяті (SharedMemory),
    який дозволяє декільком процесам обмінюватися вже обчисленими результатами
    без дублювання важких CPU-інтенсивних обчислень.

    У цій роботі кешування виконується для функції count_primes_up_to(n),
    яка обчислює кількість простих чисел ≤ n за допомогою решета Ератосфена.
    Це повністю детермінована, чиста функція, результат якої ідеально
    підходить для збереження та повторного використання між процесами.

    Чому SharedMemory?
        - multiprocessing не ділить об’єкти між процесами (кожен має свій Python heap);
        - Manager().dict() працює повільніше, бо всі операції йдуть через IPC;
        - SharedMemory дозволяє створювати спільні масиви без копіювання, які доступні всім процесам одночасно;
        - інформація структурується в простих NumPy-масивах: keys[], values[], states[].

    Завдання складається з трьох частин:
        1. SharedCacheStorage
            - створює спільні сегменти памʼяті;
            - ініціалізує масиви keys / values / states;
            - надає worker-процесам дескриптор (імена сегментів + capacity).

        2. SharedPrimeCache
            - підʼєднується до існуючих сегментів SharedMemory;
            - реалізує процесобезпечний протокол доступу до кешу:
                HIT - значення вже є;
                WAIT - інший процес зараз рахує;
                MISS - ні в кого не обчислено, процес резервує слот;
            - забезпечує, що кожне n буде обчислено лише 1 раз.

        3. Worker-процеси
            - отримують значення через get_or_compute(n);
            - не дублюють роботу сусідніх процесів;
            - не блокують один одного довше, ніж потрібно.

    Що потрібно реалізувати:
        - коректну логіку пошуку слотів (_find_ready, _find_in_progress);
        - резервування слоту (_reserve_slot);
        - атомарний протокол get_or_compute із правильним використанням блокування.

    Актуальність:
        Цей патерн використовується в реальних продакшен-системах:
            - паралельні ETL-пайплайни;
            - CPU-bound наукові обчислення;
            - рендеринг/обробка зображень;
            - ML-процеси, які кешують важкі кроки;
            - високопродуктивні веб-сервіси, де кілька воркерів розділяють кеш.

        Спільна памʼять дозволяє суттєво зменшити час обчислень та уникнути
        дублювання важких задач, забезпечуючи при цьому коректну синхронізацію
        між процесами без використання повільних IPC-примітивів.
"""

import math
import multiprocessing

from enum import IntEnum
from multiprocessing import shared_memory
from typing import Generator

import numpy as np


class CacheSlotState(IntEnum):
    EMPTY = 0
    READY = 1
    IN_PROGRESS = 2


def count_primes_up_to(n: int) -> int:
    """
    Обчислює кількість простих чисел, що не перевищують n (включно),
    використовуючи оптимізоване решето Ератосфена.

    Це CPU-інтенсивна операція, яка добре демонструє переваги кешування
    та multiprocessing: для великих n її обчислення займає помітний час,
    але результат є чистою функцією (англ. deterministic, pure) і тому ідеально
    підходить для повторного використання між процесами.

    Потребує O(n) памʼяті. Виконується за приблизно O(n log log n).
    """
    if n < 2:
        return 0

    sieve = np.ones(n + 1, dtype=bool)
    sieve[:2] = False

    limit = int(math.isqrt(n))
    for p in range(2, limit + 1):
        if sieve[p]:
            sieve[p * p : n + 1 : p] = False

    return int(sieve.sum())


class SharedCacheStorage:
    def __init__(self, capacity: int):
        self.capacity = capacity

        # ОС може виділити більший блок - це нормально
        self.keys_shm = shared_memory.SharedMemory(create=True, size=capacity * 8)
        self.values_shm = shared_memory.SharedMemory(create=True, size=capacity * 8)
        self.states_shm = shared_memory.SharedMemory(create=True, size=capacity * 1)

        # Ініціалізація строго в межах capacity
        np.ndarray((capacity,), dtype=np.int64, buffer=self.keys_shm.buf)[:] = -1
        np.ndarray((capacity,), dtype=np.int64, buffer=self.values_shm.buf)[:] = 0
        np.ndarray((capacity,), dtype=np.uint8, buffer=self.states_shm.buf)[:] = 0

    def descriptor(self) -> tuple[str, str, str, int]:
        """
        Повертає дані, необхідні підпроцесам для підʼєднання до спільної памʼяті.

        Обʼєкти SharedMemory не можна передавати між процесами напряму
        (вони не є pickle-safe), тому підпроцеси повинні самостійно
        підʼєднатися до існуючих сегментів за їхніми іменами.
        Цей метод забезпечує мінімальний набір метаданих, потрібний
        для коректного під’єднання до спільних масивів.
        """
        return (
            self.keys_shm.name,
            self.values_shm.name,
            self.states_shm.name,
            self.capacity,
        )

    def close(self) -> None:
        """
        Закриває та видаляє всі сегменти спільної памʼяті.

        Викликається лише в головному процесі, після того як
        усі воркер-процеси завершили роботу і більше не потребують
        доступу до спільного кешу.
            - shm.close() - закриває локальний файловий дескриптор на сегмент спільної памʼяті;
            - shm.unlink() - фізично видаляє сегмент із системи.
        """
        for shm in (self.keys_shm, self.values_shm, self.states_shm):
            shm.close()
            shm.unlink()


class SharedPrimeCache:
    def __init__(
        self,
        keys_name: str,
        values_name: str,
        states_name: str,
        capacity: int,
        lock: multiprocessing.Lock,
    ):
        self.capacity = capacity
        self.lock = lock

        # Підʼєднання до існуючих сегментів
        self._keys_shm = shared_memory.SharedMemory(name=keys_name)
        self._values_shm = shared_memory.SharedMemory(name=values_name)
        self._states_shm = shared_memory.SharedMemory(name=states_name)

        # Масиви строго розміром capacity
        self._keys = np.ndarray((capacity,), dtype=np.int64, buffer=self._keys_shm.buf)
        self._values = np.ndarray((capacity,), dtype=np.int64, buffer=self._values_shm.buf)
        self._states = np.ndarray((capacity,), dtype=np.uint8, buffer=self._states_shm.buf)

    def _find_ready(self, n: int) -> int:
        """
        Знайти індекс слоту, де вже збережено готове значення для n.

        Завдання:
            - проаналізувати масиви self._keys та self._states;
            - знайти всі індекси, де:
                  states[i] == READY і keys[i] == n;
            - повернути перший знайдений індекс або -1, якщо відповідного слоту нема.
        """
        # TODO: implement solution
        ...

    def _find_in_progress(self, n: int) -> int:
        """
        Знайти індекс слоту, e якому вже триває обчислення значення для n (виконує інший процес).

        Завдання:
            - знайти індекси, де:
                  states[i] == IN_PROGRESS і keys[i] == n;
            - повернути перший індекс або -1, якщо n зараз не обчислюється.
        """
        # TODO: implement solution
        ...

    def _reserve_slot(self, n: int) -> int:
        """
        Зарезервувати слот під обчислення для n.

        Завдання:
            - знайти будь-який вільний слот, де states[i] == EMPTY;
            - якщо таких немає - використати слот 0 (найпростіша стратегія);
            - записати:
                  keys[idx] = n
                  states[idx] = IN_PROGRESS
            - повернути номер слоту.
        """
        # TODO: implement solution
        ...

    def get_or_compute(self, n: int) -> int:
        """
        Головний протокол доступу до кешу.

        Завдання:
            Реалізувати повну логіку взаємодії між процесами так, щоб:

            1. Якщо значення для n вже готове:
                   -> повернути його (стан READY).

            2. Якщо інший процес зараз обчислює n:
                   -> вийти з критичної секції (lock) та зачекати, періодично перевіряючи стан.

            3. Якщо значення відсутнє й ніхто його не рахує:
                   -> зарезервувати слот через _reserve_slot(n) (встановити IN_PROGRESS) та перейти до обчислення.

            4. Після завершення обчислення:
                   -> записати результат у values[];
                   -> змінити стан на READY.

            Важливо:
                - не забути про блокування для усієї роботи з пошуком/резервуванням слоту, щоб уникнути race conditions;
                - очікування виконується без lock, щоб не блокувати інші процеси.

            Для наочності можна логувати процес виконання:
                print(f'[PID {os.getpid()}] HIT   n={n}')
                print(f'[PID {os.getpid()}] WAIT  n={n}')
                print(f'[PID {os.getpid()}] MISS  n={n}, slot={slot}')
                print(f'[PID {os.getpid()}] CALC  n={n}, primes={result}')
        """
        # TODO: implement solution
        ...

    def snapshot(self) -> Generator[tuple[int, int, int], None, None]:
        return ((int(self._keys[i]), int(self._values[i]), int(self._states[i])) for i in range(self.capacity))

    def close(self) -> None:
        self._keys_shm.close()
        self._values_shm.close()
        self._states_shm.close()


# -------------------------------
# Подивитися на роботу програми:
# -------------------------------


def worker_task(
    n: int,
    desc: tuple[str, str, str, int],
    lock: multiprocessing.Lock,
) -> tuple[int, int]:
    cache = SharedPrimeCache(lock=lock, *desc)
    result = cache.get_or_compute(n)
    cache.close()
    return n, result


def main() -> None:
    print('=== SharedMemory Multiprocess Cache ===')

    storage = SharedCacheStorage(capacity=32)
    desc = storage.descriptor()
    manager = multiprocessing.Manager()
    lock = manager.Lock()

    keys = (80_000, 120_000, 80_000, 50_000, 120_000, 300_000)
    print('Workload:', keys)

    with multiprocessing.Pool(4) as pool:
        results = pool.starmap(worker_task, ((n, desc, lock) for n in keys))

    print('\nResults:')
    for n, v in results:
        print(f'  n={n} -> primes={v}')

    print('\nCache snapshot:')
    c = SharedPrimeCache(*desc, lock)
    snap = c.snapshot()

    for i, (k, v, s) in enumerate(snap):
        if s != 0:
            print(f'  slot {i}: key={k}, value={v}, state={s}')

    c.close()
    storage.close()


if __name__ == '__main__':
    main()
