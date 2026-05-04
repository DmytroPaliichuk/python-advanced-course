"""
Billion Row Challenge - реалізація на процесах.

Завдання:
    Файл містить температурні вимірювання у форматі:
        <station>;<temperature>

    Приклад:
        Hamburg;12.3
        Kyiv;-5.0
        Amsterdam;7.1
        Kyiv;2.3

    Для кожної станції потрібно обчислити:
        min / mean / max

Мета домашнього завдання:
    - навчитися використовувати multiprocessing;
    - навчитися розбивати великі файли на частини;
    - обробляти дані потоково;
    - мінімізувати зайві алокації.

Обмеження:
    - використовувати лише стандартну бібліотеку Python;
    - не використовувати pandas / numpy тощо;
    - не читати файл повністю в памʼять;
    - уникати зайвих копій даних;
    - можна додавати додаткові методи в клас за потреби.

Актуальність:
    У системах обробки даних (data engineering, лог-аналіз, телеметрія, фінансові системи) часто доводиться працювати
    з дуже великими текстовими файлами - від сотень мегабайт до десятків гігабайт.
    Навіть якщо алгоритм написаний ефективно, обробка може бути обмежена одним CPU-ядром.
    Для таких задач можна використати multiprocessing - підхід, який дозволяє розподілити роботу між кількома процесами.
    Кожен процес працює незалежно і використовує окреме CPU-ядро.

"""

import multiprocessing as mp
import time

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    @classmethod
    def create(cls, value: float) -> 'StationStats':
        """
        Створює початкову статистику для станції.
        Викликається при першому зустрічанні станції у даних.
        """
        # TODO: implement solution
        ...

    def add(self, value: float) -> None:
        """
        Додає нове значення температури до статистики.
        """
        # TODO: implement solution
        ...

    def merge(self, other: 'StationStats') -> None:
        """
        Об'єднує статистику з іншого процесу.
        Використовується при merge результатів worker-процесів.
        """
        # TODO: implement solution
        ...

    def mean(self) -> float:
        """
        Обчислює середню температуру.
        """
        # TODO: implement solution
        ...


class ParallelMeasurementsAggregator:
    def __init__(self, workers: int | None = None):
        """
        Ініціалізує агрегатор.
        Якщо workers не задано — використовується кількість CPU ядер.
        """
        # TODO: implement solution
        ...

    @staticmethod
    def _process_partition(
        path: Path,
        start_offset: int,
        end_offset: int,
    ) -> dict[bytes, StationStats]:
        """
        Worker-функція.

        Кожен процес:
            1. відкриває файл
            2. переходить до start offset
            3. читає рядки до end offset
            4. обчислює локальну статистику

        Повертає словник:
            station -> StationStats
        """
        # TODO: implement solution
        ...

    def process_file(self, path: Path) -> dict[bytes, StationStats]:
        """
        Основний метод обробки файлу.

        Потрібно:
        1. визначити розмір файлу
        2. розбити файл на partitions
        3. запустити multiprocessing Pool
        4. об'єднати результати worker-процесів
        """
        # TODO: implement solution
        ...

    @staticmethod
    def render_sorted(stats: dict[bytes, StationStats]) -> dict[str, str]:
        """
        Формує фінальний результат.

        Потрібно:

        - відсортувати станції
        - повернути результат у форматі:

            station -> "min_value/mean/max_value"
        """
        # TODO: implement solution
        ...


def main() -> None:
    mp.set_start_method('fork')

    BASE_DIR = Path(__file__).parent

    path = Path(BASE_DIR / 'data/measurements.txt')

    print('Running aggregation...')
    t2 = time.perf_counter()

    aggregator = ParallelMeasurementsAggregator()
    stats = aggregator.process_file(path)
    result = aggregator.render_sorted(stats)

    t3 = time.perf_counter()

    print(f'Aggregation completed in {t3 - t2:.2f}s')
    print(f'Stations processed: {len(result)}')


if __name__ == '__main__':
    main()
