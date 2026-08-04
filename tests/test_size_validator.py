import pytest

from src.config import load_config
from src.schemas import (
    AgentState,
    AgentType,
    BiologicalHypothesis,
    BiologicalScale,
    EnvironmentSpecification,
    InitialCondition,
    InteractionRule,
    ModelSpecification,
    OutputMetric,
    ResearchQuestion,
    TimeSpecification,
)
from src.size_validator import assert_simulation_size, validate_simulation_size


def build_simple_spec():
    return ModelSpecification(
        title="Size test",
        research_question=ResearchQuestion(text="How do agents behave?"),
        biological_hypothesis=BiologicalHypothesis(text="They interact."),
        biological_scale=BiologicalScale.cellular,
        agent_types=[AgentType(name="Cell")],
        agent_states=[AgentState(agent_type="Cell", name="healthy")],
        agent_behaviors=[{"description": "Move"}],
        interaction_rules=[InteractionRule(trigger="Near", effect="Move", probability=0.2, agents_involved=["Cell"])],
        environment=EnvironmentSpecification(environment_type="Two-dimensional grid", grid_width=10, grid_height=10),
        initial_conditions=[InitialCondition(agent_type="Cell", count=10)],
        time_specification=TimeSpecification(steps=10, duration_per_step="1 hour"),
        output_metrics=[OutputMetric(name="Cell count")],
        scenarios=[{"name": "baseline", "description": "Baseline."}],
    )


def test_simulation_within_limits_is_valid():
    spec = build_simple_spec()
    result = validate_simulation_size(spec)
    assert result.valid
    assert not result.messages


def test_excessive_agent_count_blocks_execution(monkeypatch):
    config = load_config()
    spec = build_simple_spec()
    spec.initial_conditions[0].count = config.sim_max_initial_agents + 1
    result = validate_simulation_size(spec)
    assert not result.valid
    assert "Initial agent count" in result.messages[0]


def test_excessive_steps_blocks_execution(monkeypatch):
    config = load_config()
    spec = build_simple_spec()
    spec.time_specification.steps = config.sim_max_steps + 1
    result = validate_simulation_size(spec)
    assert not result.valid
    assert "Simulation steps" in " ".join(result.messages)


def test_excessive_workload_score_blocks_execution(monkeypatch):
    config = load_config()
    spec = build_simple_spec()
    spec.initial_conditions[0].estimated_max_count = config.sim_max_initial_agents
    spec.time_specification.steps = config.sim_max_workload_score // config.sim_max_initial_agents + 2
    result = validate_simulation_size(spec)
    assert not result.valid
    assert "Estimated workload" in " ".join(result.messages)


def test_assert_simulation_size_raises():
    spec = build_simple_spec()
    spec.initial_conditions[0].count = 1000000
    with pytest.raises(Exception):
        assert_simulation_size(spec)
