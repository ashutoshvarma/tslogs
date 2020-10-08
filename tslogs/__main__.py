import argparse
import json
import logging
import os
import sys
import textwrap
from ast import parse
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from tslogs import __version__ as ver
from tslogs import get_stats, load_files

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    # formatter = logging.Formatter('%(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _to_dict(lines: Iterable[Any]) -> str:
    return [asdict(l) for l in lines]


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

    parser.add_argument(
        "--quiet", "-q", action="store_true", default=False, help="Run in silent mode"
    )
    parser.add_argument(
        "--version", "-v", action="store_true", default=False, help="print version info"
    )
    return parser


def main(args=None):
    setup_logging()

    P = init_argparse()
    A = P.parse_args(args=args)

    if A.version:
        ver_str = f"""\
            tslogs v{ver}
            Copyright(c) 2020 Ashutosh Varma
            Report Bugs - https://github.com/ashutoshvarma/tslogs/issues
        """
        logger.info(textwrap.dedent(ver_str))
        return 0

    if A.quiet:
        logger.setLevel(logging.ERROR)

    date_range = None
    if len(A.dates) == 1:
        date_range = []
        date_range.insert(0, A.dates[0])
        date_range.insert(1, datetime(9999, 1, 1, 1))
    elif len(A.dates) >= 2:
        date_range = A.dates[:2]

    parsed = load_files(A.paths, date_range)
    logger.info(f"{len(parsed)} logs parsed.")

    if A.plot:
        content = "NotImplemented" + os.linesep
        pass
    elif A.json:
        content = json.dumps([asdict(l) for l in parsed], default=str, indent=4)
    else:
        if len(parsed) > 0:
            content = (
                json.dumps(asdict(get_stats(parsed)), default=str, indent=4)
                + os.linesep
            )
        else:
            content = ""

    if A.output != sys.stdout:
        content = content.encode("utf-8")
    A.output.write(content)


if __name__ == "__main__":
    sys.exit(main())
