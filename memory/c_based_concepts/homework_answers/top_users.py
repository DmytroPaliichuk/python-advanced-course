import heapq

from collections import defaultdict


def top_users(file_path: str, top_n: int = 5) -> list[tuple[str, float]]:
    totals: defaultdict = defaultdict(int)

    with open(file_path, 'r') as f:
        for line in f:
            try:
                _, user_id, _, value = line.strip().split(',')
                totals[user_id] += float(value)
            except Exception:
                continue

    top = heapq.nlargest(top_n, totals.items(), key=lambda x: x[1])
    return top
