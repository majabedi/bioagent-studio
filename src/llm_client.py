from __future__ import annotations

import json
import logging
import time
from typing import Dict, Optional

import openai

from src.config import load_config
from src.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        self.config = load_config()
        self.model = self.config.llm_model
        self.timeout = self.config.llm_timeout_seconds
        self.temperature = self.config.llm_temperature
        self.max_retries = self.config.llm_max_retries
        openai.api_key = self.config.llm_api_key
        openai.api_base = self.config.llm_base_url

    def _send_request(self, messages: list, timeout: Optional[int] = None) -> str:
        attempt = 0
        while attempt <= self.max_retries:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    timeout=timeout or self.timeout,
                )
                choice = response.choices[0]
                content = getattr(getattr(choice, "message", None), "content", None)
                if content is None:
                    content = choice["message"]["content"]
                return content
            except Exception as exc:
                attempt += 1
                logger.warning("LLM request failed on attempt %s: %s", attempt, exc)
                if attempt > self.max_retries:
                    raise LLMError(
                        "Unable to reach the language model. Please check your configuration and try again."
                    ) from exc
                time.sleep(1)
        raise LLMError("LLM request failed after retries.")

    def request_model_specification(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a scientific assistant that creates structured biological agent-based model specifications. "
                    "Return valid JSON only unless otherwise requested."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        return self._send_request(messages)

    def request_interpretation(self, summary: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistant that interprets simulation outputs carefully. "
                    "Provide a cautious biological interpretation without making experimental claims."
                ),
            },
            {"role": "user", "content": summary},
        ]
        return self._send_request(messages)
