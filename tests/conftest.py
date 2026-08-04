import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("SIM_MAX_INITIAL_AGENTS", "500")
    monkeypatch.setenv("SIM_MAX_STEPS", "500")
    monkeypatch.setenv("SIM_MAX_GRID_CELLS", "10000")
    monkeypatch.setenv("SIM_MAX_SCENARIOS", "5")
    monkeypatch.setenv("SIM_MAX_REPLICATES", "10")
    monkeypatch.setenv("SIM_MAX_WORKLOAD_SCORE", "1000000")
    yield
