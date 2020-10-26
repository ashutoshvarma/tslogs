#!/usr/bin/env python

import logging
from dataclasses import dataclass, field
from datetime import datetime
from os import PathLike
from typing import Iterable, List, Optional, Tuple, Union

from .utils import RE_ISO_DATE, get_files_in_date_range

logger = logging.getLogger(__name__)


@dataclass
class LogLine:
    time: datetime
    multi: float
    c0: float
    clock_mod: float
    chip_mod: float
    battery_mw: float
    cpu_temp: float
    gpu_mhz: float
    gpu_temp: float
    vid: float
    power: float
    limits: List[str] = field(default_factory=list)


def is_valid_log_file(line: str) -> bool:
    """
    Check whether first line of file resembles throttlestop's log file

    If line is valid log line
    >>> is_valid_log_file("2020-08-21  07:00:02  ........")
    True

    If line is log header
    >>> is_valid_log_file("   DATE       TIME    MULTI   C0% ....")
    True

    >>> is_valid_log_file("abc abc")
    False

    >>> is_valid_log_file("` DATE")
    False

    >>> is_valid_log_file("")
    False
    """
    line = line.split()
    return bool(len(line) > 0 and (("DATE" in line[0]) or RE_ISO_DATE.match(line[0])))


def _parse_log_lines(lines: List[str]) -> List[LogLine]:
    loglines = []
    data = [log.split() for log in lines if "DATE" not in log]

    for line in data:
        try:
            # date and time
            dt = datetime.strptime(" ".join(line[:2]), "%Y-%m-%d %H:%M:%S")
            # limits
            limits = line[12:]
            loglines.append(LogLine(dt, *[float(i) for i in line[2:12]], limits=limits))
        except Exception:
            logger.exception("failed to parse line - {line}")
    logger.debug(f"{len(loglines)} parsed.")
    return loglines


def parse_log(
    files: List[Union[PathLike, str]],
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> List[LogLine]:
    lines = []
    for file_path in files:
        logger.debug(f"loading file {str(file_path)}")
        with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
            if is_valid_log_file(fp.readline()):
                fp.seek(0)
                lines += fp.readlines()
            else:
                logger.debug(f"ignoring {file_path}")

    parsed = _parse_log_lines(lines)
    if date_range:
        parsed = [p for p in parsed if date_range[0] <= p.time < date_range[1]]
    return parsed


def load_files(
    paths: Iterable[Union[str, PathLike]],
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> List[LogLine]:
    return parse_log(get_files_in_date_range(paths, date_range), date_range)
