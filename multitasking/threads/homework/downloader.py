"""
Завдання:
    Реалізувати клас ThreadDownloader, який уміє завантажувати файли
    як послідовно, так і конкурентно, коректно працюючи з файловою системою
    в умовах багатопоточності.

    Є список URL-адрес та дві директорії:
        - series_dir      - куди зберігаються файли при послідовному завантаженні;
        - concurrent_dir  - куди зберігаються файли при конкурентному завантаженні.

    За потреби можна додавати нові атрибути класу, але робіть їх опційними, щоб не впали тести.
    За потреби можна розширювати клас допоміжними методами.

Вимоги:
    - Для потокового виконання використати ThreadPoolExecutor;
    - Не використовувати глобальні змінні;
    - Скачувати файл оптимально по памʼяті;
    - Забезпечити потокобезпечне створення файлів.

Актуальність:
    У реальних системах завантаження великих обсягів даних є поширеною задачею.
    Сервіси, які працюють із файлами - медіа-платформи, бекап-системи, ETL-пайплайни,
    аналітичні рішення, CDN, інструменти синхронізації - постійно виконують
    однотипні I/O-bound операції, що можуть сильно уповільнювати роботу,
    якщо виконувати їх послідовно.

    Конкурентне завантаження:
        - дозволяє збільшити пропускну здатність у кілька разів;
        - ефективно використовує час очікування мережевих операцій;
        - показує різницю між CPU-bound та I/O-bound навантаженням;
        - демонструє силу потоків у задачах, де GIL не є вузьким місцем.

    Це завдання дозволяє:
        - побачити реальний приріст продуктивності при конкурентному виконанні;
        - освоїти роботу з ThreadPoolExecutor;
        - навчитися запобігати race conditions при роботі з файловою системою;
        - зрозуміти принципи ефективного завантаження великих файлів;
        - отримати навички побудови багатопоточних I/O-пайплайнів.
"""

import os
import time

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True, slots=True)
class DownloadResult:
    """Represents the result of a single file download."""

    url: str  # Original source URL that was downloaded
    path: str  # Local filesystem path where the file was saved


class ThreadDownloader:
    def __init__(
        self,
        urls: Sequence[str],
        series_dir: str,
        concurrent_dir: str,
        workers: int = 8,
        # можна додавати ще аргументи за потреби
    ):
        self.urls = list(urls)
        self.series_dir = series_dir
        self.concurrent_dir = concurrent_dir
        self.workers = max(1, min(workers, len(self.urls))) if self.urls else 1

    def download_series(self) -> list[DownloadResult]:
        """
        Послідовно завантажити всі файли з self.urls у self.series_dir.
        """
        # TODO: implement solution
        ...

    def download_concurrent(self) -> list[DownloadResult]:
        """
        Конкурентно завантажити всі файли з self.urls у self.concurrent_dir.
        Використовувати ThreadPoolExecutor.
        """
        # TODO: implement solution
        ...

    def _download_one(self, url: str, directory: str) -> DownloadResult:
        """
        Метод для скачування одного файла, має бути використано в download_series та download_concurrent.
        Повертає шляхи файлу (DownloadResult).
        """
        # TODO: implement solution
        ...


def main(num: int = 50) -> None:
    """Допоміжна функція для тестування з безпечним файлом для скачування."""
    base_urls = ('https://speed.cloudflare.com/__down?bytes=20971520',)  # ~20MB
    urls = [base_urls[i % len(base_urls)] for i in range(num)]

    series_dir = 'downloads_series'
    concurrent_dir = 'downloads_concurrent'

    downloader = ThreadDownloader(
        urls=urls,
        series_dir=series_dir,
        concurrent_dir=concurrent_dir,
        workers=...,  # обрати кількість самостійно
    )

    print('=== SERIES DOWNLOAD ===')
    t_start = time.perf_counter()
    downloader.download_series()
    t_series = time.perf_counter() - t_start
    print(f'Series time: {t_series:.2f} s, files in {series_dir}: {len(os.listdir(series_dir))}')

    print('=== PARALLEL DOWNLOAD ===')
    t_start = time.perf_counter()
    downloader.download_concurrent()
    t_concurrent = time.perf_counter() - t_start
    print(f'Parallel time: {t_concurrent:.2f} s, files in {concurrent_dir}: {len(os.listdir(concurrent_dir))}')

if __name__ == '__main__':
    main()
