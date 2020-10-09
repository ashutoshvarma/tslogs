import argparse
import json
import logging
import os
import sys
import textwrap
from ast import parse
from dataclasses import asdict
from datetime import datetime
from os import stat
from pathlib import Path
from typing import Any, Iterable, List

from tslogs import __version__, get_stats, load_files
from tslogs.parse import LogLine
from tslogs.stats import LogStats

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        type=Path,
        default=None,
        nargs="+",
        help="One or more paths to log dir or log files.",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--json",
        "-j",
        action="store_true",
        default=False,
        help="dump all parsed log data.",
    )
    mode_group.add_argument(
        "--plot", "-p", action="store_true", default=False, help="plot data"
    )

    filter_group = parser.add_argument_group("Filter")
    filter_group.add_argument(
        "--dates",
        type=datetime.fromisoformat,
        nargs="+",
        default=[],
        help="Datetime range to filter (in ISO format, yyyy-mm-dd HH:MM:SS)",
        metavar=("start_date", "end_date"),
    )

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("wb"),
        default=sys.stdout,
        help="Output file path, default is '-' (stdout)",
        metavar="file",
    )
    output_group.add_argument(
        "--indent",
        type=int,
        default=4,
        help="indent value for json output, default is 4",
        metavar="value",
    )

    parser.add_argument(
        "--quiet", "-q", action="store_true", default=False, help="Run in silent mode"
    )
    parser.add_argument(
        "--version", "-v", action="store_true", default=False, help="print version info"
    )
    return parser


def print_version():
    ver_str = f"""\
        tslogs v{__version__}
        Copyright(c) 2020 Ashutosh Varma
        Report Bugs - https://github.com/ashutoshvarma/tslogs/issues
    """
    logger.info(textwrap.dedent(ver_str))


def dump_json(loglines: List[LogLine], indent: int, out_fp: argparse.FileType) -> None:
    content = json.dumps([asdict(l) for l in loglines], default=str, indent=indent)
    if "b" in out_fp.mode:
        content = content.encode("utf-8")
    out_fp.write(content + os.linesep)


def print_stats(stats: LogStats):
    dt_fmt = "%d-%b-%y %H:%M"
    start_t: str = stats.time_range[0].strftime(dt_fmt)
    end_t: str = stats.time_range[1].strftime(dt_fmt)
    logger.info(f"Logs from {start_t} to {end_t}")
    logger.info(f"Total Log time - {stats.time_elapsed}")

    logger.info(f"{os.linesep}CPU Stats")
    logger.info(f"Average CPU Temp - {stats.avg_cpu_temp:.2f}°C")
    logger.info(
        f"Average CPU Multiplier - {stats.avg_multi:.2f} (~ {stats.avg_multi/10:.2f} GHz)"
    )
    logger.info(
        f"Time above 90°C - {stats.time_above_90} (~ {stats.percent_above_90:.2f}%)"
    )

    logger.info(f"{os.linesep}GPU Stats")
    logger.info(f"Average GPU Temp - {stats.avg_gpu_temp:.2f}°C")
    logger.info(f"Average GPU MHz - {stats.avg_gpu_mhz:.2f} MHz")

    logger.info(f"{os.linesep}Power Stats")
    logger.info(f"Average Power - {stats.avg_power:.2f} W")
    logger.info(f"Average VID - {stats.avg_vid:.4f} V")
    logger.info(f"Average Battery Voltage - {stats.avg_battery_mw:.2f} mW")

    logger.info(f"{os.linesep}Limits Stats")
    for lm_stat in stats.limits:
        logger.info(
            f"{lm_stat.limit} Limit - {lm_stat.total_secs} sec (~ {lm_stat.percent_time:.2f}%)"
        )


def main(args=None):
    setup_logging()

    P = init_argparse()
    A = P.parse_args(args=args)

    if A.version:
        print_version()
        return 0

    if A.quiet:
        logger.setLevel(logging.ERROR)

    # fix date range
    date_range: List[datetime] = []
    if len(A.dates) == 1:
        date_range.insert(0, A.dates[0])
        date_range.insert(1, datetime(9999, 1, 1, 1))
    elif len(A.dates) >= 2:
        date_range = A.dates[:2]

    parsed = load_files(A.paths, date_range)
    logger.info(f"{len(parsed)} logs parsed.")

    if A.plot:
        raise NotImplementedError
    elif A.json:
        dump_json(parsed, A.indent, A.output)
    else:
        print_stats(get_stats(parsed))


if __name__ == "__main__":
    sys.exit(main())
