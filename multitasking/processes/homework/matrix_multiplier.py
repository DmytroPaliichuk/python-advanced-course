"""
Завдання:
    Реалізувати два способи множення матриць A * B:

    1) multiply_sequentially()
       - послідовне обчислення в одному процесі;
       - класичні вкладені цикли;
       - повертає нову матрицю C.

    2) multiply_in_parallel()
       - паралельне множення з використанням multiprocessing;
       - розподіл рядків між кількома процесами;
       - використання спільного буфера пам'яті для результату.

Актуальність:
    Множення матриць - базова операція в машинному навчанні,
    статистиці, комп'ютерній графіці та обробці великих даних.
    Уміння розпаралелювати такі обчислення - ключова навичка для
    data engineers і програмістів, які працюють із високими навантаженнями.
"""

import argparse
import multiprocessing as mp
import random
import time

from typing import Any, Callable


class MatrixGenerator:
    """Клас-утиліта для генерації випадкових матриць."""

    @staticmethod
    def random_matrix(rows: int, cols: int) -> list[list[float]]:
        """
        Створює матрицю розміром rows x cols,
        заповнену випадковими числами з інтервалу [0, 1).
        """
        return [[random.random() for _ in range(cols)] for _ in range(rows)]


class MatrixMultiplier:
    """
    Клас для множення матриць послідовно та паралельно.

    При створенні об’єкта перевіряє коректність розмірів матриць.
    Після цього можна викликати:
      - multiply_sequentially() - послідовне множення;
      - multiply_in_parallel() - паралельне множення з використанням кількох процесів.
    """

    def __init__(self, A: list[list[float]], B: list[list[float]]):
        self.A = A
        self.B = B
        self._validate_dimensions()

    def _validate_dimensions(self) -> None:
        """
        Перевіряє, що розміри матриць сумісні для множення A * B.

        Якщо кількість стовпчиків у A не дорівнює кількості рядків у B, ValueError.
        """
        if not self.A or not self.A[0] or not self.B or not self.B[0]:
            raise ValueError('Матриці не можуть бути порожніми.')

        if len(self.A[0]) != len(self.B):
            raise ValueError(f'Некоректні розміри: {len(self.A)}*{len(self.A[0])} * {len(self.B)}*{len(self.B[0])}')

    def multiply_sequentially(self) -> list[list[float]]:
        """
        Обчислює добуток матриць A * B послідовно в одному процесі. Повертає нову матрицю C.
        """
        # TODO: implement solution
        ...

    def multiply_in_parallel(self) -> list[list[float]]:
        """
        Обчислює добуток матриць A * B паралельно в кількох процесах.
        """
        # TODO: implement solution
        ...


# -------------------------------
# Подивитися на роботу програми:
# -------------------------------


class PerformanceTester:
    """
    Клас-утиліта для вимірювання часу виконання функції.
    """

    @staticmethod
    def measure(func: Callable[[], Any], runs: int = 3) -> float:
        """
        Вимірює середній час виконання функції func за runs повторів.

        Повертає середній час у секундах.
        """
        total = 0.0
        for _ in range(runs):
            start = time.perf_counter()
            func()
            total += time.perf_counter() - start
        return total / runs


def main() -> None:
    """
    Створює випадкові матриці, перемножує їх послідовно та паралельно і порівнює середній час роботи обох підходів.
    """
    parser = argparse.ArgumentParser(description='Порівняння послідовного та паралельного множення матриць.')
    parser.add_argument(
        '--rows',
        type=int,
        default=200,
        help='Кількість рядків матриці A (за замовчуванням: 200).',
    )
    parser.add_argument(
        '--cols',
        type=int,
        default=200,
        help='Кількість стовпчиків матриці A / рядків матриці B (за замовчуванням: 200).',
    )
    parser.add_argument(
        '--eval-runs',
        type=int,
        default=1,
        help='Скільки разів повторити вимірювання для усереднення (за замовчуванням: 1).',
    )
    args = parser.parse_args()

    A = MatrixGenerator.random_matrix(args.rows, args.cols)
    B = MatrixGenerator.random_matrix(args.cols, args.rows)

    multiplier = MatrixMultiplier(A, B)

    # Невеликий прогрів і перевірка коректності:
    seq_res = multiplier.multiply_sequentially()
    par_res = multiplier.multiply_in_parallel()
    if seq_res != par_res:
        raise RuntimeError('Послідовний та паралельний результати не збігаються!')

    # Бенчмарк
    seq_time = PerformanceTester.measure(multiplier.multiply_sequentially, args.eval_runs)
    par_time = PerformanceTester.measure(multiplier.multiply_in_parallel, args.eval_runs)

    print(f'Середній час послідовно: {seq_time * 1000:.2f} мс')
    print(f'Середній час паралельно: {par_time * 1000:.2f} мс')
    print(f'Прискорення:             {seq_time / par_time:.2f}x')
    print(f'Ефективність на ядро:    {100 * (seq_time / par_time) / mp.cpu_count():.2f}%')


if __name__ == '__main__':
    """
    На Linux і macOS використовуємо стартовий метод 'fork', оскільки він
    створює процеси значно швидше за 'spawn' завдяки механізму copy-on-write (COW).
    У цьому режимі дочірні процеси миттєво отримують доступ до імпортованих
    модулів та даних, що особливо критично для великих матриць.

    На Windows доступний лише 'spawn', який перезапускає інтерпретатор і
    потребує серіалізації даних, тому працює значно повільніше.

    На Linux 'fork' має стояти за замовчуванням.
    На macOS часто за замовчуванням 'spawn' через політику безпеки Apple.
    """
    mp.set_start_method('fork')
    main()
