import os
import time
import tracemalloc

from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Callable, Iterable, Iterator

import psutil


@dataclass
class MemoryMetrics:
    exec_time_sec: float
    python_current_mb: float
    python_peak_mb: float
    rss_start_mb: float
    rss_end_mb: float
    rss_delta_mb: float


@dataclass
class ProfilingSession:
    process: psutil.Process
    rss_start: int
    snap_start: tracemalloc.Snapshot
    t0: float


@dataclass
class AllocationRecord:
    file: str
    line: int
    size_kb: float
    count: int
    stat_repr: str


class MemoryInspector:
    def __init__(
        self,
        project_root: str | None = None,
        only_project_files: bool = True,
        excluded_files: Iterable[str] | None = None,
    ) -> None:
        self.project_root = project_root or os.getcwd()
        self.only_project_files = only_project_files
        self.excluded_files = excluded_files or {'memory_profiler.py'}

    @staticmethod
    def take_snapshot() -> tracemalloc.Snapshot:
        return tracemalloc.take_snapshot()

    def extract(
        self,
        stats: Iterable[tracemalloc.Statistic | tracemalloc.StatisticDiff],
    ) -> list[AllocationRecord]:
        conclusions: list[AllocationRecord] = []

        for stat in stats:
            for frame in stat.traceback:
                if self._is_project_file(frame.filename):
                    conclusions.append(
                        AllocationRecord(
                            file=frame.filename,
                            line=frame.lineno,
                            size_kb=stat.size / 1024,
                            count=stat.count,
                            stat_repr=str(stat),
                        )
                    )
                    break

        conclusions.sort(key=lambda r: r.size_kb, reverse=True)
        return conclusions

    def _is_project_file(self, filename: str) -> bool:
        if any(excluded in filename for excluded in self.excluded_files):
            return False

        if not self.only_project_files:
            return True

        return filename.startswith(self.project_root)


class MemoryPrinter:
    @staticmethod
    def print_metrics(m: MemoryMetrics):
        print(f'Execution time:      {m.exec_time_sec:.4f} sec')
        print(f'Python peak alloc:   {m.python_peak_mb:.3f} MB')
        print(f'Python current mem:  {m.python_current_mb:.3f} MB')
        print(f'RSS start:           {m.rss_start_mb:.3f} MB')
        print(f'RSS end:             {m.rss_end_mb:.3f} MB')
        print(f'RSS Δ:               {m.rss_delta_mb:.3f} MB')

    @staticmethod
    def print_allocations(
        title: str,
        allocs: list[AllocationRecord],
        top_n: int,
    ):
        print(f'\n{title}')
        print('-' * 70)

        if not allocs:
            print('No memory allocations detected.')
            return

        for rec in allocs[:top_n]:
            print(rec.stat_repr)


class MemoryProfiler:
    def __init__(
        self,
        project_root: str | None = None,
        *,
        top_n: int = 10,
        only_project_files: bool = True,
    ):
        self.inspector = MemoryInspector(project_root, only_project_files)
        self.printer = MemoryPrinter()
        self.top_n = top_n

    @contextmanager
    def _profiling_session(self) -> Iterator[ProfilingSession]:
        process = psutil.Process(os.getpid())

        tracemalloc.start()
        session = ProfilingSession(
            process=process,
            rss_start=process.memory_info().rss,
            snap_start=self.inspector.take_snapshot(),
            t0=time.perf_counter(),
        )

        try:
            yield session
        finally:
            t1 = time.perf_counter()
            snap_end = self.inspector.take_snapshot()
            python_current, python_peak = tracemalloc.get_traced_memory()
            rss_end = session.process.memory_info().rss
            tracemalloc.stop()

            metrics = MemoryMetrics(
                exec_time_sec=t1 - session.t0,
                python_current_mb=python_current / 1024 / 1024,
                python_peak_mb=python_peak / 1024 / 1024,
                rss_start_mb=session.rss_start / 1024 / 1024,
                rss_end_mb=rss_end / 1024 / 1024,
                rss_delta_mb=(rss_end - session.rss_start) / 1024 / 1024,
            )

            diff_stats = snap_end.compare_to(session.snap_start, 'lineno')
            top_stats = snap_end.statistics('lineno')

            diff = self.inspector.extract(diff_stats)
            top = self.inspector.extract(top_stats)

            self.printer.print_metrics(metrics)
            self.printer.print_allocations('DIFF ALLOCATIONS', diff, self.top_n)
            self.printer.print_allocations('TOP LINES BY ALLOCATED MEMORY', top, self.top_n)

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f'MEMORY PROFILING: {func.__name__}')
            print('-' * 70)

            with self._profiling_session():
                result = func(*args, **kwargs)

            return result

        return wrapper
