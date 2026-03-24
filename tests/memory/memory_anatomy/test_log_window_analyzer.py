from pathlib import Path

import pytest

from memory.memory_anatomy.homework.log_window_analyzer.analyzer import LogWindowAnalyzer


class TestLogWindowAnalyzer:
    def test_basic_window(self, tmp_path: Path):
        file_path = tmp_path / 'log.txt'

        file_path.write_text('1;auth;10\n2;auth;20\n3;auth;30\n4;auth;40\n5;auth;50\n')

        analyzer = LogWindowAnalyzer(window_size=3)

        result = analyzer.process_file(file_path)

        assert result.max_window_sum == 120
        assert result.window_size == 3
        assert result.processed_rows == 5

    def test_window_size_one(self, tmp_path: Path):
        file_path = tmp_path / 'log.txt'

        file_path.write_text('1;auth;10\n2;auth;20\n3;auth;5\n')

        analyzer = LogWindowAnalyzer(window_size=1)

        result = analyzer.process_file(file_path)

        assert result.max_window_sum == 20
        assert result.processed_rows == 3

    def test_empty_lines_are_skipped(self, tmp_path: Path):
        file_path = tmp_path / 'log.txt'

        file_path.write_text('1;auth;10\n\n2;auth;20\n\n3;auth;30\n')

        analyzer = LogWindowAnalyzer(window_size=2)

        result = analyzer.process_file(file_path)

        assert result.max_window_sum == 50
        assert result.processed_rows == 3

    def test_invalid_duration(self, tmp_path: Path):
        file_path = tmp_path / 'log.txt'

        file_path.write_text('1;auth;10\n2;auth;bad\n')

        analyzer = LogWindowAnalyzer(window_size=2)

        with pytest.raises(ValueError):
            analyzer.process_file(file_path)

    def test_invalid_line_format(self, tmp_path: Path):
        file_path = tmp_path / 'log.txt'

        file_path.write_text('1;auth;10\ninvalid_line\n')

        analyzer = LogWindowAnalyzer(window_size=2)

        with pytest.raises(ValueError):
            analyzer.process_file(file_path)
