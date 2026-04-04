from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


@dataclass(slots=True, frozen=True)
class WindowResult:
    max_window_sum: int
    window_size: int
    processed_rows: int


class LogWindowAnalyzer:
    __slots__ = ('_window_size',)

    def __init__(self, window_size: int):
        if window_size <= 0:
            raise ValueError('window_size must be greater than 0')

        self._window_size = window_size

    def process_file(self, path: Path) -> WindowResult:
        with path.open('r', encoding='utf-8', newline='') as stream:
            window_result = self._process_stream(stream)

        return window_result

    def _process_stream(self, stream: TextIO) -> WindowResult:
        window: deque[int] = deque()

        current_window_sum = 0
        max_window_sum = 0
        processed_rows = 0

        for line in stream:
            if line == '\n':
                continue

            duration = self._parse_duration(line)

            window.append(duration)
            current_window_sum += duration
            processed_rows += 1

            if len(window) > self._window_size:
                current_window_sum -= window.popleft()

            if len(window) == self._window_size and current_window_sum > max_window_sum:
                max_window_sum = current_window_sum

        return WindowResult(
            max_window_sum=max_window_sum,
            window_size=self._window_size,
            processed_rows=processed_rows,
        )

    @staticmethod
    def _parse_duration(line: str) -> int:
        last_sep = line.rfind(';')
        if last_sep == -1:
            raise ValueError(f'Invalid log line: {line!r}')

        raw_duration = line[last_sep + 1 :].rstrip('\n')

        try:
            duration = int(raw_duration)
        except ValueError as exc:
            raise ValueError(f'Invalid duration value: {raw_duration!r}') from exc

        return duration
