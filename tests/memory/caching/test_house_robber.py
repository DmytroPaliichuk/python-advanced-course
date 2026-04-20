import unittest

from memory.caching.homework.house_robber import (
    HouseRobberMemoized,
    HouseRobberOptimized,
    HouseRobberTabulated,
)


class TestHouseRobberImplementations(unittest.TestCase):
    def setUp(self):
        self.solvers = [
            HouseRobberMemoized(),
            HouseRobberTabulated(),
            HouseRobberOptimized(),
        ]

    def _check_all(self, houses, expected):
        for solver in self.solvers:
            with self.subTest(solver=solver.__class__.__name__):
                self.assertEqual(solver.rob(houses), expected)

    def test_basic_cases(self):
        self._check_all([1, 2, 3, 1], 4)
        self._check_all([2, 7, 9, 3, 1], 12)
        self._check_all([6, 7, 1, 30, 8, 2, 4], 41)

    def test_more_cases(self):
        self._check_all([20, 25, 30, 15, 10, 5, 50], 110)
        self._check_all([5, 3, 4, 11, 2], 16)
        self._check_all([3, 2, 5, 10, 7], 15)

    def test_single_house(self):
        self._check_all([10], 10)

    def test_two_houses(self):
        self._check_all([10, 1], 10)
        self._check_all([1, 10], 10)

    def test_empty_list(self):
        """Очікуємо 0 як для стандартної поведінки."""
        self._check_all([], 0)

    def test_large_values(self):
        self._check_all([100, 1, 1, 100], 200)
        self._check_all([50, 100, 50], 100)

    def test_all_zeros(self):
        self._check_all([0, 0, 0, 0], 0)

    def test_alternating_pattern(self):
        self._check_all([5, 1, 5, 1, 5], 15)
        self._check_all([10, 1, 10, 1, 10], 30)
