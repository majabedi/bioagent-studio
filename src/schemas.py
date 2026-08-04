from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, PositiveInt, confloat, validator


class BiologicalScale(str, Enum):
    intracellular = "Intracellular"
    cellular = "Cellular"
    tissue = "Tissue"
    organism = "Organism"
    population = "Population"
    multiscale = "Multiscale"


class EnvironmentType(str, Enum):
    grid = "Two-dimensional grid"
    well_mixed = "Well-mixed environment"


class ParameterSource(str, Enum):
    user_supplied = "User supplied"
    example_value = "Example value"
    assumption = "Assumption"
    literature_value = "Literature value"
    value_requiring_calibration = "Value requiring calibration"


class ResearchQuestion(BaseModel):
    text: str = Field(..., description="The primary biological research question.")


class BiologicalHypothesis(BaseModel):
    text: str = Field(..., description="The hypothesis the simulation should test.")


class AgentType(BaseModel):
    name: str = Field(..., description="The name of the agent type.")
    role: Optional[str] = Field(None, description="The biological role of this agent type.")
    attributes: Optional[Dict[str, str]] = Field(None, description="Optional attributes for the agent type.")


class AgentState(BaseModel):
    agent_type: str = Field(..., description="Which agent type can take this state.")
    name: str = Field(..., description="State name.")
    description: Optional[str] = Field(None, description="Description of the state.")


class AgentBehavior(BaseModel):
    description: str = Field(..., description="The behavior description for agents.")
    behavior_type: Optional[str] = Field(None, description="A short behavior category.")


class InteractionRule(BaseModel):
    trigger: str = Field(..., description="The condition that triggers the interaction.")
    effect: str = Field(..., description="The biological effect of the interaction.")
    probability: Optional[confloat(ge=0.0, le=1.0)] = Field(
        None,
        description="Probability of the interaction occurring during each time step.",
    )
    agents_involved: Optional[List[str]] = Field(
        None, description="Agent types involved in the interaction."
    )
    notes: Optional[str] = Field(None, description="Additional notes or assumptions.")


class EnvironmentSpecification(BaseModel):
    environment_type: EnvironmentType = Field(
        EnvironmentType.grid, description="The environment type for the simulation."
    )
    grid_width: Optional[PositiveInt] = Field(
        20, description="Grid width for a two-dimensional tissue layer."
    )
    grid_height: Optional[PositiveInt] = Field(
        20, description="Grid height for a two-dimensional tissue layer."
    )
    description: Optional[str] = Field(None, description="High-level environment description.")

    @validator("grid_width", "grid_height", pre=True, always=True)
    def validate_grid_dimensions(cls, value, values, field):
        if values.get("environment_type") == EnvironmentType.grid:
            if value is None:
                raise ValueError("Grid dimensions are required for grid environments.")
        return value


class InitialCondition(BaseModel):
    agent_type: str = Field(..., description="Agent type name for the initial condition.")
    count: PositiveInt = Field(..., description="Initial number of agents of this type.")
    estimated_max_count: Optional[PositiveInt] = Field(
        None,
        description="Estimated maximum population for the agent type during the simulation.",
    )


class TimeSpecification(BaseModel):
    steps: PositiveInt = Field(..., description="Number of simulation time steps.")
    duration_per_step: str = Field(
        ...,
        description="Biological duration represented by one simulation step, including units.",
    )


class OutputMetric(BaseModel):
    name: str = Field(..., description="Name of the output metric to collect.")
    description: Optional[str] = Field(None, description="Description of the output metric.")


class ExperimentalScenario(BaseModel):
    name: str = Field(..., description="Scenario name.")
    description: Optional[str] = Field(None, description="Scenario description.")
    parameter_overrides: Optional[Dict[str, str]] = Field(
        None,
        description="Small parameter changes for this scenario.")


class Assumption(BaseModel):
    text: str = Field(..., description="Assumed model detail or parameter.")
    source: ParameterSource = Field(
        ParameterSource.assumption,
        description="Source label for the assumption.",
    )


class Uncertainty(BaseModel):
    text: str = Field(..., description="A recognized uncertainty in the model.")
    source: Optional[ParameterSource] = Field(
        ParameterSource.value_requiring_calibration,
        description="Source label for the uncertainty.",
    )


class ParameterDefinition(BaseModel):
    name: str = Field(..., description="Parameter name.")
    value: str = Field(..., description="Parameter value.")
    source: ParameterSource = Field(..., description="Source label for the parameter.")


class ModelSpecification(BaseModel):
    title: str = Field(..., description="Title of the model specification.")
    research_question: ResearchQuestion
    biological_hypothesis: BiologicalHypothesis
    biological_scale: BiologicalScale
    agent_types: List[AgentType]
    agent_states: List[AgentState]
    agent_behaviors: List[AgentBehavior]
    interaction_rules: List[InteractionRule]
    environment: EnvironmentSpecification
    initial_conditions: List[InitialCondition]
    time_specification: TimeSpecification
    output_metrics: List[OutputMetric]
    scenarios: List[ExperimentalScenario]
    assumptions: Optional[List[Assumption]] = Field(
        default_factory=list, description="Assumptions added by the model.")
    uncertainties: Optional[List[Uncertainty]] = Field(
        default_factory=list, description="Model uncertainties and unknowns.")
    additional_information: Optional[str] = Field(
        None, description="Additional researcher-provided biological information.")
    parameter_definitions: Optional[List[ParameterDefinition]] = Field(
        default_factory=list,
        description="Parameters and their sources for the simulation.")
    replicates: PositiveInt = Field(1, description="Number of replicates per scenario.")

    @validator("scenarios")
    def non_empty_scenarios(cls, value):
        if not value:
            raise ValueError("At least one experimental scenario is required.")
        return value

    @validator("initial_conditions")
    def validate_initial_conditions(cls, value):
        if not value:
            raise ValueError("At least one initial condition is required.")
        return value
