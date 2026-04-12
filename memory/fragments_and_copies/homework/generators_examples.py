"""
List vs generator — what matters for EventAggregator.

1) List: materialized in RAM; you can iterate many times; len(), indexing.
2) Generator: lazy; one pass; no len/index until you exhaust or tee/copy.
"""

from collections.abc import Generator
from time import perf_counter

from memory.fragments_and_copies.homework.memory_profiler import memory_profile

_list = [i for i in range(100_000)]


@memory_profile
def do_something_list(lst: list[int]) -> list[int]:
    result = []
    for i in lst:
        result.append(i * 2)
    return result


@memory_profile
def do_something_generator(gen: list[int]) -> Generator[int]:
    for i in gen:
        yield i * 2


if __name__ == '__main__':
    t0 = perf_counter()
    lst = do_something_list(_list)
    _ = [i for i in lst]
    t1 = perf_counter()
    print(f'List time: {t1 - t0:.4f}s')

    print('=' * 100)

    t0 = perf_counter()
    gen = do_something_generator(_list)
    _ = [i for i in gen]
    t1 = perf_counter()
    print(f'Generator time: {t1 - t0:.4f}s')
    print('=' * 100)
