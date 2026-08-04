from __future__ import annotations

from typing import List

from src.schemas import ModelSpecification


def generate_python_code(spec: ModelSpecification) -> str:
    parameters = []
    for condition in spec.initial_conditions:
        parameters.append(f"    '{condition.agent_type}': {condition.count}")
    parameter_block = ",\n".join(parameters)

    behavior_block = "\n".join(
        [f"# - {behavior.description}" for behavior in spec.agent_behaviors]
    )
    scenario_block = "\n".join(
        [f"# - {scenario.name}: {scenario.description or ''}" for scenario in spec.scenarios]
    )
    code = (
        '"""Generated simulation code for the configured biological model.\n'
        'This code is provided as an artifact for inspection and is not executed automatically.\n'
        '"""\n\n'
        'import random\n'
        'import matplotlib.pyplot as plt\n\n'
        f'model_title = {spec.title!r}\n'
        f'research_question = {spec.research_question.text!r}\n'
        f'biological_hypothesis = {spec.biological_hypothesis.text!r}\n\n'
        f'environment = {spec.environment.environment_type.value!r}\n'
        f'grid_width = {spec.environment.grid_width}\n'
        f'grid_height = {spec.environment.grid_height}\n\n'
        'initial_conditions = {\n'
        f'{parameter_block}\n'
        '}\n\n'
        f'time_steps = {spec.time_specification.steps}\n'
        f'duration_per_step = {spec.time_specification.duration_per_step!r}\n\n'
        f'output_metrics = { [metric.name for metric in spec.output_metrics]!r }\n\n'
        '# Agent behaviors\n'
        f'{behavior_block}\n\n'
        '# Scenarios\n'
        f'{scenario_block}\n\n'
        f'seed = {spec.replicates}\n'
        'random.seed(seed)\n\n'
        'class Agent:\n'
        '    def __init__(self, agent_type, state, position):\n'
        '        self.agent_type = agent_type\n'
        '        self.state = state\n'
        '        self.position = position\n'
        '        self.alive = True\n\n\n'
        'agents = []\n'
        'for agent_type, count in initial_conditions.items():\n'
        '    for _ in range(count):\n'
        "        agents.append(Agent(agent_type, 'default', (0, 0)))\n"
        '\n'
        'counts_over_time = []\n'
        'for step in range(time_steps):\n'
        '    counts = {}\n'
        '    for agent in agents:\n'
        '        if not agent.alive:\n'
        '            continue\n'
        '        counts[agent.agent_type] = counts.get(agent.agent_type, 0) + 1\n'
        '    counts_over_time.append(counts)\n\n'
        'plt.figure(figsize=(8, 4))\n'
        'for agent_type in initial_conditions.keys():\n'
        '    series = [counts.get(agent_type, 0) for counts in counts_over_time]\n'
        '    plt.plot(series, label=agent_type)\n\n'
        'plt.title(\'Agent counts over time\')\n'
        'plt.xlabel(\'Step\')\n'
        'plt.ylabel(\'Count\')\n'
        'plt.legend()\n'
        'plt.tight_layout()\n'
        'plt.show()\n'
    )
    return code
