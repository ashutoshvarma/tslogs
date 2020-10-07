#!/usr/bin/env python

import logging
import os
import sys
from dataclasses import dataclass, fields
from datetime import datetime
from logging import getLogger
from os import PathLike
from typing import Iterable, List, Optional, Tuple, Union

from .utils import get_files_in_date_range

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
    limits: Iterable[str]


# def _parse_filters(filter_str: str, parsed_lines: List[LogLine]):
#     allowed_tokens = [f.name for f in fields(LogLine)]
#     comp_tokens = ["<", "<=", "=", ">", ">="]
#     result_dict = {}

#     for fltr in filter_str.split(";"):
#         keys = fltr.split()
#         # check for length
#         if len(keys) != 3:
#             logger.warning(f"ignoring filter string '{fltr}' as more than 3 token found")
#             continue
#         nprop = None
#         ncomp = None
#         value = None
#         for k in keys:
#             if k in allowed_tokens:
#                 nprop = k
#             elif k in comp_tokens:
#                 ncomp = k
#             else:
#                 try:
#                     value = float(k)
#                 except ValueError:
#                     pass
#         if not all([nprop, ncomp, value]):
#             logger.warning(f"ignoring filter string '{fltr}', cannot parse properly")
#             continue


def _parse_log_lines(lines: List[str]) -> List[LogLine]:
    loglines = []
    data = [l.split() for l in lines if not "DATE" in l]

    for line in data:
        # date and time
        dt = datetime.strptime(" ".join(line[:2]), "%Y-%m-%d %H:%M:%S")
        # (
        #     multi,
        #     c0,
        #     clock_mod,
        #     chip_mod,
        #     battery_mw,
        #     cpu_temp,
        #     gpu_mhz,
        #     gpu_temp,
        #     vid,
        #     power,
        # ) = [float(i) for i in line[2:12]]

        # limits
        limits = line[12:]

        loglines.append(LogLine(dt, *[float(i) for i in line[2:12]], limits=limits))
    logger.debug(f"{len(loglines)} parsed.")
    return loglines


def parse_log(
    files: List[Union[PathLike, str]],
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> List[LogLine]:
    lines = []
    for file_path in files:
        logger.debug(f"loading file {str(file_path)}")
        with open(file_path, "r") as fp:
            lines += fp.read().splitlines()
    
    parsed = _parse_log_lines(lines)
    if date_range:
        parsed = [p for p in parsed if date_range[0] <= p.time < date_range[1]]
    return parsed


def load_files(
    paths: Iterable[Union[str, PathLike]],
    date_range: Optional[Tuple[datetime, datetime]] = None,
) -> List[LogLine]:
    return parse_log(get_files_in_date_range(paths, date_range), date_range)
