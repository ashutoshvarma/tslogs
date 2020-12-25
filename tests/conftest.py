import argparse
from pathlib import Path

import pytest

import tslogs.cli as cli


@pytest.fixture
def args_parser() -> argparse.ArgumentParser:
    return cli.init_argparse()


@pytest.fixture
def test_root() -> Path:
    return Path(__file__).parent


@pytest.fixture
def log_root(test_root: Path) -> Path:
    return test_root / Path("logs")
