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
from src.simulation_engine import ControlledSimulator


def build_simulation_spec():
    return ModelSpecification(
        title="Engine test",
        research_question=ResearchQuestion(text="What happens when cells interact?"),
        biological_hypothesis=BiologicalHypothesis(text="Interactions shape population dynamics."),
        biological_scale=BiologicalScale.cellular,
        agent_types=[AgentType(name="Epithelial cells"), AgentType(name="Immune cells")],
        agent_states=[
            AgentState(agent_type="Epithelial cells", name="healthy"),
            AgentState(agent_type="Immune cells", name="inactive"),
        ],
        agent_behaviors=[{"description": "Immune cells move toward infected cells and remove them."}],
        interaction_rules=[
            InteractionRule(
                trigger="Immune cell next to infected cell",
                effect="Remove infected cell",
                probability=0.3,
                agents_involved=["Immune cells", "Epithelial cells"],
            )
        ],
        environment=EnvironmentSpecification(environment_type="Two-dimensional grid", grid_width=10, grid_height=10),
        initial_conditions=[
            InitialCondition(agent_type="Epithelial cells", count=5),
            InitialCondition(agent_type="Immune cells", count=3),
        ],
        time_specification=TimeSpecification(steps=5, duration_per_step="1 hour"),
        output_metrics=[OutputMetric(name="Cell counts")],
        scenarios=[{"name": "baseline", "description": "Baseline response."}],
    )


def test_simulation_under_limits_can_run():
    spec = build_simulation_spec()
    simulator = ControlledSimulator(spec, seed=123)
    result = simulator.run()
    assert result.diagnostics["steps"] == 5
    assert isinstance(result.time_series, list)
    assert result.diagnostics["random_seed"] == 123


def test_reproducible_seed_produces_same_result():
    spec = build_simulation_spec()
    result_a = ControlledSimulator(spec, seed=42).run()
    result_b = ControlledSimulator(spec, seed=42).run()
    assert result_a.time_series == result_b.time_series
    assert result_a.diagnostics == result_b.diagnostics


def test_unsupported_rule_is_reported():
    spec = build_simulation_spec()
    spec.interaction_rules.append(
        InteractionRule(
            trigger="Unknown signal",
            effect="Unknown behavior",
            probability=0.1,
            agents_involved=["Epithelial cells"],
        )
    )
    result = ControlledSimulator(spec, seed=42).run()
    assert any("Unsupported rule" in entry for entry in result.unsupported_rules)
