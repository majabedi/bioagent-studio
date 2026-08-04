import pytest

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
    ParameterSource,
    ResearchQuestion,
    TimeSpecification,
)


def build_minimal_valid_spec():
    return ModelSpecification(
        title="Test model",
        research_question=ResearchQuestion(text="How does A affect B?"),
        biological_hypothesis=BiologicalHypothesis(text="A increases B."),
        biological_scale=BiologicalScale.cellular,
        agent_types=[AgentType(name="Cell", role="Target")],
        agent_states=[AgentState(agent_type="Cell", name="healthy")],
        agent_behaviors=[{"description": "Move and interact"}],
        interaction_rules=[InteractionRule(trigger="Near", effect="Change state", probability=0.5, agents_involved=["Cell"])],
        environment=EnvironmentSpecification(environment_type="Two-dimensional grid", grid_width=10, grid_height=10),
        initial_conditions=[InitialCondition(agent_type="Cell", count=10, estimated_max_count=20)],
        time_specification=TimeSpecification(steps=10, duration_per_step="1 hour"),
        output_metrics=[OutputMetric(name="Cell count")],
        scenarios=[{"name": "baseline", "description": "Base scenario"}],
        assumptions=[],
        uncertainties=[],
        parameter_definitions=[],
        additional_information="None.",
    )


def test_valid_model_specification_passes_validation():
    spec = build_minimal_valid_spec()
    assert spec.title == "Test model"
    assert spec.research_question.text == "How does A affect B?"


def test_invalid_probability_is_rejected():
    with pytest.raises(ValueError):
        InteractionRule(
            trigger="When X",
            effect="Y",
            probability=1.5,
            agents_involved=["Cell"],
        )


def test_negative_agent_counts_are_rejected():
    with pytest.raises(ValueError):
        InitialCondition(agent_type="Cell", count=-5)


def test_model_requires_at_least_one_scenario():
    with pytest.raises(ValueError):
        ModelSpecification(
            title="Bad model",
            research_question=ResearchQuestion(text="Why?"),
            biological_hypothesis=BiologicalHypothesis(text="Because."),
            biological_scale=BiologicalScale.cellular,
            agent_types=[AgentType(name="Cell")],
            agent_states=[AgentState(agent_type="Cell", name="healthy")],
            agent_behaviors=[{"description": "Do something"}],
            interaction_rules=[InteractionRule(trigger="X", effect="Y")],
            environment=EnvironmentSpecification(environment_type="Two-dimensional grid", grid_width=10, grid_height=10),
            initial_conditions=[InitialCondition(agent_type="Cell", count=1)],
            time_specification=TimeSpecification(steps=1, duration_per_step="1 hour"),
            output_metrics=[OutputMetric(name="Count")],
            scenarios=[],
        )
