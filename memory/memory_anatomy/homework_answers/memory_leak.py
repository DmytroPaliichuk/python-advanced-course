def simulate_memory_leak(memory1: int, memory2: int) -> list[int]:
    i = 1
    while max(memory1, memory2) >= i:
        if memory1 >= memory2:
            memory1 -= i
        else:
            memory2 -= i
        i += 1
    return [i, memory1, memory2]
