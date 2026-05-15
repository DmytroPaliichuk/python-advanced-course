"""
Багатопотоковий сервер для прийому логів.

Цей файл містить повністю готову, допоміжну реалізацію HTTP-сервера,
який використовується у домашньому завданні для демонстрації реального
I/O-bound навантаження.

Сервер приймає HTTP POST-запити на endpoint `/logs`, очікує JSON-об’єкт
у тілі запиту, виконує мінімальну перевірку валідності та потокобезпечно
дописує кожен лог у файл `server_logs.jsonl`.

Для обробки кожного вхідного запиту сервер створює окремий робочий потік
(ThreadingMixIn), тому він здатний одночасно приймати велику кількість
записів, що дозволяє протестувати прискорення від використання
потоків у клієнтському коді.

Цей файл не є частиною завдання і не потребує жодних змін.
"""

import json
import threading

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """HTTP-сервер, який обробляє кожен запит у окремому потоці."""

    daemon_threads = True  # потоки закриваються разом із сервером


class LogHTTPServer(ThreadedHTTPServer):
    """Сервер, який приймає POST /logs з JSON і зберігає кожен запис у файл."""

    def __init__(self, server_address, RequestHandlerClass, log_path: Path):
        super().__init__(server_address, RequestHandlerClass)
        self.log_path = log_path
        self._lock = threading.Lock()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def append_log(self, raw_body: bytes) -> None:
        """Потокобезпечний запис у файл."""
        with self._lock, self.log_path.open('ab') as f:
            f.write(raw_body)
            f.write(b'\n')


class LogRequestHandler(BaseHTTPRequestHandler):
    server: LogHTTPServer

    def do_POST(self) -> None:
        if self.path != '/logs':
            self.send_error(404, 'Not Found')
            return

        length_header = self.headers.get('Content-Length')
        if not length_header:
            self.send_error(400, 'Missing Content-Length')
            return

        try:
            length = int(length_header)
        except ValueError:
            self.send_error(400, 'Invalid Content-Length')
            return

        body = self.rfile.read(length)
        try:
            _ = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400, 'Invalid JSON')
            return

        self.server.append_log(body)

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    # приглушуємо стандартний шумний лог
    def log_message(self, format: str, *args) -> None:
        return


def run_server(
    host: str = '127.0.0.1',
    port: int = 8000,
    log_file: str = 'server_logs.jsonl',
) -> None:
    log_path = Path(log_file)
    server = LogHTTPServer((host, port), LogRequestHandler, log_path=log_path)
    print(f'Log server listening on http://{host}:{port}/logs')
    print(f'Writing logs to {log_path.resolve()}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Server shutting down...')
    finally:
        server.server_close()


if __name__ == '__main__':
    run_server()
