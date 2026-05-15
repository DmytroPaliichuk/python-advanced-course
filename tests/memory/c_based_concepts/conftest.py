from pathlib import Path

import pytest


@pytest.fixture
def sample_file(tmp_path: Path) -> Path:
    file_path = tmp_path / 'measurements.txt'

    file_path.write_text(
        '\n'.join(
            [
                'Kyiv;1.0',
                'Kyiv;3.0',
                'Kyiv;5.0',
                'Amsterdam;7.0',
                'Amsterdam;9.0',
            ]
        )
    )

    return file_path
