from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.exceptions import SimulationError, UnsupportedRuleError
from src.schemas import (
    EnvironmentSpecification,
    EnvironmentType,
    ExperimentalScenario,
    InitialCondition,
    InteractionRule,
    ModelSpecification,
)


@dataclass
class Agent:
    id: int
    type_name: str
    state_name: str
    position: Tuple[int, int]
    age: int = 0
    alive: bool = True
    activation: float = 0.0
    infection: float = 0.0
    energy: float = 1.0


@dataclass
class SimulationResult:
    time_series: List[Dict[str, int]]
    final_agents: List[Agent]
    diagnostics: Dict[str, object]
    unsupported_rules: List[str] = field(default_factory=list)


class ControlledSimulator:
    def __init__(self, spec: ModelSpecification, seed: int = 42) -> None:
        self.spec = spec
        self.seed = seed
        self.random = random.Random(seed)
        self.environment = spec.environment
        self.grid_width = self.environment.grid_width or 20
        self.grid_height = self.environment.grid_height or 20
        self.agents: List[Agent] = []
        self.unsupported_rules: List[str] = []

    def _parse_initial_conditions(self, scenario: ExperimentalScenario) -> None:
        self.agents = []
        next_id = 1
        for initial_condition in self.spec.initial_conditions:
            count = initial_condition.count
            for _ in range(count):
                position = self._sample_position()
                state_name = self._default_state_for_agent(initial_condition.agent_type)
                self.agents.append(
                    Agent(
                        id=next_id,
                        type_name=initial_condition.agent_type,
                        state_name=state_name,
                        position=position,
                    )
                )
                next_id += 1

    def _sample_position(self) -> Tuple[int, int]:
        if self.environment.environment_type == EnvironmentType.grid:
            return (self.random.randrange(self.grid_width), self.random.randrange(self.grid_height))
        return (0, 0)

    def _default_state_for_agent(self, agent_type: str) -> str:
        matching_states = [s.name for s in self.spec.agent_states if s.agent_type == agent_type]
        return matching_states[0] if matching_states else "active"

    def _neighbors(self, agent: Agent) -> List[Agent]:
        return [
            other
            for other in self.agents
            if other.alive
            and other.id != agent.id
            and abs(other.position[0] - agent.position[0]) <= 1
            and abs(other.position[1] - agent.position[1]) <= 1
        ]

    def _apply_movements(self, agent: Agent, behavior_text: str) -> None:
        if "move" not in behavior_text.lower():
            return
        dx = self.random.choice([-1, 0, 1])
        dy = self.random.choice([-1, 0, 1])
        new_x = max(0, min(self.grid_width - 1, agent.position[0] + dx))
        new_y = max(0, min(self.grid_height - 1, agent.position[1] + dy))
        agent.position = (new_x, new_y)

    def _apply_rules(self, agent: Agent) -> None:
        for rule in self.spec.interaction_rules:
            text = f"{rule.trigger} {rule.effect}".lower()
            handled = False
            if "infect" in text and agent.type_name.lower().startswith("infected"):
                handled = True
                for neighbor in self._neighbors(agent):
                    if self.random.random() < (rule.probability or 0.1):
                        neighbor.infection = min(1.0, neighbor.infection + 0.3)
                        neighbor.state_name = "infected"
            elif "remove" in text or "kill" in text or "clear" in text:
                handled = True
                for neighbor in self._neighbors(agent):
                    if self.random.random() < (rule.probability or 0.1):
                        if "infected" in neighbor.type_name.lower() or "infected" in neighbor.state_name.lower():
                            neighbor.alive = False
                            neighbor.state_name = "dead"
            elif "divide" in text or "prolifer" in text:
                handled = True
                if self.random.random() < (rule.probability or 0.05):
                    self._divide_agent(agent)
            elif "die" in text and "infected" in agent.state_name.lower():
                handled = True
                if self.random.random() < (rule.probability or 0.05):
                    agent.alive = False
                    agent.state_name = "dead"
            elif "activate" in text and "immune" in agent.type_name.lower():
                handled = True
                agent.activation = min(1.0, agent.activation + 0.2)
            elif "signal" in text and ("produce" in text or "respond" in text or "signal" in rule.effect.lower()):
                handled = True
                agent.energy = max(0.0, agent.energy - 0.05)
            if not handled:
                self._record_unsupported(rule)

    def _record_unsupported(self, rule: InteractionRule) -> None:
        rule_text = f"Unsupported rule: trigger={rule.trigger}, effect={rule.effect}"
        if rule_text not in self.unsupported_rules:
            self.unsupported_rules.append(rule_text)

    def _divide_agent(self, agent: Agent) -> None:
        if len(self.agents) >= 1000:
            return
        new_id = max(a.id for a in self.agents) + 1
        self.agents.append(
            Agent(
                id=new_id,
                type_name=agent.type_name,
                state_name=agent.state_name,
                position=agent.position,
            )
        )

    def _collect_metrics(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for agent in self.agents:
            if agent.alive:
                key = f"{agent.type_name}:{agent.state_name}"
                counts[key] = counts.get(key, 0) + 1
        return counts

    def run(self) -> SimulationResult:
        if not self.spec.scenarios:
            raise SimulationError("No scenarios are configured for this simulation.")

        start_time = time.time()
        self._parse_initial_conditions(self.spec.scenarios[0])
        time_series: List[Dict[str, int]] = []
        for step in range(self.spec.time_specification.steps):
            current_counts = self._collect_metrics()
            time_series.append(current_counts)
            for agent in list(self.agents):
                if not agent.alive:
                    continue
                agent.age += 1
                for behavior in self.spec.agent_behaviors:
                    self._apply_movements(agent, behavior.description)
                self._apply_rules(agent)

        diagnostics = {
            "runtime_seconds": round(time.time() - start_time, 3),
            "random_seed": self.seed,
            "steps": self.spec.time_specification.steps,
            "initial_agent_count": sum(ic.count for ic in self.spec.initial_conditions),
            "maximum_agent_count": max((ic.estimated_max_count or ic.count) for ic in self.spec.initial_conditions),
            "scenario_count": len(self.spec.scenarios),
            "replicates": self.spec.replicates,
            "workload_score": self.spec.time_specification.steps
            * max((ic.estimated_max_count or ic.count) for ic in self.spec.initial_conditions)
            * len(self.spec.scenarios)
            * self.spec.replicates,
        }

        return SimulationResult(
            time_series=time_series,
            final_agents=[agent for agent in self.agents if agent.alive],
            diagnostics=diagnostics,
            unsupported_rules=self.unsupported_rules,
        )
