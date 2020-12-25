from datetime import datetime
from pathlib import Path

from tslogs.utils import get_files_in_date_range

LOG_VALID_NAME = [
    "2020-10-10.txt",
    "2020-10-11.txt",
    "2020-10-12.txt",
    "2020-10-13.txt",
    "2020-10-14.txt",
    "2020-10-15.txt",
]

INVALID_LOG_DATE_NAME = "2020-99-99.txt"


class TestUtils:
    def test_valid_get_files_in_date_range(self, tmp_path: Path):
        valid_dir = tmp_path / "valid"
        valid_dir.mkdir()

        valid_paths = []
        for fn in LOG_VALID_NAME:
            f_path = valid_dir / fn
            f_path.touch()
            valid_paths.append(f_path)
        assert len(get_files_in_date_range(valid_paths)) == len(valid_paths)
        assert len(get_files_in_date_range(valid_dir)) == len(valid_paths)

        # use valid_dir as date_range is ignored for explict files (valid_paths)
        assert len(
            get_files_in_date_range(
                valid_dir, (datetime(2020, 10, 10), datetime(2020, 10, 12))
            )
        ) == len(valid_paths[:2])

    def test_invalid_get_files_in_date_range(self, tmp_path: Path):
        invalid_dir = tmp_path / "invalid"
        invalid_dir.mkdir()

        invalid_file = invalid_dir / INVALID_LOG_DATE_NAME
        invalid_file.touch()

        assert (
            get_files_in_date_range(
                invalid_dir, (datetime(2020, 10, 10), datetime(2020, 10, 10))
            )
            == []
        )
