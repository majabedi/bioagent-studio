from __future__ import annotations

from typing import Dict, List


def build_model_prompt(responses: Dict[str, str]) -> str:
    prompt_lines: List[str] = [
        "You are an assistant helping a biological researcher design a small agent-based model.",
        "Process the following research inputs, restate the model goal, and produce a structured JSON model specification.",
        "Always set source labels: User supplied, Example value, Assumption, Literature value, or Value requiring calibration.",
        "Do not invent scientific references.",
        "Do not execute generated code.",
        "The JSON output must match the provided schema and be valid.",
        "If any required information is missing, explicitly add a clearly labeled assumption.",
        "Use explicit biological units whenever possible.",
    ]
    for key, value in responses.items():
        text_value = str(value).strip() if value is not None else ""
        prompt_lines.append(f"{key.replace('_', ' ').capitalize()}: {text_value}")
    prompt_lines.append("""
Produce a JSON object with the following top-level fields:
- title
- research_question
- biological_hypothesis
- biological_scale
- agent_types
- agent_states
- agent_behaviors
- interaction_rules
- environment
- initial_conditions
- time_specification
- output_metrics
- scenarios
- assumptions
- uncertainties
- parameter_definitions
- additional_information
- replicates
""")
    return "\n\n".join(prompt_lines)


def build_repair_prompt(raw_response: str) -> str:
    return (
        "The previous LLM response failed JSON validation. "
        "Please return only valid JSON that matches the requested schema. "
        "Do not add narrative text outside the JSON object. "
        f"Previous response:\n{raw_response}"
    )
