import re
from datetime import datetime
from os import PathLike
from pathlib import Path
from re import match
from typing import Iterable, List, Optional, Tuple, Union


__author__ = "Ashutosh Varma <ashutoshvarma11@live.com>"
__license__ = "MIT"
__version__ = (
    __import__("pkg_resources")
    .resource_string(__name__, "_version.txt")
    .decode("utf-8")
    .strip()
)


from .parse import load_files, parse_log, LogLine
from .utils import get_files_in_date_range

__all__ = ["parse_log", "LogLine", "load_files"]
