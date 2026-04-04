import unittest

from memory.memory_anatomy.homework.memory_leak import simulate_memory_leak


class TestMemoryLeakSimulation(unittest.TestCase):
    def test_handles_examples_from_problem_statement(self):
        result = simulate_memory_leak(2, 2)
        self.assertEqual(result, [3, 1, 0])

        result = simulate_memory_leak(8, 11)
        self.assertEqual(result, [6, 0, 4])

    def test_handles_zero_initial_memory1(self):
        result = simulate_memory_leak(0, 5)
        self.assertEqual(result, [3, 0, 2])

    def test_handles_zero_initial_memory2(self):
        result = simulate_memory_leak(5, 0)
        self.assertEqual(result, [3, 2, 0])

    def test_handles_equal_initial_memory(self):
        result = simulate_memory_leak(10, 10)
        self.assertEqual(result, [6, 1, 4])

    def test_handles_large_input_values(self):
        result = simulate_memory_leak(1_000_000, 1_000_000)
        self.assertEqual(result[0], result[0])

    def test_crashes_immediately_when_no_memory_is_available(self):
        result = simulate_memory_leak(0, 0)
        self.assertEqual(result, [1, 0, 0])

    def test_allocates_when_only_one_memory_cell_can_handle_request(self):
        result = simulate_memory_leak(1, 0)
        self.assertEqual(result, [2, 0, 0])
