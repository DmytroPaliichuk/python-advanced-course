"""
Billion Row Challenge - реалізація на Pandas

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

    Формат фінального результату:
        station -> "min/mean/max"

    Наприклад:
        {
            "Amsterdam": "7.1/7.1/7.1",
            "Hamburg": "12.3/12.3/12.3",
            "Kyiv": "-5.0/-1.4/2.3",
        }

Що потрібно реалізувати:
    Потрібно реалізувати pandas-based підхід, у якому:
        - файл читається не повністю, а частинами (chunks);
        - для кожного chunk-а обчислюється локальна агрегація;
        - проміжні результати зливаються у фінальну статистику;
        - для читання CSV використовується C engine;
        - фінальний результат повертається у зручному відформатованому вигляді.

Обмеження та фокус:
    - основний акцент реалізації на pandas;
    - не потрібно зчитувати весь файл одразу в один DataFrame;
    - реалізація має бути не full read + one global groupby, а chunked read + local groupby + final merge.

Актуальність:
    У попередньому варіанті цієї задачі ви реалізовували baseline-рішення на чистому Python: читали файл рядок
    за рядком, парсили дані вручну та агрегували статистику у звичайному словнику.

    Такий підхід є важливим як відправна точка, але при роботі з великими файлами він швидко впирається у вартість:
        - створення великої кількості Python-об'єктів;
        - ручного парсингу рядків;
        - обробки даних на рівні Python-циклів.

    У реальних задачах data engineering та batch processing часто використовують C-backed інструменти, які можуть:
        - швидше парсити великі текстові файли;
        - виконувати агрегації більш ефективно;
        - дозволяти працювати з даними chunk-ами.

    Одним із таких інструментів є pandas.
"""

from __future__ import annotations

import time

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class StationStats:
    min_value: float
    max_value: float
    sum_value: float
    count: int

    def mean(self) -> float:
        """
        Повертає середнє значення температури.
        """
        # TODO: implement solution
        ...


class PandasMeasurementsAggregator:
    def __init__(self, chunk_size: int = 1_000_000):
        """
        Ініціалізує агрегатор.
        chunk_size: кількість рядків, які читаються за один chunk.
        """
        # TODO: implement solution
        ...

    def process_file(self, path: Path) -> None:
        """
        Основний метод обробки файлу.
        Потрібно реалізувати:
        1. Прочитати файл через pandas.read_csv(...);
        2. Для кожного chunk виконати chunk.groupby;
        3. Об'єднати всі partial results через pd.concat().
        4. Виконати фінальну агрегацію groupby(level=0).
        """
        # TODO: implement solution
        ...

    def render_sorted(self) -> dict[str, str]:
        """
        Формує фінальний результат.
        Потрібно:
            - відсортувати станції за назвою;
            - порахувати mean через StationStats.mean();
            - сформувати рядок "min_value/mean/max_value".
        """
        # TODO: implement solution
        ...


def main():
    BASE_DIR = Path(__file__).parent

    agg = PandasMeasurementsAggregator()

    print('Running aggregation...')
    t1 = time.perf_counter()
    agg.process_file(BASE_DIR / 'data/measurements.txt')
    result = agg.render_sorted()
    t2 = time.perf_counter()

    print(f'Aggregation completed in {t2 - t1:.2f}s')
    print(f'Stations processed: {len(result)}')


if __name__ == '__main__':
    main()
