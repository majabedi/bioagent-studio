from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

import matplotlib.pyplot as plt


def plot_time_series(time_series: List[Dict[str, int]]):
    if not time_series:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No data to display", ha="center", va="center")
        return fig

    series: Dict[str, List[int]] = defaultdict(list)
    for entry in time_series:
        for key, count in entry.items():
            series[key].append(count)
        for missing in set(series) - set(entry):
            series[missing].append(0)

    fig, ax = plt.subplots(figsize=(8, 4))
    for key, values in series.items():
        ax.plot(values, label=key)

    ax.set_xlabel("Step")
    ax.set_ylabel("Count")
    ax.set_title("Agent counts over time")
    ax.legend(loc="upper right", fontsize="small")
    fig.tight_layout()
    return fig


def plot_spatial_state(final_agents: List[object], grid_width: int, grid_height: int):
    fig, ax = plt.subplots(figsize=(6, 6))
    positions = {}
    for agent in final_agents:
        positions.setdefault(agent.type_name, []).append(agent.position)

    markers = ["o", "s", "^", "D", "x"]
    for index, (agent_type, coords) in enumerate(positions.items()):
        xs, ys = zip(*coords) if coords else ([], [])
        ax.scatter(xs, ys, label=agent_type, marker=markers[index % len(markers)], alpha=0.8)

    ax.set_xlim(-0.5, grid_width - 0.5)
    ax.set_ylim(-0.5, grid_height - 0.5)
    ax.set_title("Final spatial agent distribution")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(fontsize="small")
    ax.set_aspect("equal")
    fig.tight_layout()
    return fig
