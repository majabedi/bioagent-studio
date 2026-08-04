import pytest

from src.exceptions import SpecificationError
from src.schemas import ModelSpecification
from src.specification_service import validate_model_specification


def test_invalid_llm_json_does_not_start_simulation():
    invalid_json = "{not valid json}"
    with pytest.raises(SpecificationError):
        validate_model_specification(invalid_json)


def test_valid_model_specification_parsing():
    valid_json = '''{
        "title": "Test model",
        "research_question": {"text": "What happens?"},
        "biological_hypothesis": {"text": "Something occurs."},
        "biological_scale": "Cellular",
        "agent_types": [{"name": "Cell"}],
        "agent_states": [{"agent_type": "Cell", "name": "healthy"}],
        "agent_behaviors": [{"description": "Move."}],
        "interaction_rules": [{"trigger": "Near", "effect": "Change", "probability": 0.2, "agents_involved": ["Cell"]}],
        "environment": {"environment_type": "Two-dimensional grid", "grid_width": 5, "grid_height": 5},
        "initial_conditions": [{"agent_type": "Cell", "count": 3}],
        "time_specification": {"steps": 3, "duration_per_step": "1 hour"},
        "output_metrics": [{"name": "Count"}],
        "scenarios": [{"name": "baseline"}],
        "assumptions": [],
        "uncertainties": [],
        "parameter_definitions": [],
        "additional_information": "None.",
        "replicates": 1
    }'''
    spec = validate_model_specification(valid_json)
    assert isinstance(spec, ModelSpecification)
    assert spec.title == "Test model"
