"""
Billion Row Challenge - реалізація на Pure Python

Завдання:
    Є великий текстовий файл з вимірюваннями температури.

    Кожен рядок має формат:
        <назва_станції>;<температура>

    Температура задана з точністю до 1 знака після коми, наприклад:
        Hamburg;12.0
        Istanbul;23.0

    Потрібно прочитати файл та для кожної станції порахувати:
        - min температуру;
        - mean температуру;
        - max температуру.

    Після цього потрібно вивести результат, відсортований за назвою станції за зростанням.

Вхід:
    - шлях до файлу measurements.txt;
    - файл може бути дуже великим (сотні МБ / ГБ).

Вихід:
    Для кожної станції один рядок (або один dict/структура для подальшого друку), де значення представлені у форматі:
        <station>: <min>/<mean>/<max>

    І всі числа відформатовані до 1 знака після коми.

Вимоги:
    - Реалізація має бути на чистому Python (без pandas/polars/duckdb тощо).
      Це базова версія, яка потрібна як “відправна точка” для наступних оптимізацій;
    - Працюємо потоково: читаємо файл рядок за рядком, не зберігаємо всі рядки в памʼяті;
    - Можна додавати додаткові методи в клас за потреби.

Актуальність:
    У реальних системах обробки даних (data engineering, лог‑аналіз, телеметрія, фінансові системи)
    часто доводиться працювати з дуже великими текстовими файлами - від сотень мегабайт до десятків гігабайт.

    Наївні реалізації, які створюють багато тимчасових об'єктів або читають весь файл у памʼять,
    швидко стають вузьким місцем системи.

    Це домашнє завдання є відправною точкою для серії оптимізацій. Його мета:
        - показати базову реалізацію задачі на чистому Python;
        - навчитися працювати з великими файлами потоково (streaming);
        - зрозуміти, де у простій реалізації виникають алокації (створення рядків, float, записів у dict тощо);
        - підготувати основу для подальших оптимізацій.

    У наступних ітераціях цієї задачі ми будемо досліджувати різні підходи до оптимізації такої обробки, зокрема:
        - зменшення кількості алокацій;
        - більш ефективний парсинг рядків;
        - використання memory-mapped файлів (mmap);
        - паралельну обробку даних.
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from memory.fragments_and_copies.homework.brc.generator import GeneratorConfig, MeasurementsGenerator


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    @classmethod
    def create(cls, value: float) -> 'StationStats':
        """
        Створює початкову статистику для нової станції.
        Використовуйте передане значення температури як перший вимір.
        """
        # TODO: implement solution
        ...

    def add(self, value: float) -> None:
        """
        Додає нове температурне значення до статистики станції.
        """
        # TODO: implement solution
        ...

    def mean(self) -> float:
        """
        Повертає середнє значення температури для станції.
        """
        # TODO: implement solution
        ...


class MeasurementsAggregator:
    def __init__(self):
        """
        Ініціалізує структуру для збереження статистики по станціях.
        """
        # TODO: implement solution
        ...

    def process_file(self, path: str) -> None:
        """
        Відкриває файл з вимірюваннями та передає його у потокову обробку.
        """
        # TODO: implement solution
        ...

    def _process_stream(self, stream: TextIO) -> None:
        """
        Читає потік рядок за рядком та оновлює статистику станцій.

        Кожен рядок має формат:
            <station>;<temperature>
        """
        # TODO: implement solution
        ...

    def render_sorted(self) -> dict[str, str]:
        """
        Формує фінальний результат.

        Потрібно:
        - відсортувати станції за назвою
        - для кожної станції сформувати рядок у форматі:
              min/mean/max
        - повернути словник:
              station -> "min_value/mean/max_value"
        """
        # TODO: implement solution
        ...


def main():
    BASE_DIR = Path(__file__).parent

    cfg = GeneratorConfig(
        rows=1_000_000_000,
        output_path=Path(BASE_DIR / 'data/measurements.txt'),
        stations_csv=Path(BASE_DIR / 'data/weather_stations.csv'),
        batch_size=10_000,
    )

    print('Generating dataset...')
    t0 = time.perf_counter()
    MeasurementsGenerator(cfg).generate()
    t1 = time.perf_counter()

    print(f'Dataset generated in {t1 - t0:.2f}s')

    agg = MeasurementsAggregator()

    print('Running aggregation...')
    t2 = time.perf_counter()
    agg.process_file(BASE_DIR / 'data/measurements.txt')
    result = agg.render_sorted()
    t3 = time.perf_counter()

    print(f'Aggregation completed in {t3 - t2:.2f}s')
    print(f'Stations processed: {len(result)}')


if __name__ == '__main__':
    main()
