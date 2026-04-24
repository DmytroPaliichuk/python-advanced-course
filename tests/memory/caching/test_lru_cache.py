import unittest

from memory.caching.homework.lru_cache import LRUCache


class TestLRUCache(unittest.TestCase):
    def test_example_case(self):
        lru = LRUCache(2)

        lru.put(1, 1)  # cache = {1=1}
        lru.put(2, 2)  # cache = {1=1, 2=2}

        self.assertEqual(lru.get(1), 1)

        lru.put(3, 3)  # evicts key 2 -> cache = {1=1, 3=3}
        self.assertEqual(lru.get(2), -1)  # returns -1 (not found)

        lru.put(4, 4)  # evicts key 1 -> cache = {4=4, 3=3}
        self.assertEqual(lru.get(1), -1)
        self.assertEqual(lru.get(3), 3)
        self.assertEqual(lru.get(4), 4)

    def test_single_put_get(self):
        lru = LRUCache(1)
        lru.put(10, 100)
        self.assertEqual(lru.get(10), 100)

    def test_overwrite_value(self):
        lru = LRUCache(2)
        lru.put(1, 1)
        lru.put(1, 10)  # overwrite existing
        self.assertEqual(lru.get(1), 10)

    def test_eviction_order(self):
        lru = LRUCache(2)
        lru.put(1, 1)
        lru.put(2, 2)
        lru.get(1)  # now 2 is LRU

        lru.put(3, 3)  # evict key 2
        self.assertEqual(lru.get(2), -1)
        self.assertEqual(lru.get(1), 1)
        self.assertEqual(lru.get(3), 3)

    def test_capacity_one(self):
        lru = LRUCache(1)
        lru.put(1, 1)
        lru.put(2, 2)  # evicts key 1
        self.assertEqual(lru.get(1), -1)
        self.assertEqual(lru.get(2), 2)
