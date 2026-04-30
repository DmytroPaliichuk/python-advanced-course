from heapq import heappop, heappush
from typing import Iterable


def get_task_order(tasks: Iterable[Iterable[int]]) -> Iterable[int]:
    result = []
    heap = []
    current_time = 0

    sorted_tasks = sorted((task, idx) for idx, task in enumerate(tasks))

    for (enqueue_time, processing_time), idx in sorted_tasks:
        while heap and current_time < enqueue_time:
            proc_time, task_idx, task_enqueue = heappop(heap)
            current_time = max(task_enqueue, current_time) + proc_time
            result.append(task_idx)
        heappush(heap, (processing_time, idx, enqueue_time))

    result.extend(task_idx for _, task_idx, _ in sorted(heap))

    return result


def get_task_order_with_pointer(tasks: Iterable[Iterable[int]]) -> list[int]:
    indexed_tasks = sorted(
        (enqueue_time, processing_time, idx) for idx, (enqueue_time, processing_time) in enumerate(tasks)
    )

    result: list[int] = []
    heap: list[tuple[int, int]] = []

    current_time = 0
    i = 0
    total_tasks = len(indexed_tasks)

    while i < total_tasks or heap:
        if not heap and current_time < indexed_tasks[i][0]:
            current_time = indexed_tasks[i][0]

        while i < total_tasks and indexed_tasks[i][0] <= current_time:
            enqueue_time, processing_time, idx = indexed_tasks[i]
            heappush(heap, (processing_time, idx))
            i += 1

        processing_time, idx = heappop(heap)
        current_time += processing_time
        result.append(idx)

    return result
