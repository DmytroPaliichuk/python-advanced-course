"""
Реалізувати задачу "House Robber" трьома методами динамічного програмування:
    1) Рекурсія з memoization (Top-Down) - O(n) пам’яті;
    2) Табуляція (Bottom-Up) з масивом - O(n) пам’яті;
    3) Оптимізована версія (Bottom-Up) з O(1) пам’яттю - опціонально.

Завдання:
    Є список будинків, де кожен елемент - сума грошей у будинку.
    Злодій не може грабувати два сусідні будинки.
    Потрібно повернути максимальну суму, яку можна викрасти.

    Опціонально - намалювати діаграму роботи алгоритму для мемоізації та табуляції

Актуальність:
    Три підходи демонструють еволюцію алгоритмів динамічного програмування:
        - Memoization: простий для розуміння, але рекурсивний;
        - Табуляція: ітеративний, контрольований, без рекурсії;
        - Оптимізований варіант: максимально ефективний по пам’яті.
    Такі техніки широко використовуються у кешуванні, оптимізації
    підзадач, аналізі часової/просторової складності та реальних
    системах з обмеженнями по пам’яті.
"""

from typing import Iterable


class HouseRobberMemoized:
    """House Robber - рекурсія + мемоізація (Top-Down Dynamic Programming)."""

    def rob(self, nums: Iterable[int]) -> int:
        # TODO: implement solution
        ...


class HouseRobberTabulated:
    """House Robber - табуляція (Bottom-Up Dynamic Programming)."""

    def rob(self, nums: Iterable[int]) -> int:
        # TODO: implement solution
        ...


class HouseRobberOptimized:
    """House Robber - оптимізована табуляція з O(1) памʼяттю. Опціонально"""

    def rob(self, nums: Iterable[int]) -> int:
        # TODO: implement solution
        ...
