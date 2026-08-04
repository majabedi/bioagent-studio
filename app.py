from __future__ import annotations

import json
import logging
from typing import Dict, List

import streamlit as st

from src.config import load_config
from src.exceptions import (
    ConfigError,
    LLMError,
    SimulationError,
    SimulationSizeError,
    SpecificationError,
)
from src.code_generator import generate_python_code
from src.prompts import build_model_prompt
from src.result_analysis import build_interpretation_prompt, summarize_results
from src.simulation_engine import ControlledSimulator
from src.size_validator import assert_simulation_size, validate_simulation_size
from src.specification_service import request_structured_specification, validate_model_specification
from src.state import DEFAULT_ANSWERS, QUESTIONS, STEP_COUNT
from src.visualizations import plot_spatial_state, plot_time_series

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def initialize_state() -> None:
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "responses" not in st.session_state:
        st.session_state.responses = DEFAULT_ANSWERS.copy()
    if "model_spec" not in st.session_state:
        st.session_state.model_spec = None
    if "generated_code" not in st.session_state:
        st.session_state.generated_code = ""
    if "simulation_result" not in st.session_state:
        st.session_state.simulation_result = None
    if "status_message" not in st.session_state:
        st.session_state.status_message = ""
    if "error_message" not in st.session_state:
        st.session_state.error_message = ""


def render_wizard_question(question: Dict[str, str], step_index: int) -> None:
    field = question["field"]
    st.header(f"Step {step_index + 1} of {STEP_COUNT}")
    st.subheader(question["prompt"])
    st.write(question["explanation"])

    if field == "biological_scale":
        st.session_state.responses[field] = st.selectbox(
            "Select biological scale",
            ["Intracellular", "Cellular", "Tissue", "Organism", "Population", "Multiscale"],
            index=["Intracellular", "Cellular", "Tissue", "Organism", "Population", "Multiscale"].index(
                st.session_state.responses.get(field, "Cellular")
            ),
        )
    elif field == "simulation_steps":
        st.session_state.responses[field] = st.number_input(
            "Simulation steps",
            min_value=1,
            max_value=500,
            value=int(st.session_state.responses.get(field, "100")),
            step=1,
        )
    elif field == "seed":
        st.session_state.responses[field] = st.number_input(
            "Random seed",
            min_value=0,
            max_value=999999,
            value=int(st.session_state.responses.get(field, "42")),
            step=1,
        )
    elif field == "duration_per_step":
        st.session_state.responses[field] = st.text_input(
            "Duration per step",
            value=st.session_state.responses.get(field, DEFAULT_ANSWERS[field]),
        )
    else:
        st.session_state.responses[field] = st.text_area(
            "Answer",
            value=st.session_state.responses.get(field, DEFAULT_ANSWERS[field]),
            height=150,
        )

    if field == "initial_conditions":
        st.warning(
            "The MVP supports only small simulations. Keep initial counts low for browser-based execution."
        )


def render_review_page() -> None:
    st.header("Review your biological model")
    st.write("Review all answers before generating the structured model and simulation.")
    for question in QUESTIONS:
        field = question["field"]
        st.markdown(f"**{question['prompt']}**")
        st.write(st.session_state.responses.get(field, ""))
        st.write("---")

    if st.button("Edit previous answers"):
        st.session_state.step = 0
    if st.button("Reset project"):
        for key in ["step", "responses", "model_spec", "generated_code", "simulation_result", "status_message", "error_message"]:
            if key in st.session_state:
                del st.session_state[key]
        initialize_state()
        st.experimental_rerun()

    if st.button("Generate model specification"):
        st.session_state.error_message = ""
        st.session_state.status_message = "Generating structured model from the LLM..."
        try:
            model_spec = request_structured_specification(st.session_state.responses)
            validation = validate_simulation_size(model_spec)
            if not validation.valid:
                raise SimulationSizeError(" ".join(validation.messages))
            st.session_state.model_spec = model_spec
            st.session_state.generated_code = generate_python_code(model_spec)
            st.session_state.status_message = "Model specification created successfully. Review the generated code and run the simulation."
        except (ConfigError, LLMError, SpecificationError, SimulationSizeError) as exc:
            st.session_state.error_message = str(exc)
            st.session_state.status_message = ""
        except Exception as exc:
            st.session_state.error_message = "An unexpected error occurred while generating the model."
            logger.exception(exc)
            st.session_state.status_message = ""

    if st.session_state.error_message:
        st.error(st.session_state.error_message)

    if st.session_state.model_spec:
        st.success(st.session_state.status_message or "Model specification is ready.")
        st.subheader("Generated simulation code")
        st.code(st.session_state.generated_code, language="python")
        st.download_button(
            label="Download generated model code",
            data=st.session_state.generated_code,
            file_name="generated_model.py",
            mime="text/x-python",
        )

        if st.button("Run controlled simulation"):
            try:
                assert_simulation_size(st.session_state.model_spec)
                simulator = ControlledSimulator(
                    st.session_state.model_spec,
                    seed=int(st.session_state.responses.get("seed", 42)),
                )
                simulation_result = simulator.run()
                st.session_state.simulation_result = simulation_result
                st.session_state.status_message = "Simulation completed successfully."
            except (SimulationError, SimulationSizeError) as exc:
                st.session_state.error_message = str(exc)
            except Exception as exc:
                st.session_state.error_message = "An unexpected error occurred during simulation execution."
                logger.exception(exc)

    if st.session_state.simulation_result:
        display_simulation_results(
            st.session_state.model_spec, st.session_state.simulation_result
        )


