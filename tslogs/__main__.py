import argparse
import io
import json
import logging
import os
import sys
import textwrap
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Union

import colorama
import matplotlib.pyplot as plt
from colorama.ansi import Fore, Style

from tslogs import __version__
from tslogs.data_ploting import ALLOWED_INPUTS, PlotInput, plot_logs
from tslogs.parse import LogLine, load_files
from tslogs.stats import LogStats, get_stats

logger = logging.getLogger(__name__)


# ANSI colors
RESET = Style.RESET_ALL
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
BLUE = Fore.BLUE
RED = Fore.RED

DIM = Style.DIM
BOLD = Style.BRIGHT


# https://github.com/psf/black/blob/dd2f86ac0a043815821d228b9db036a295be5372/src/black/__init__.py#L872
def wrap_stream_for_windows(
    f: io.TextIOWrapper,
) -> Union[io.TextIOWrapper, "colorama.AnsiToWin32"]:
    """
    Wrap stream with colorama's wrap_stream so colors are shown on Windows.
    If `colorama` is unavailable, the original stream is returned unmodified.
    Otherwise, the `wrap_stream()` function determines whether the stream needs
    to be wrapped for a Windows environment and will accordingly either return
    an `AnsiToWin32` wrapper or the original stream.
    """
    try:
        from colorama.initialise import wrap_stream
    except ImportError:
        return f
    else:
        # Set `strip=False` to avoid needing to modify test_express_diff_with_color.
        return wrap_stream(f, convert=None, strip=False, autoreset=False, wrap=True)


class CustomFormatter(argparse.HelpFormatter):
    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        if action.nargs == argparse.ZERO_OR_MORE:
            return ""
        elif action.nargs == argparse.ONE_OR_MORE:
            return "%s %s" % get_metavar(2)
        else:
            return super()._format_args(action, default_metavar)

    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ", ".join(action.option_strings) + " " + args_string


def setup_logging() -> None:
    logger = logging.getLogger(__name__)

    log_stream = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", write_through=True
    )
    handler = logging.StreamHandler(wrap_stream_for_windows(log_stream))
    # formatter = logging.Formatter('%(levelname)-8s %(message)s')
    # handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def _arg_check_positive(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(formatter_class=CustomFormatter)
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
        "--plot",
        "-p",
        nargs="*",
        choices=ALLOWED_INPUTS,
        help=(
            "Plot given the logs attributes (default: %(default)s)."
            " Allowed values are {%(choices)s}"
        ),
        metavar="INPUTS",
    )

    filter_group = parser.add_argument_group("Filter")
    filter_group.add_argument(
        "--dates",
        "-d",
        type=datetime.fromisoformat,
        nargs="+",
        default=[],
        help="Datetime range to filter (in ISO format, yyyy-mm-dd HH:MM:SS)",
        metavar=("START", "END"),
    )

    plot_group = parser.add_argument_group("Plot Options")
    plot_group.add_argument("--interval", "-I", type=_arg_check_positive, default=60)
    plot_group.add_argument("--smooth", "-S", type=_arg_check_positive, default=2)

    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--output",
        "-o",
        type=argparse.FileType("wb"),
        default=sys.stdout,
        help="Output file path, default is '-' (stdout)",
        metavar="FILE",
    )
    output_group.add_argument(
        "--indent",
        type=int,
        default=4,
        help="indent value for json output, default is 4",
        metavar="VALUE",
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
    content = json.dumps([asdict(log) for log in loglines], default=str, indent=indent)
    if "b" in out_fp.mode:
        content = content.encode("utf-8")
    out_fp.write(content + os.linesep)


def print_stats(stats: LogStats):
    def _print(name: str, value: Any, meta: str = "", value_color=""):
        color = value_color
        if meta:
            logger.info(f"- {name:30}: {BOLD}{color}{str(value):10} ({meta}){RESET}")
        else:
            logger.info(f"- {name:30}: {BOLD}{color}{str(value):10}{RESET}")

    def _print_sub_head(name: str):
        logger.info(f"{DIM}{YELLOW}{name}{RESET}")

    def nl():
        logger.info("")

    dt_fmt = "%d-%b-%y %H:%M"
    start_t: str = stats.time_range[0].strftime(dt_fmt)
    end_t: str = stats.time_range[1].strftime(dt_fmt)
    _print_sub_head(f"Logs from {BOLD}{start_t}{DIM} to {BOLD}{end_t}")
    _print("Total Log time", stats.time_elapsed)
    nl()
    _print_sub_head("CPU Stats")
    _print("Average CPU Temp", f"{stats.avg_cpu_temp:.2f}°C")
    _print("Max CPU Temp", f"{stats.max_cpu_temp:.2f}°C", value_color=RED)
    _print(
        "Average CPU Multiplier",
        f"{stats.avg_multi:.2f}",
        f"~ {stats.avg_multi/10:.2f} GHz",
    )
    _print(
        "Time above 90°C", stats.time_above_90, f"{stats.percent_above_90:.2f}%", RED
    )
    nl()
    _print_sub_head("GPU Stats")
    _print("Average GPU Temp", f"{stats.avg_gpu_temp:.2f}°C")
    _print("Average GPU MHz", f"{stats.avg_gpu_mhz:.2f} MHz")
    nl()
    _print_sub_head("Power Stats")
    _print("Average Power", f"{stats.avg_power:.2f} W")
    _print("Average VID", f"{stats.avg_vid:.4f} V")
    _print("Average Battery Voltage", f"{stats.avg_battery_mw:.2f} mW")

    if len(stats.limits) > 0:
        nl()
        _print_sub_head("Limits Stats")
        for lm_stat in stats.limits:
            _print(
                f"{lm_stat.limit} Limit",
                f"{lm_stat.total_secs} sec",
                f"~ {lm_stat.percent_time:.2f}%",
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

    # try to parse log files
    parsed = load_files(A.paths, date_range)
    logger.info(f"{GREEN}{len(parsed)} logs parsed{RESET}")

    if len(parsed) > 0:
        if A.plot is not None:
            if len(A.plot) == 0:
                A.plot.append(PlotInput("cpu_temp", color="red"))
            plot_logs(parsed, A.plot, A.interval, A.smooth)
            if A.output != sys.stdout:
                plt.savefig(A.output, format="png")
            else:
                plt.show()
        elif A.json:
            dump_json(parsed, A.indent, A.output)
        else:
            print_stats(get_stats(parsed))
    else:
        logger.info(f"{BOLD}{YELLOW}No logs found 😴{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
