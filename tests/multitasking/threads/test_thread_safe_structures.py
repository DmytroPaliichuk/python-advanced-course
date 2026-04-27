import threading
import unittest

from multitasking.threads.homework.thread_safe_structures import (
    FastThreatSafeHashTable,
    HashTable,
    LinkedList,
    Node,
    ThreatSafeHashTable,
    ThreatSafeLinkedList,
)


class TestThreadSafeStructures(unittest.TestCase):
    def test_linked_list_add_and_find(self):
        ll = LinkedList()
        ll.add_node(Node(1, 10))
        ll.add_node(Node(2, 20))

        self.assertEqual(ll.count, 2)
        self.assertEqual(ll.find(1).value, 10)
        self.assertEqual(ll.find(2).value, 20)
        self.assertIsNone(ll.find(999))

    def test_linked_list_pop_head(self):
        ll = LinkedList()
        ll.add_node(Node(1, 10))
        ll.add_node(Node(2, 20))

        head = ll.pop_head()
        self.assertEqual(head.key, 1)
        self.assertEqual(ll.count, 1)

        head = ll.pop_head()
        self.assertEqual(head.key, 2)
        self.assertEqual(ll.count, 0)

        self.assertIsNone(ll.pop_head())

    def test_safe_linked_list_threaded_insert(self):
        ll = ThreatSafeLinkedList()

        def worker(start, end):
            for i in range(start, end):
                ll.add_node(Node(i, i))

        t1 = threading.Thread(target=worker, args=(1, 500))
        t2 = threading.Thread(target=worker, args=(500, 1000))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self.assertEqual(ll.count, 999)
        self.assertIsNotNone(ll.find(1))
        self.assertIsNotNone(ll.find(500))
        self.assertIsNotNone(ll.find(999))

    def test_hash_table_basic(self):
        ht = HashTable(buckets=3)
        ht.add(1, 10)
        ht.add(2, 20)
        ht.add(3, 30)

        self.assertEqual(ht.get(1).value, 10)
        self.assertEqual(ht.get(2).value, 20)
        self.assertEqual(ht.get(3).value, 30)

    def test_safe_hash_table_threaded_insert(self):
        ht = ThreatSafeHashTable(buckets=3)

        def inserter(keys):
            for k in keys:
                ht.add(k, 1)

        keys1 = range(1, 600)
        keys2 = range(600, 1200)

        t1 = threading.Thread(target=inserter, args=(keys1,))
        t2 = threading.Thread(target=inserter, args=(keys2,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        for key in [1, 500, 1100]:
            self.assertEqual(ht.get(key).value, 1)

    def test_fast_safe_hash_table_parallelism(self):
        ht = FastThreatSafeHashTable(buckets=3)

        def inserter(start):
            for k in range(start, start + 1000, 3):
                ht.add(k, 1)

        t1 = threading.Thread(target=inserter, args=(1,))
        t2 = threading.Thread(target=inserter, args=(2,))
        t3 = threading.Thread(target=inserter, args=(3,))

        t1.start()
        t2.start()
        t3.start()
        t1.join()
        t2.join()
        t3.join()

        count = 0
        for i in range(1, 1000):
            node = ht.get(i)
            if node:
                count += 1

        self.assertGreater(count, 900)

    def test_fast_hash_table_read_write(self):
        ht = FastThreatSafeHashTable(buckets=3)
        read_results = []
        writer_started = threading.Event()

        def writer():
            writer_started.set()
            for i in range(1, 2000):
                ht.add(i, 1)

        def reader():
            writer_started.wait()

            current_sum = 0
            for i in range(1, 2000):
                node = ht.get(i)
                if node is not None:
                    current_sum += node.value

            read_results.append(current_sum)

        writer_thread = threading.Thread(target=writer)
        reader_thread = threading.Thread(target=reader)

        writer_thread.start()
        reader_thread.start()
        writer_thread.join()
        reader_thread.join()

        self.assertEqual(len(read_results), 1)
        self.assertGreaterEqual(read_results[0], 0)
        self.assertLessEqual(read_results[0], 1999)

        for key in range(1, 2000):
            node = ht.get(key)
            self.assertIsNotNone(node)
            self.assertEqual(node.value, 1)
