import unittest

from multitasking.gil.homework.single_threading import get_task_order


class TestSingleThreadedCPU(unittest.TestCase):
    def test_basic_example(self):
        tasks = [[1, 2], [2, 4], [3, 2], [4, 1]]
        self.assertEqual(get_task_order(tasks), [0, 2, 3, 1])

    def test_all_same_enqueue_time(self):
        # усі задачі доступні одночасно -> порядок за processing_time
        tasks = [[7, 10], [7, 12], [7, 5], [7, 4], [7, 2]]
        self.assertEqual(get_task_order(tasks), [4, 3, 2, 0, 1])

    def test_cpu_idle_then_continue(self):
        # CPU має простоювати між задачами
        tasks = [[5, 3], [10, 2], [15, 1]]
        self.assertEqual(get_task_order(tasks), [0, 1, 2])

    def test_processing_tie_breaker(self):
        # однаковий processing_time -> обираємо за індексом
        tasks = [[0, 5], [2, 5], [4, 5]]
        self.assertEqual(get_task_order(tasks), [0, 1, 2])

    def test_mixed_enqueue_and_processing(self):
        tasks = [[2, 3], [1, 4], [2, 2], [1, 1]]
        # задачі надходять у два різні моменти часу
        self.assertEqual(get_task_order(tasks), [3, 2, 0, 1])

    def test_single_task(self):
        tasks = [[5, 10]]
        self.assertEqual(get_task_order(tasks), [0])

    def test_large_processing_time(self):
        tasks = [[0, 100000], [0, 1]]
        self.assertEqual(get_task_order(tasks), [1, 0])

    def test_large_gap_idle(self):
        tasks = [[0, 3], [100, 1]]
        self.assertEqual(get_task_order(tasks), [0, 1])
