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
