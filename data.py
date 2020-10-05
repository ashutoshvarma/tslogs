#!/usr/bin/env python

from logging import getLogger
import os
import sys
from datetime import datetime

import logging
logger = logging,getLogger(__name__)

if len(sys.argv) > 1:
    file = sys.argv[1]
elif (file := os.environ.get("TS_LOG_FILE")) is None:
    logging.error(f"No log file given")
    logger.error(f"either set env TS_LOG_FILE or pass file path as script argument.")
    sys.exit(1)

print(f"Reading log file - {file}")
with open(file) as f:
    data = [d.split() for d in f.read().splitlines()[1:]]


clock = [float(d[2]) for d in data]
time = [
    datetime.strptime(f"{d[0].strip()} {d[1].strip()}", "%Y-%m-%d %H:%M:%S")
    for d in data
]
temp = [int(d[7]) for d in data]

total_sec = (time[-1] - time[0]).total_seconds()
avg_clock = sum(clock) / total_sec
avg_temp = sum(temp) / total_sec
above_85_secs = len([_ for _ in temp if _ >= 85])
limit_temp = len([_ for _ in data if len(_) == 13 and _[-1] == "TEMP"])
max_power = max([float(d[11]) for d in data])

print(f"Summary for {time[0]} - {time[-1]} :-")
print(f"total_sec: {total_sec}")
print(f"avg_clock: {avg_clock}")
print(f"avg_temp: {avg_temp}")
print(f"above_85_sec: {above_85_secs} or {above_85_secs/total_sec:.2%}")
print(f"limit_temp: {limit_temp} times")
print(f"max_power: {max_power}")
