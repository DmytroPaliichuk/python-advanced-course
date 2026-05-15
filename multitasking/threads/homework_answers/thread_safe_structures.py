from threading import Lock


class Node:
    __slots__ = ('key', 'value', 'next')

    def __init__(self, key: int, value: int):
        self.key = key
        self.value = value
        self.next = None

    def __repr__(self):
        return f'Node({self.key}, {self.value})'


class LinkedList:
    def __init__(self):
        self.head: Node | None = None
        self.tail: Node | None = None
        self.count = 0

    def add_node(self, node: Node) -> None:
        if self.head is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.count += 1

    def pop_head(self) -> Node | None:
        if self.head is None:
            return None

        node = self.head
        self.head = self.head.next
        self.count -= 1
        if self.head is None:
            self.tail = None

        return node

    def find(self, key: int) -> Node | None:
        cur = self.head

        while cur:
            if cur.key == key:
                return cur
            cur = cur.next

        return None

    @property
    def count(self) -> int:
        return self._count

    @count.setter
    def count(self, value: int) -> None:
        self._count = value


class ThreatSafeLinkedList(LinkedList):
    def __init__(self):
        super().__init__()
        self._lock = Lock()

    def add_node(self, node: Node) -> None:
        with self._lock:
            return super().add_node(node)

    def pop_head(self) -> Node | None:
        with self._lock:
            return super().pop_head()

    def find(self, key: int) -> Node | None:
        with self._lock:
            return super().find(key)


class HashTable:
    def __init__(self, buckets: int = 3):
        self.buckets_count = buckets
        self.buckets = [LinkedList() for _ in range(buckets)]

    def _bucket(self, key: int) -> LinkedList:
        return self.buckets[key % self.buckets_count]

    def add(self, key: int, value: int) -> None:
        self._bucket(key).add_node(Node(key, value))

    def get(self, key: int) -> Node | None:
        return self._bucket(key).find(key)


class ThreatSafeHashTable(HashTable):
    def __init__(self, buckets: int = 3):
        self.buckets_count = buckets
        self.buckets = [LinkedList() for _ in range(buckets)]
        self._global_lock = Lock()

    def _bucket(self, key: int) -> LinkedList:
        return self.buckets[key % self.buckets_count]

    def add(self, key: int, value: int) -> None:
        with self._global_lock:
            self._bucket(key).add_node(Node(key, value))

    def get(self, key: int) -> Node | None:
        with self._global_lock:
            return self._bucket(key).find(key)


class FastThreatSafeHashTable(HashTable):
    def __init__(self, buckets: int = 3):
        self.buckets_count = buckets
        self.buckets = [ThreatSafeLinkedList() for _ in range(buckets)]

    def _bucket(self, key: int) -> ThreatSafeLinkedList:
        return self.buckets[key % self.buckets_count]

    def add(self, key, value) -> None:
        self._bucket(key).add_node(Node(key, value))

    def get(self, key) -> Node | None:
        return self._bucket(key).find(key)
