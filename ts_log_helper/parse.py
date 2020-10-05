#!/usr/bin/env python

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from logging import getLogger
from os import PathLike
from typing import Iterable, List, Union

logger = logging, getLogger(__name__)

if len(sys.argv) > 1:
    file = sys.argv[1]
elif (file := os.environ.get("TS_LOG_FILE")) is None:
    logging.error(f"No log file given")
    logger.error(f"either set env TS_LOG_FILE or pass file path as script argument.")
    sys.exit(1)


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


def parse_log(file: PathLike) -> List[LogLine]:
    data = []
    with open(file, "r") as fp:
        data = [l.split() for l in fp.read().splitlines() if not "DATE" in l]

    loglines = []
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

        loglines.append(
            LogLine(dt, *[float(i) for i in line[2:12]], limits=limits)
        )
    return loglines

