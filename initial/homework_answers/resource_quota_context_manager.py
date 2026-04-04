from types import TracebackType
from typing import Type


class ResourceQuota:
    def __init__(self, total_limit: int):
        self.total_limit = total_limit
        self.used = 0

    def request(self, amount: int) -> '_QuotaContext':
        return _QuotaContext(self, amount)


class _QuotaContext:
    def __init__(self, quota: ResourceQuota, amount: int):
        self.quota = quota
        self.amount = amount

    def __enter__(self) -> int:
        if self.quota.used + self.amount > self.quota.total_limit:
            raise ValueError('Resource limit exceeded')
        self.quota.used += self.amount
        return self.amount

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self.quota.used -= self.amount
