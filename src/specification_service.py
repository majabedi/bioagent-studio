from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from pydantic import ValidationError

from src.exceptions import LLMError, SpecificationError
from src.prompts import build_model_prompt, build_repair_prompt
from src.schemas import ModelSpecification
from src.llm_client import LLMClient

logger = logging.getLogger(__name__)


def build_prompt_from_responses(responses: Dict[str, str]) -> str:
    return build_model_prompt(responses)


def validate_model_specification(raw_json_text: str) -> ModelSpecification:
    try:
        payload = json.loads(raw_json_text)
    except json.JSONDecodeError as exc:
        raise SpecificationError("Received invalid JSON from the language model.") from exc

    try:
        model_spec = ModelSpecification.parse_obj(payload)
    except ValidationError as exc:
        logger.debug("ModelSpecification validation failed: %s", exc)
        raise SpecificationError("The model specification did not match the expected schema.") from exc

    return model_spec


def request_structured_specification(responses: Dict[str, str]) -> ModelSpecification:
    llm = LLMClient()
    prompt = build_prompt_from_responses(responses)
    raw_response = llm.request_model_specification(prompt)

    try:
        return validate_model_specification(raw_response)
    except SpecificationError:
        repair_prompt = build_repair_prompt(raw_response)
        repaired_response = llm.request_model_specification(repair_prompt)
        try:
            return validate_model_specification(repaired_response)
        except SpecificationError as exc:
            raise SpecificationError(
                "The model specification could not be validated after repair."
            ) from exc
