"""
Реалізувати комплексний декоратор для профілювання пам'яті в Python.

Завдання:
    Створити декоратор @memory_profile, який вимірює ключові метрики використання памʼяті.
    Формат вільний. Зробити так, як буде зручно саме тобі, щоб використовувати його для аналізу коду.
    Ідеї, що може виконувати декоратор:
        - Знімати snapshots памʼяті ДО та ПІСЛЯ виконання функції.
        - Фіксувати:
            - сумарні алокації між snapshots;
            - поточне та пікове використання памʼяті;
            - час виконання функції;
            - RSS процесу до/після.
        - Показувати топ-рядків коду, що створили найбільше алокацій.
        - Визначати "hotspots" - ймовірні місця створення копій (за кількістю та розміром алокацій).

Актуальність:
    Глибоке профілювання пам'яті - критична навичка для оптимізації Python коду,
    де великі структури даних, копії та зайві алокації можуть створювати
    приховані ботлнеки. Це дозволяє зрозуміти, де саме виникають копії,
    яка пікова памʼять потрібна коду, і як поводиться програма під навантаженням.
    Це фундаментальна техніка для систем високої пропускної здатності,
    асинхронних сервісів та задач інжинірингу даних.
"""

from __future__ import annotations

import functools
import os
import sys
import time
import tracemalloc

from collections.abc import Callable
from typing import Any, TextIO

import psutil


def memory_profile(
    func: Callable[..., Any] | None = None,
    *,
    top_n: int = 5,
    stream: TextIO | None = None,
) -> Callable[..., Any]:
    """
    Профілює пам'ять і час виконання обгорнутої функції.

    Використання:
        @memory_profile
        def foo(): ...

        @memory_profile(top_n=10)
        def bar(): ...

    Якщо tracemalloc уже увімкнено ззовні, декоратор не викликає stop() —
    щоб не зламати зовнішній профайлер.
    """

    def decorator(f: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            out = stream if stream is not None else sys.stdout
            process = psutil.Process(os.getpid())
            rss_before = process.memory_info().rss

            we_started_tracing = False
            if not tracemalloc.is_tracing():
                tracemalloc.start()
                we_started_tracing = True

            snapshot_before = tracemalloc.take_snapshot()
            start_time = time.perf_counter()

            try:
                result = f(*args, **kwargs)
            finally:
                current, peak = tracemalloc.get_traced_memory()
                elapsed = time.perf_counter() - start_time
                snapshot_after = tracemalloc.take_snapshot()
                rss_after = process.memory_info().rss

                stats = snapshot_after.compare_to(snapshot_before, 'lineno')
                filtered_stats = [stat for stat in stats if _is_interesting_stat(stat)]

                total_positive_diff = sum(stat.size_diff for stat in stats if stat.size_diff > 0)
                total_negative_diff = sum(stat.size_diff for stat in stats if stat.size_diff < 0)
                net_diff = sum(stat.size_diff for stat in stats)

                if we_started_tracing:
                    tracemalloc.stop()

                _print_report(
                    out,
                    name=f.__name__,
                    elapsed=elapsed,
                    rss_before=rss_before,
                    rss_after=rss_after,
                    current=current,
                    peak=peak,
                    total_positive_diff=total_positive_diff,
                    total_negative_diff=total_negative_diff,
                    net_diff=net_diff,
                    top_stats=filtered_stats[: max(0, top_n)],
                )

            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def _print_report(
    out: TextIO,
    *,
    name: str,
    elapsed: float,
    rss_before: int,
    rss_after: int,
    current: int,
    peak: int,
    total_positive_diff: int,
    total_negative_diff: int,
    net_diff: int,
    top_stats: list[tracemalloc.StatisticDiff],
) -> None:
    print(f'Function: {name}', file=out)
    print(f'Elapsed time: {elapsed:.6f} seconds', file=out)
    print(f'RSS before: {_bytes_to_kib(rss_before):.2f} KiB', file=out)
    print(f'RSS after: {_bytes_to_kib(rss_after):.2f} KiB', file=out)
    print(f'RSS delta: {_bytes_to_kib(rss_after - rss_before):+.2f} KiB', file=out)
    print(f'Current trace memory usage: {_bytes_to_kib(current):.2f} KiB', file=out)
    print(f'Peak memory usage: {_bytes_to_kib(peak):.2f} KiB', file=out)
    print(f'Total positive diff: {_format_size(total_positive_diff, sign=True)}', file=out)
    print(f'Total negative diff: {_format_size(total_negative_diff, sign=True)}', file=out)
    print(f'Net diff: {_format_size(net_diff, sign=True)}', file=out)

    print('\nTop allocated diffs:', file=out)
    for index, stat in enumerate(top_stats, start=1):
        if not stat.traceback:
            continue
        frame = stat.traceback[0]
        average_size = stat.size_diff / stat.count_diff if stat.count_diff else 0.0

        print(
            f'{index}. {frame.filename}:{frame.lineno} | '
            f'size diff={_format_size(stat.size_diff, sign=False)} | '
            f'count diff={stat.count_diff} | '
            f'avg={average_size:.2f} B',
            file=out,
        )


def _is_interesting_stat(stat: tracemalloc.StatisticDiff) -> bool:
    if stat.size_diff <= 0:
        return False

    if not stat.traceback:
        return False

    frame = stat.traceback[0]
    filename = frame.filename

    ignore_parts = (
        'tracemalloc',
        'psutil',
        'importlib',
        'site-packages',
    )

    return not any(part in filename for part in ignore_parts)


def _bytes_to_kib(n: int) -> float:
    return n / 1024


def _format_size(size_bytes: int, sign: bool = False) -> str:
    value = _bytes_to_kib(size_bytes)

    if sign:
        return f'{value:+.2f} KiB'

    return f'{value:.2f} KiB'


def _allocations_for_demo() -> int:
    """Створює помітні алокації: великий список + копія для порівняння у знімках."""
    n = 300_000
    buffer = [0] * n
    duplicate = list(buffer)
    return len(buffer) + len(duplicate)


if __name__ == '__main__':

    @memory_profile(top_n=8)
    def test_function() -> int:
        return _allocations_for_demo()

    test_function()
