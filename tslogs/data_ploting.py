from typing import Any, Dict, List, Literal, Optional, Tuple, Union, get_args
from tslogs.parse import LogLine
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass, fields, field
import math


PLOT_MODE = {
    "plot": plt.plot,
    "fill": plt.fill_between,
}
TAB_COLORS = Literal[
    "red", "blue", "green", "orange", "brown", "grey", "pink", "olive", "default"
]
ALLOWED_INPUTS = [f.name for f in fields(LogLine) if f.type == float]


@dataclass
class PlotInput:
    name: str
    color: Optional[TAB_COLORS] = "default"
    plot: Literal[list(PLOT_MODE.keys())] = "plot"
    kwargs: Dict[str, Any] = field(default_factory=lambda: {"linewidth": 1})
    label: Optional[str] = None


def convolve_average(arr, span):
    re = np.convolve(arr, np.ones(span * 2 + 1) / (span * 2 + 1), mode="same")

    # shrinks the averaging window on the side that
    # reaches beyond the data, keeps the other side the same size as given
    # by "span"
    re[0] = np.average(arr[:span])
    for i in range(1, span + 1):
        re[i] = np.average(arr[: i + span])
        re[-i] = np.average(arr[-i - span :])
    return re


def normalize_data(
    logs: List[LogLine],
    inputs: List[PlotInput],
    interval,
    smooth_span,
) -> Tuple[np.ndarray, np.ndarray]:
    # sort array
    logs.sort(key=lambda l: l.time)

    # time ranges
    s_time = np.datetime64(str(logs[0].time))
    e_time = np.datetime64(str(logs[-1].time))
    times = np.arange(
        s_time, e_time + np.timedelta64(1, "s"), np.timedelta64(interval, "s")
    )

    x_array = np.empty((len(inputs), len(times)))
    x_array[:] = np.nan

    for l in logs:
        ltime = l.time
        idx = int(((l.time - s_time.item()).total_seconds()) / interval)
        for i, inp in enumerate(inputs):
            x_array[i][idx] = getattr(l, inp.name)

    if smooth_span:
        for i in range(len(x_array)):
            x_array[i][:] = convolve_average(x_array[i], smooth_span)

    return times, x_array


def plot_logs(
    logs: List[LogLine],
    inputs: List[Union[str, PlotInput]],
    interval: Optional[int] = 1,
    smooth_span: Optional[int] = None,
    title=None,
    subplots_kwargs: Dict[str, Any] = {"figsize": (16, 9), "dpi": 80},
):
    # get valid LogLine fields
    valid_inputs = []
    for inp in inputs:
        if isinstance(inp, str):
            inp = PlotInput(inp)
        if (
            inp.name in [f.name for f in fields(LogLine)]
            and inp.plot in PLOT_MODE
            and inp.color in get_args(TAB_COLORS)
        ):
            valid_inputs.append(inp)
    # valid_inputs = [
    #     PlotInput(i) if isinstance(i, str) else i
    #     for i in inputs
    #     if i.name in [f.name for f in fields(LogLine)]
    #     and i.plot in PLOT_MODE
    #     and i.color in get_args(TAB_COLORS)
    # ]

    x_data, plot_data = normalize_data(logs, valid_inputs, interval, smooth_span)

    fig, ax = plt.subplots(1, 1, **subplots_kwargs)

    for i, inp in enumerate(valid_inputs):
        if inp.color != "default":
            inp.kwargs["color"] = f"tab:{inp.color}"
        else:
            inp.kwargs["color"] = f"C{i}"
        if inp.plot == "fill":
            inp.kwargs["alpha"] = inp.kwargs.get("alpha") or 0.5
        PLOT_MODE[inp.plot](
            x_data, plot_data[i], label=inp.label or inp.name, **inp.kwargs
        )

    max_y = max(np.nanmax(arr) for arr in plot_data)
    min_y = min(np.nanmin(arr) for arr in plot_data)

    # set title
    ax.set_title("ThrottleStop Logs", fontsize=18)
    ax.set_xlabel("Time", fontsize=16)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.07),
        # fancybox=True,
        # shadow=True,
        ncol=10,
        fontsize=12,
    )

    # ylim, xlim
    ylim = [math.floor((min_y) / 10) * 10, math.ceil((max_y * 1.01) / 10) * 10]
    xlim = [
        # calculate based on range of time
        x_data[0]
        - (
            (x_data[-1] - x_data[0]).astype("timedelta64[s]").astype("int") / 100
        ).astype("timedelta64[s]"),
        x_data[-1],
    ]
    ax.set(xlim=xlim, ylim=ylim)

    plt.xticks(fontsize=12, horizontalalignment="center")
    plt.yticks(fontsize=12)

    # y tick line
    plt.grid(axis="y")

    # Lighten borders
    plt.gca().spines["top"].set_alpha(0)
    plt.gca().spines["bottom"].set_alpha(0.3)
    plt.gca().spines["right"].set_alpha(0)
    plt.gca().spines["left"].set_alpha(0.3)

    return fig, ax
