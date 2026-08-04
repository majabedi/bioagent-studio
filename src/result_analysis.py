from __future__ import annotations

from collections import Counter
from typing import Dict, List

import numpy as np
import pandas as pd

from src.schemas import ModelSpecification
from src.simulation_engine import SimulationResult


def summarize_results(spec: ModelSpecification, result: SimulationResult) -> Dict[str, object]:
    final_counts = Counter()
    alive_counts = Counter()
    for agent in result.final_agents:
        final_counts[agent.type_name] += 1
        if agent.alive:
            alive_counts[agent.type_name] += 1

    df = pd.DataFrame(result.time_series).fillna(0).astype(int)
    peak_counts = df.max(axis=0).to_dict() if not df.empty else {}
    total_agents = len(result.final_agents)
    survivors = sum(alive_counts.values())
    survival_percentage = float(np.round((survivors / total_agents * 100), 2)) if total_agents else 0.0

    summary = {
        "final_populations": dict(final_counts),
        "surviving_populations": dict(alive_counts),
        "peak_counts": peak_counts,
        "time_series_length": len(result.time_series),
        "final_total_agents": total_agents,
        "survival_percentage": survival_percentage,
    }
    return summary


def build_interpretation_prompt(spec: ModelSpecification, result: SimulationResult) -> str:
    interpretation_lines = [
        f"Research question: {spec.research_question.text}",
        f"Hypothesis: {spec.biological_hypothesis.text}",
        "Simulation diagnostics:",
    ]
    interpretation_lines.append(f"- Steps: {result.diagnostics.get('steps')}")
    interpretation_lines.append(f"- Seed: {result.diagnostics.get('random_seed')}")
    interpretation_lines.append("Final agent counts:")
    for key, value in Counter([a.type_name for a in result.final_agents]).items():
        interpretation_lines.append(f"- {key}: {value}")
    interpretation_lines.append(
        "Provide a cautious interpretation making clear that this is model-dependent and not experimental proof."
    )
    return "\n".join(interpretation_lines)
