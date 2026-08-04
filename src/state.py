from __future__ import annotations

from typing import Dict, List

DEFAULT_ANSWERS = {
    "research_question": "How do immune cells affect the clearance of virus-infected epithelial cells?",
    "biological_hypothesis": "Increasing the initial number of immune cells reduces viral burden but may increase tissue damage.",
    "biological_scale": "Cellular",
    "agent_types": "Epithelial cells, infected epithelial cells, and immune cells",
    "agent_states": "Epithelial cells can be healthy, infected, damaged, or dead. Immune cells can be inactive or activated.",
    "agent_behaviors": "Immune cells move toward infected cells, infected cells produce virus, and immune cells remove infected cells.",
    "interaction_rules": "When an immune cell is next to an infected cell, it has a 30% probability of removing that infected cell during each time step.",
    "environment": "A two-dimensional tissue grid representing an epithelial layer",
    "initial_conditions": "100 healthy epithelial cells\n10 infected epithelial cells\n20 immune cells",
    "simulation_steps": "100",
    "duration_per_step": "One step represents one hour.",
    "output_metrics": "Healthy-cell count, infected-cell count, immune-cell count, viral burden, and tissue damage over time",
    "additional_information": "Immune cells should become less effective after prolonged activation.",
    "experimental_scenarios": "Compare low, medium, and high initial immune-cell numbers.",
    "seed": "42",
}

QUESTIONS: List[Dict[str, str]] = [
    {
        "field": "research_question",
        "prompt": "What biological question would you like to investigate?",
        "explanation": "Describe the main scientific question, not implementation details.",
    },
    {
        "field": "biological_hypothesis",
        "prompt": "What hypothesis would you like the simulation to test?",
        "explanation": "Describe the biological hypothesis in plain language.",
    },
    {
        "field": "biological_scale",
        "prompt": "Which biological scale best fits the model?",
        "explanation": "Choose a biological scale for the simulation.",
    },
    {
        "field": "agent_types",
        "prompt": "Which biological entities should behave as individual agents?",
        "explanation": "List the relevant cell or organism types.",
    },
    {
        "field": "agent_states",
        "prompt": "What states can the agents have?",
        "explanation": "Describe the possible states for each agent type.",
    },
    {
        "field": "agent_behaviors",
        "prompt": "What can the agents do?",
        "explanation": "List the main biological behaviors the agents should show.",
    },
    {
        "field": "interaction_rules",
        "prompt": "How should the biological agents interact?",
        "explanation": "Describe conditions, effects, probabilities, and relevant agent types.",
    },
    {
        "field": "environment",
        "prompt": "What environment should contain the agents?",
        "explanation": "A simple 2D grid or a well-mixed environment is best for this MVP.",
    },
    {
        "field": "initial_conditions",
        "prompt": "What is the initial number of each agent type?",
        "explanation": "Provide small numbers for a browser-based model.",
    },
    {
        "field": "simulation_steps",
        "prompt": "How many simulation steps should be performed?",
        "explanation": "Choose a small number to keep the model manageable.",
    },
    {
        "field": "seed",
        "prompt": "Which random seed should the simulation use?",
        "explanation": "A seed makes the small simulation results reproducible.",
    },
    {
        "field": "duration_per_step",
        "prompt": "What biological duration does one step represent?",
        "explanation": "Describe the time represented by a single simulation step.",
    },
    {
        "field": "output_metrics",
        "prompt": "Which results would you like to measure?",
        "explanation": "Choose counts, burdens, damage, or other time-series outputs.",
    },
    {
        "field": "additional_information",
        "prompt": "Is there any additional biological information the model should consider?",
        "explanation": "Optional details can help refine the final model description.",
    },
    {
        "field": "experimental_scenarios",
        "prompt": "Which scenarios should the simulation compare?",
        "explanation": "Describe a small set of variations to compare in the results.",
    },
]

STEP_COUNT = len(QUESTIONS) + 1  # include review step
