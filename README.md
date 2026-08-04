# Biological ABM Assistant

A minimal Python Streamlit application for guiding biological researchers through the design, validation, and execution of small agent-based models.

## Product overview

This MVP helps researchers:
- Answer one question at a time using a wizard-style interface.
- Capture research questions, hypotheses, agents, behaviors, interactions, environment, and outputs.
- Validate a structured model specification with Pydantic.
- Use an OpenAI-compatible LLM to improve and structure the model description.
- Execute a controlled, predefined simulation engine.
- View time-series and spatial results.
- Inspect generated Python code without executing it automatically.

## MVP limitations

This application is intended for prototyping and exploration only. It:
- Supports only small simulations.
- Focuses on two-dimensional grid and well-mixed models.
- Supports a limited set of agent behaviors.
- Does not process uploaded files.
- Does not search literature or validate parameters against publications.
- Does not execute arbitrary generated code.
- Is not a replacement for experimental validation or clinical decision-making.

## Installation

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Edit `.env` and set `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL`.

## Running the app

```bash
streamlit run app.py
```

## Running tests

```bash
pytest
```

## Deployment guide

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions on deploying the Streamlit app locally or on a host.

## Example biological use case

Investigate how immune cells affect the clearance of virus-infected epithelial cells in a small tissue patch. The wizard collects the research question, hypothesis, agent types, interaction rules, and outputs for this model.

## Security and design

- LLM-generated code is displayed as an artifact only.
- The application validates the model specification with Pydantic before simulation.
- Generated code is never automatically executed via `exec`, `eval`, `subprocess`, or equivalent calls.
- Simulation-size limits prevent oversized browser-based execution.

## Simulation-size limits

The app uses environment variables to enforce limits such as:
- `SIM_MAX_INITIAL_AGENTS`
- `SIM_MAX_STEPS`
- `SIM_MAX_GRID_CELLS`
- `SIM_MAX_SCENARIOS`
- `SIM_MAX_REPLICATES`
- `SIM_MAX_WORKLOAD_SCORE`

Oversized simulations are blocked with a clear message.

## Future development ideas

Potential future extensions include:
- Scientific paper and experimental data upload
- Retrieval-augmented generation
- Parameter extraction from literature
- Three-dimensional simulations
- More advanced agent behaviors
- Support for Mesa, PhysiCell, or CompuCell3D
- Calibration and sensitivity analysis
- User accounts and project storage
- Cloud or cluster execution
