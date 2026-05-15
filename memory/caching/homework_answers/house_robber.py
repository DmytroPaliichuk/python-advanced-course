from typing import Iterable


class HouseRobberMemoized:
    def rob(self, nums: Iterable[int]) -> int:
        if not nums:
            return 0
        if len(nums) == 1:
            return nums[0]

        cache: dict[int, int] = {}
        return self._compute_max_loot(nums, len(nums) - 1, cache)

    def _compute_max_loot(self, nums: Iterable[int], i: int, cache: dict[int, int]) -> int:
        if i in cache:
            return cache[i]

        if i == 0:
            result = nums[0]
        elif i == 1:
            result = max(nums[0], nums[1])
        else:
            result = max(
                self._compute_max_loot(nums, i - 1, cache),
                nums[i] + self._compute_max_loot(nums, i - 2, cache),
            )

        cache[i] = result
        return result


class HouseRobberTabulated:
    def rob(self, nums: Iterable[int]) -> int:
        n = len(nums)
        if n == 0:
            return 0

        if n == 1:
            return nums[0]

        max_loot = [0] * n
        max_loot[0] = nums[0]
        max_loot[1] = max(nums[0], nums[1])

        for i in range(2, n):
            max_loot[i] = max(max_loot[i - 1], nums[i] + max_loot[i - 2])

        return max_loot[-1]


class HouseRobberOptimized:
    def rob(self, nums: Iterable[int]) -> int:
        prev = curr = 0

        for val in nums:
            new_curr = max(curr, prev + val)
            prev = curr
            curr = new_curr

        return curr
