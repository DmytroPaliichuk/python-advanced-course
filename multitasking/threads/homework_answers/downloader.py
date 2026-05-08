import hashlib
import os
import random
import threading
import time
import uuid

from concurrent.futures import as_completed, ThreadPoolExecutor
from dataclasses import dataclass
from typing import BinaryIO, Sequence
from urllib.parse import urlparse

import requests

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass(frozen=True, slots=True)
class DownloadResult:
    url: str
    path: str


class ThreadDownloader:
    def __init__(
        self,
        urls: Sequence[str],
        series_dir: str,
        concurrent_dir: str,
        workers: int = 8,
        chunk_size: int = 1024 * 1024,
        timeout: tuple[float, float] = (10.0, 60.0),  # (connect, read)
        max_retries: int = 6,
        backoff_factor: float = 0.6,
    ):
        self.urls = list(urls)
        self.series_dir = series_dir
        self.concurrent_dir = concurrent_dir
        self.workers = max(1, min(workers, len(self.urls))) if self.urls else 1
        self.chunk_size = chunk_size
        self.timeout = timeout

        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

        os.makedirs(self.series_dir, exist_ok=True)
        os.makedirs(self.concurrent_dir, exist_ok=True)

        self._local = threading.local()

    @staticmethod
    def _build_base_name(url: str) -> str:
        parsed = urlparse(url)
        name = os.path.basename(parsed.path) or 'file'

        safe = ''.join(c if (c.isalnum() or c in '._-') else '_' for c in name).strip('._-')
        safe = safe or 'file'

        h = hashlib.sha1(url.encode('utf-8')).hexdigest()[:8]
        root, ext = os.path.splitext(safe)
        return f'{root}_{h}{ext or ".bin"}'

    @staticmethod
    def _open_unique_file(directory: str, base_name: str) -> tuple[BinaryIO, str]:
        path = os.path.join(directory, base_name)
        try:
            file = open(path, 'xb')  # atomic create
        except FileExistsError:
            root, ext = os.path.splitext(base_name)
            unique_name = f'{root}_{uuid.uuid4().hex[:6]}{ext}'
            path = os.path.join(directory, unique_name)
            file = open(path, 'xb')
        return file, path

    def _get_session(self) -> requests.Session:
        session = getattr(self._local, 'session', None)
        if session is not None:
            return session

        session = requests.Session()

        retry = Retry(
            total=self.max_retries,
            connect=self.max_retries,
            read=self.max_retries,
            status=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=('GET',),
            respect_retry_after_header=True,  # важливо для 429
            raise_on_status=False,  # ми самі піднімемо помилку після retry
        )

        adapter = HTTPAdapter(max_retries=retry, pool_connections=50, pool_maxsize=50)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers.update(
            {
                'User-Agent': 'ThreadDownloader/1.0 (+learning; requests)',
                'Accept': '*/*',
            }
        )

        self._local.session = session
        return session

    def _download_one(self, url: str, directory: str) -> DownloadResult:
        base_name = self._build_base_name(url)
        file, path = self._open_unique_file(directory, base_name)

        session = self._get_session()

        try:
            with file:
                with session.get(url, stream=True, timeout=self.timeout) as resp:
                    try:
                        resp.raise_for_status()
                    except requests.HTTPError:
                        # For 429, add a small jitter before bubbling up the error
                        if resp.status_code == 429:
                            time.sleep(1.0 + random.random())
                        raise

                    for chunk in resp.iter_content(chunk_size=self.chunk_size):
                        if chunk:
                            file.write(chunk)

        except Exception:
            try:
                os.remove(path)
            except OSError:
                pass
            raise

        return DownloadResult(url=url, path=path)

    def download_series(self) -> list[DownloadResult]:
        return [self._download_one(url, self.series_dir) for url in self.urls]

    def download_concurrent(self) -> list[DownloadResult]:
        if not self.urls:
            return []

        results: list[DownloadResult] = []
        errors: list[tuple[str, Exception]] = []

        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            future_to_url = {pool.submit(self._download_one, url, self.concurrent_dir): url for url in self.urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results.append(future.result())
                except Exception as error:
                    errors.append((url, error))

        if errors:
            first = errors[0][1]
            raise RuntimeError(
                f'{len(errors)} downloads failed; first url={errors[0][0]!r}, error={first!r}'
            ) from first

        return results
