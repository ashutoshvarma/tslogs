import logging

from .parse import LogLine, load_files, parse_log
from .stats import get_stats

logging.getLogger(__name__).addHandler(logging.NullHandler())


__author__ = "Ashutosh Varma <ashutoshvarma11@live.com>"
__license__ = "MIT"
__version__ = (
    __import__("pkg_resources")
    .resource_string(__name__, "_version.txt")
    .decode("utf-8")
    .strip()
)


__all__ = ["parse_log", "LogLine", "load_files", "get_stats"]
