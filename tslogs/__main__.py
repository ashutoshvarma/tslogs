import argparse
import json
import sys
from ast import parse
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

from tslogs import LogLine, load_files, parse_log

# from parse import LogLine, parse_log


# from thlogs.parse import LogLine
# from thlogs.parse import LogLine


def dump_json(lines: Iterable[LogLine]) -> str:
    return json.dumps([asdict(l) for l in lines], default=str, indent=4)


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "paths",
        type=Path,
        default=None,
        nargs="+",
        help="One or more paths to log dir or files.",
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--json", "-j", action="store_true", default=False, help="Dump log data as json"
    )
    mode_group.add_argument(
        "--plot", "-p", action="store_true", default=False, help="Plot data"
    )

    filter_group = parser.add_argument_group("Filter")
    filter_group.add_argument(
        "--dates",
        "-d",
        type=datetime.fromisoformat,
        nargs="+",
        default=[],
        help="Datetime range to filter",
    )

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output", "-o", type=argparse.FileType("wb"), default=sys.stdout
    )

    return parser


def main(args=None):
    P = init_argparse()
    A = P.parse_args(args=args)
    print(A)

    date_range = None
    if len(A.dates) == 1:
        date_range = []
        date_range.insert(0, datetime(1, 1, 1, 1))
        date_range.insert(1, A.dates[0])
    elif len(A.dates) >= 2:
        date_range = A.dates[:2]

    parsed = load_files(A.paths, date_range)

    if A.json:
        dump = dump_json(parsed)
        if A.output == sys.stdout:
            A.output.write(dump)
        else:
            A.output.write(dump.encode("utf-8"))
    elif A.plot:
        # Plot functions
        pass
    else:
        # pritn info
        pass


if __name__ == "__main__":
    sys.exit(main())
