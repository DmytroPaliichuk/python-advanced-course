import os

from typing import Sequence
from unittest.mock import MagicMock, patch

import pytest

from requests import RequestException

from multitasking.threads.homework.downloader import ThreadDownloader


class TestThreadDownloader:
    def test_download_one_writes_file(self, downloader: ThreadDownloader, tmp_dirs: Sequence[str]):
        series_dir, _ = tmp_dirs
        url = downloader.urls[0]

        # mock response with iter_content
        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.iter_content.return_value = [b'hello', b'world']
        mock_resp.raise_for_status.return_value = None

        with patch('requests.sessions.Session.get', return_value=mock_resp):
            result = downloader._download_one(url, series_dir)

        assert os.path.exists(result.path)
        with open(result.path, 'rb') as f:
            assert f.read() == b'helloworld'

    def test_download_one_raises_on_error(self, downloader: ThreadDownloader, tmp_dirs: Sequence[str]):
        series_dir, _ = tmp_dirs
        url = downloader.urls[0]

        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.iter_content.side_effect = RequestException

        with patch('requests.sessions.Session.get', return_value=mock_resp):
            with pytest.raises(RequestException):
                downloader._download_one(url, series_dir)

    def test_download_series_creates_all_files(self, downloader: ThreadDownloader, tmp_dirs: Sequence[str]):
        series_dir, _ = tmp_dirs

        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.iter_content.return_value = [b'data']
        mock_resp.raise_for_status.return_value = None

        with patch('requests.sessions.Session.get', return_value=mock_resp):
            downloader.download_series()

        created = os.listdir(series_dir)
        assert len(created) == len(downloader.urls)

    def test_download_concurrent_creates_all_files(self, downloader: ThreadDownloader, tmp_dirs: Sequence[str]):
        _, concurrent_dir = tmp_dirs

        mock_resp = MagicMock()
        mock_resp.__enter__.return_value = mock_resp
        mock_resp.iter_content.return_value = [b'data']
        mock_resp.raise_for_status.return_value = None

        with patch('requests.sessions.Session.get', return_value=mock_resp):
            downloader.download_concurrent()

        created = os.listdir(concurrent_dir)
        assert len(created) == len(downloader.urls)
