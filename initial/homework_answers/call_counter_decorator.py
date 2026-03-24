from typing import Any, Callable


def call_counter(func: Callable) -> Callable:
    calls = 0

    def wrapper(*args, **kwargs) -> Any:
        nonlocal calls
        calls += 1
        wrapper.calls = calls  # type: ignore[attr-defined]
        return func(*args, **kwargs)

    wrapper.calls = calls  # type: ignore[attr-defined]
    return wrapper