def display_simulation_results(spec, result) -> None:
    st.header("Simulation results")
    st.subheader("Biological summary")
    st.write("**Research question:**", spec.research_question.text)
    st.write("**Hypothesis:**", spec.biological_hypothesis.text)
    if spec.assumptions:
        st.write("**Assumptions:**")
        for assumption in spec.assumptions:
            st.write(f"- {assumption.text}")
    if spec.uncertainties:
        st.write("**Uncertainties:**")
        for uncertainty in spec.uncertainties:
            st.write(f"- {uncertainty.text}")
    st.write("**Scenarios run:**")
    for scenario in spec.scenarios:
        st.write(f"- {scenario.name}: {scenario.description or 'No description.'}")

    st.subheader("Time-series results")
    st.pyplot(plot_time_series(result.time_series))

    st.subheader("Final spatial distribution")
    st.pyplot(plot_spatial_state(result.final_agents, spec.environment.grid_width, spec.environment.grid_height))

    summary = summarize_results(spec, result)
    st.subheader("Final-state results")
    st.write(summary)

    st.subheader("Technical diagnostics")
    st.write(result.diagnostics)
    st.write("**Unsupported rules:**")
    if result.unsupported_rules:
        for item in result.unsupported_rules:
            st.write(f"- {item}")
    else:
        st.write("None detected.")

    st.subheader("Interpretation")
    try:
        from src.llm_client import LLMClient

        interpretation_prompt = build_interpretation_prompt(spec, result)
        interpreter = LLMClient()
        interpretation = interpreter.request_interpretation(interpretation_prompt)
        st.write(interpretation)
    except Exception:
        st.write(
            "Automatic interpretation is unavailable. Simulation results are model-dependent and not experimental proof."
        )


def main() -> None:
    st.set_page_config(
        page_title="Biological ABM Assistant",
        page_icon="🧬",
        layout="wide",
    )
    initialize_state()
    st.title("Biological ABM Assistant")
    st.write(
        "A step-by-step wizard for designing and running small biological agent-based simulations."
    )
    st.info("File upload will be available in a future version.")

    if st.session_state.step < len(QUESTIONS):
        render_wizard_question(QUESTIONS[st.session_state.step], st.session_state.step)
    else:
        render_review_page()

    cols = st.columns([1, 1, 1])
    with cols[0]:
        if st.button("Back"):
            st.session_state.error_message = ""
            st.session_state.status_message = ""
            st.session_state.step = max(0, st.session_state.step - 1)
    with cols[1]:
        if st.button("Next"):
            if st.session_state.step < len(QUESTIONS):
                field = QUESTIONS[st.session_state.step]["field"]
                answer = st.session_state.responses.get(field, "")
                if not answer:
                    st.error("Please answer the question before continuing.")
                else:
                    st.session_state.step += 1
    with cols[2]:
        if st.button("Go to review"):
            st.session_state.step = len(QUESTIONS)

    if st.session_state.status_message:
        st.success(st.session_state.status_message)


if __name__ == "__main__":
    try:
        load_config()
        main()
    except ConfigError as exc:
        st.title("Configuration required")
        st.error(str(exc))
    except Exception as exc:
        logging.exception(exc)
        st.title("Error")
        st.error("Unable to start the application. Check the logs for details.")
