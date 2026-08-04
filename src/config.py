from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseSettings, Field, ValidationError, root_validator

from src.exceptions import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class AppConfig(BaseSettings):
    llm_api_key: str = Field(..., env="LLM_API_KEY")
    llm_base_url: str = Field(..., env="LLM_BASE_URL")
    llm_model: str = Field(..., env="LLM_MODEL")
    llm_timeout_seconds: int = Field(60, env="LLM_TIMEOUT_SECONDS")
    llm_temperature: float = Field(0.2, env="LLM_TEMPERATURE")
    llm_max_retries: int = Field(2, env="LLM_MAX_RETRIES")
    sim_max_initial_agents: int = Field(500, env="SIM_MAX_INITIAL_AGENTS")
    sim_max_steps: int = Field(500, env="SIM_MAX_STEPS")
    sim_max_grid_cells: int = Field(10000, env="SIM_MAX_GRID_CELLS")
    sim_max_scenarios: int = Field(5, env="SIM_MAX_SCENARIOS")
    sim_max_replicates: int = Field(10, env="SIM_MAX_REPLICATES")
    sim_max_workload_score: int = Field(1000000, env="SIM_MAX_WORKLOAD_SCORE")

    @root_validator(pre=True)
    def validate_required_vars(cls, values):
        missing = []
        for key in ["llm_api_key", "llm_base_url", "llm_model"]:
            if not values.get(key) and not os.getenv(key):
                missing.append(key)
        if missing:
            raise ConfigError(
                "Missing required configuration. "
                "Please set LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL in your environment."
            )
        return values

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_config() -> AppConfig:
    try:
        return AppConfig()
    except ValidationError as exc:
        raise ConfigError(
            "Environment configuration is invalid. Review required LLM and simulation variables."
        ) from exc
