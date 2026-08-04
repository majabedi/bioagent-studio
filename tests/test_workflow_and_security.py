import os

import pytest

from src.code_generator import generate_python_code
from src.config import AppConfig
from src.exceptions import ConfigError
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


def build_simple_spec():
    return ModelSpecification(
        title="Security test",
        research_question=ResearchQuestion(text="Why?"),
        biological_hypothesis=BiologicalHypothesis(text="Because."),
        biological_scale=BiologicalScale.cellular,
        agent_types=[AgentType(name="Cell")],
        agent_states=[AgentState(agent_type="Cell", name="healthy")],
        agent_behaviors=[{"description": "Move"}],
        interaction_rules=[InteractionRule(trigger="Near", effect="Move", probability=0.1, agents_involved=["Cell"])],
        environment=EnvironmentSpecification(environment_type="Two-dimensional grid", grid_width=5, grid_height=5),
        initial_conditions=[InitialCondition(agent_type="Cell", count=2)],
        time_specification=TimeSpecification(steps=3, duration_per_step="1 hour"),
        output_metrics=[OutputMetric(name="Count")],
        scenarios=[{"name": "baseline", "description": "Baseline."}],
    )


def test_generated_code_does_not_contain_exec_or_eval_or_subprocess():
    spec = build_simple_spec()
    code = generate_python_code(spec)
    assert "exec(" not in code
    assert "eval(" not in code
    assert "subprocess" not in code


def test_missing_environment_variables_produce_config_error(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    with pytest.raises(ConfigError):
        AppConfig()
