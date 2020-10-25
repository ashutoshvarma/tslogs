from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Tuple

from tslogs.parse import LogLine


@dataclass
class LimitStat:
    limit: str
    total_secs: int
    percent_time: float


@dataclass
class LogStats:
    time_range: Tuple[datetime, datetime]
    time_elapsed: timedelta

    max_cpu_temp: int
    time_above_90: timedelta
    percent_above_90: float

    avg_multi: float
    avg_c0: float
    avg_clock_mod: float
    avg_chip_mod: float
    avg_battery_mw: float
    avg_cpu_temp: float
    avg_gpu_mhz: float
    avg_gpu_temp: float
    avg_vid: float
    avg_power: float

    limits: List[LimitStat]


def _get_limits_elasped(loglines: Iterable[LogLine], total_sec: int) -> List[LimitStat]:
    # limits_dict: Dict[str, datetime] = {}
    # for line in loglines:
    #     if len(line.limits) > 0:
    #         for lm in line.limits:
    #             if not limits_dict.get(lm):
    #                 limits_dict[lm] = []
    #             limits_dict[lm].append(line.time)

    # limit_stats: List[LimitsStat] = []
    # for lm, times in limits_dict.items():
    #     limit_stats.append(LimitsStat(lm, (max(times) - max(times))))
    # return limit_stats

    limit_stats: Dict[str, int] = {}
    for log in loglines:
        if len(log.limits) > 0:
            for lm in log.limits:
                if not limit_stats.get(lm):
                    limit_stats[lm] = 1
                else:
                    limit_stats[lm] += 1
    return [
        LimitStat(k, v, percent_time=(v / total_sec) * 100)
        for k, v in limit_stats.items()
    ]


def get_stats(loglines: Iterable[LogLine]) -> LogStats:
    # FIXME: extremely unoptimised implementaion, lost of repetaed
    #       loops. Change to a single for loop
    count = len(loglines)
    if count <= 0:
        raise ValueError(f"'loglines' cannot be empty.")

    start_t = min(loglines, key=lambda x: x.time).time
    end_t = max(loglines, key=lambda x: x.time).time

    # logs are print per second
    time_elapsed = timedelta(seconds=len(loglines))
    # above_90 = [l.time for l in loglines if l.cpu_temp >= 90]
    time_above_90 = timedelta(seconds=sum(l.cpu_temp >= 90 for l in loglines))
    percent_above_90 = (
        time_above_90.total_seconds() / time_elapsed.total_seconds()
    ) * 100

    max_cpu_temp = max(loglines, key=lambda x: x.cpu_temp).cpu_temp

    avg_dict: Dict[str, float] = {}
    for f in fields(LogLine):
        if f.type == float:
            avg_dict[f"avg_{f.name}"] = (
                sum(l.__dict__[f.name] for l in loglines) / count
            )

    limits_stats = _get_limits_elasped(loglines, time_elapsed.total_seconds())

    return LogStats(
        time_range=(start_t, end_t),
        time_elapsed=time_elapsed,
        max_cpu_temp=max_cpu_temp,
        time_above_90=time_above_90,
        percent_above_90=percent_above_90,
        limits=limits_stats,
        **avg_dict,
    )
