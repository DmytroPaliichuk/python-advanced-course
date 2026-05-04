import logging
import multiprocessing
import time

from unittest.mock import MagicMock

from multitasking.processes.homework.logging_centralization import (
    LogListenerThread,
    MPLogManager,
    QueueLogHandler,
    SENTINEL,
)


class TestMPLogManager:
    def test_start_replaces_handlers_with_queue_handler(
        self, logger: logging.Logger, mock_handler: logging.StreamHandler
    ):
        logger.addHandler(mock_handler)

        mgr = MPLogManager(logger)
        mgr.start()

        # старий хендлер забрали
        assert mock_handler not in logger.handlers

        # додано QueueLogHandler
        assert any(isinstance(h, QueueLogHandler) for h in logger.handlers)

        mgr.stop()

    def test_log_record_flows_through_listener(self, logger: logging.Logger, mock_handler: logging.StreamHandler):
        """
        Перевіряємо, що LogRecord проходить через queue -> listener -> mock_handler.emit()
        """

        logger.addHandler(mock_handler)

        mgr = MPLogManager(logger)
        mgr.start()

        logger.info('hello world')

        # даємо listener час витягнути запис з черги
        time.sleep(0.2)

        mock_handler.emit.assert_called_once()
        emitted_record = mock_handler.emit.call_args[0][0]
        assert emitted_record.msg == 'hello world'

        mgr.stop()

    def test_stop_restores_original_handlers(self, logger: logging.Logger, mock_handler: logging.StreamHandler):
        logger.addHandler(mock_handler)

        mgr = MPLogManager(logger)
        mgr.start()
        mgr.stop()

        # Queue handler більше не присутній
        assert not any(isinstance(h, QueueLogHandler) for h in logger.handlers)

        # Оригінальний хендлер повернувся
        assert mock_handler in logger.handlers

    def test_listener_stops_on_sentinel(self):
        queue = multiprocessing.Queue(-1)
        handler = logging.StreamHandler()
        handler.emit = MagicMock()

        listener = LogListenerThread(queue=queue, handlers=[handler], logger_name='x')
        listener.start()

        queue.put(SENTINEL)
        listener.join(timeout=2.0)

        assert not listener.is_alive()

    def test_multiple_log_records_are_processed(self, logger: logging.Logger, mock_handler: logging.StreamHandler):
        logger.addHandler(mock_handler)

        mgr = MPLogManager(logger)
        mgr.start()

        for i in range(5):
            logger.info(f'msg {i}')

        time.sleep(0.3)

        assert mock_handler.emit.call_count == 5

        msgs = [call[0][0].msg for call in mock_handler.emit.call_args_list]
        assert msgs == [f'msg {i}' for i in range(5)]

        mgr.stop()

    def test_start_is_idempotent(self, logger: logging.Logger, mock_handler: logging.StreamHandler):
        logger.addHandler(mock_handler)
        mgr = MPLogManager(logger)

        mgr.start()
        mgr.start()  # не має створити дублікати

        queue_handlers = [h for h in logger.handlers if isinstance(h, QueueLogHandler)]
        assert len(queue_handlers) == 1

        mgr.stop()
