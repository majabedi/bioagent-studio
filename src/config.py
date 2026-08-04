from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from src.exceptions import ConfigError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class AppConfig:
    """Application configuration loaded from environment variables."""

    def __init__(self):
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.llm_base_url = os.getenv("LLM_BASE_URL", "")
        self.llm_model = os.getenv("LLM_MODEL", "")
        self.llm_timeout_seconds = int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
        self.llm_temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        self.llm_max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))
        self.sim_max_initial_agents = int(os.getenv("SIM_MAX_INITIAL_AGENTS", "500"))
        self.sim_max_steps = int(os.getenv("SIM_MAX_STEPS", "500"))
        self.sim_max_grid_cells = int(os.getenv("SIM_MAX_GRID_CELLS", "10000"))
        self.sim_max_scenarios = int(os.getenv("SIM_MAX_SCENARIOS", "5"))
        self.sim_max_replicates = int(os.getenv("SIM_MAX_REPLICATES", "10"))
        self.sim_max_workload_score = int(os.getenv("SIM_MAX_WORKLOAD_SCORE", "1000000"))

        # Validate required fields
        if not self.llm_api_key or not self.llm_base_url or not self.llm_model:
            raise ConfigError(
                "Missing required configuration. "
                "Please set LLM_API_KEY, LLM_BASE_URL, and LLM_MODEL in your environment."
            )


def load_config() -> AppConfig:
    """Load and return application configuration."""
    try:
        return AppConfig()
    except Exception as exc:
        raise ConfigError(
            "Environment configuration is invalid. Review required LLM and simulation variables."
        ) from exc
