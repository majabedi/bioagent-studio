from __future__ import annotations

from typing import List, Tuple

from src.config import load_config
from src.exceptions import SimulationSizeError
from src.schemas import EnvironmentType, InitialCondition, ModelSpecification


class SizeValidationResult:
    def __init__(self, valid: bool, messages: List[str]):
        self.valid = valid
        self.messages = messages


def estimate_workload(spec: ModelSpecification) -> int:
    max_agents = max(
        [ic.estimated_max_count or ic.count for ic in spec.initial_conditions] + [0]
    )
    steps = spec.time_specification.steps
    scenarios = len(spec.scenarios)
    replicates = spec.replicates or 1
    return max_agents * steps * scenarios * replicates


def validate_simulation_size(spec: ModelSpecification) -> SizeValidationResult:
    config = load_config()
    messages: List[str] = []

    total_initial_agents = sum(ic.count for ic in spec.initial_conditions)
    if total_initial_agents > config.sim_max_initial_agents:
        messages.append(
            f"Initial agent count {total_initial_agents} exceeds the limit of {config.sim_max_initial_agents}."
        )

    max_estimated_agents = max(
        [ic.estimated_max_count or ic.count for ic in spec.initial_conditions] + [0]
    )
    if max_estimated_agents > config.sim_max_initial_agents:
        messages.append(
            f"Estimated maximum agent count {max_estimated_agents} exceeds the limit of {config.sim_max_initial_agents}."
        )

    if spec.time_specification.steps > config.sim_max_steps:
        messages.append(
            f"Simulation steps {spec.time_specification.steps} exceeds the limit of {config.sim_max_steps}."
        )

    grid_cells = 1
    if spec.environment.environment_type == EnvironmentType.grid:
        grid_cells = spec.environment.grid_width * spec.environment.grid_height
    if grid_cells > config.sim_max_grid_cells:
        messages.append(
            f"Grid size {grid_cells} cells exceeds the limit of {config.sim_max_grid_cells}."
        )

    if len(spec.scenarios) > config.sim_max_scenarios:
        messages.append(
            f"Scenario count {len(spec.scenarios)} exceeds the limit of {config.sim_max_scenarios}."
        )

    if spec.replicates > config.sim_max_replicates:
        messages.append(
            f"Replicate count {spec.replicates} exceeds the limit of {config.sim_max_replicates}."
        )

    workload_score = estimate_workload(spec)
    if workload_score > config.sim_max_workload_score:
        messages.append(
            f"Estimated workload {workload_score} exceeds the limit of {config.sim_max_workload_score}."
        )

    valid = len(messages) == 0
    return SizeValidationResult(valid=valid, messages=messages)


def assert_simulation_size(spec: ModelSpecification) -> None:
    result = validate_simulation_size(spec)
    if not result.valid:
        raise SimulationSizeError("Simulation size validation failed: " + " ".join(result.messages))
