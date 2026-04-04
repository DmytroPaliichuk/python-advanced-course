import unittest

from memory.memory_anatomy.homework.allocator import Allocator


class TestAllocator(unittest.TestCase):
    def test_basic_allocation(self):
        alloc = Allocator(5)
        self.assertEqual(alloc.allocate(1, 1), 0)
        self.assertEqual(alloc.allocate(1, 2), 1)
        self.assertEqual(alloc.allocate(1, 3), 2)

    def test_allocate_no_space(self):
        alloc = Allocator(3)
        alloc.allocate(1, 1)
        alloc.allocate(1, 2)
        alloc.allocate(1, 3)
        self.assertEqual(alloc.allocate(1, 4), -1)

    def test_allocate_exact_fit(self):
        alloc = Allocator(4)
        self.assertEqual(alloc.allocate(4, 1), 0)
        self.assertEqual(alloc.allocate(1, 2), -1)

    def test_free_single_block(self):
        alloc = Allocator(5)
        alloc.allocate(2, 10)
        self.assertEqual(alloc.free_memory(10), 2)
        self.assertEqual(alloc.allocate(5, 1), 0)

    def test_free_multiple_blocks_same_owner(self):
        alloc = Allocator(10)
        alloc.allocate(1, 7)
        alloc.allocate(2, 7)
        alloc.allocate(1, 7)
        self.assertEqual(alloc.free_memory(7), 4)

        self.assertEqual(alloc.allocate(10, 99), 0)

    def test_fragmentation_behavior(self):
        alloc = Allocator(9)
        alloc.allocate(3, 1)
        alloc.allocate(3, 2)
        alloc.free_memory(1)
        self.assertEqual(alloc.allocate(4, 3), -1)
        self.assertEqual(alloc.allocate(3, 3), 0)

    def test_free_nonexistent_id(self):
        alloc = Allocator(5)
        alloc.allocate(2, 1)
        self.assertEqual(alloc.free_memory(999), 0)

    def test_allocations_match_example(self):
        alloc = Allocator(10)
        self.assertEqual(alloc.allocate(1, 1), 0)
        self.assertEqual(alloc.allocate(1, 2), 1)
        self.assertEqual(alloc.allocate(1, 3), 2)
        self.assertEqual(alloc.free_memory(2), 1)
        self.assertEqual(alloc.allocate(3, 4), 3)
        self.assertEqual(alloc.allocate(1, 1), 1)
        self.assertEqual(alloc.allocate(1, 1), 6)
        self.assertEqual(alloc.free_memory(1), 3)
        self.assertEqual(alloc.allocate(10, 2), -1)
        self.assertEqual(alloc.free_memory(7), 0)
