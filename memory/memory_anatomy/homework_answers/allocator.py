class Allocator:
    def __init__(self, n: int):
        self.memory = [-1] * n
        self.n = n

    def allocate(self, size: int, alloc_id: int) -> int:
        available = 0
        for i in range(self.n):
            if self.memory[i] == -1:
                available += 1
            else:
                available = 0
            if available == size:
                for j in range(i - available + 1, i + 1):
                    self.memory[j] = alloc_id
                return i - available + 1
        return -1

    def free_memory(self, alloc_id: int) -> int:
        count = 0
        for i in range(self.n):
            if self.memory[i] == alloc_id:
                count += 1
                self.memory[i] = -1
        return count
