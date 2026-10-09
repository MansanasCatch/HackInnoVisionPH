"""Sanitization, syntax repair, and Pydantic validation for LLM-generated JSON."""

import json
import re

from app.core.logging import get_logger
from app.schemas.ai import StudyMaterialsResponse

logger = get_logger(__name__)


def _extract_outermost_json(text: str) -> str | None:
    """Extract outermost JSON substring from raw text."""
    # Strip markdown code blocks if present
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()

    # Search for first opening brace and last closing brace
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start : end + 1].strip()

    return None


def _repair_common_json_syntax(json_str: str) -> str:
    """Fix common local LLM syntax defects such as trailing commas."""
    # Remove trailing commas before closing braces/brackets
    # e.g. [1, 2,] -> [1, 2] or {"a": 1,} -> {"a": 1}
    fixed = re.sub(r",\s*(\}|\])", r"\1", json_str)
    return fixed


def clean_and_parse_study_json(raw_text: str) -> StudyMaterialsResponse | None:
    """Clean, repair, and parse raw LLM output into StudyMaterialsResponse."""
    if not raw_text or not raw_text.strip():
        return None

    candidate = _extract_outermost_json(raw_text)
    if not candidate:
        return None

    candidate = _repair_common_json_syntax(candidate)

    try:
        data = json.loads(candidate)
        if isinstance(data, dict):
            return StudyMaterialsResponse.model_validate(data)
    except Exception as first_err:
        logger.debug("Initial JSON parsing failed: %s; attempting secondary repairs", first_err)

    # Secondary attempt: balance brackets if LLM output was truncated
    try:
        open_braces = candidate.count("{") - candidate.count("}")
        open_brackets = candidate.count("[") - candidate.count("]")

        repaired = candidate
        if open_brackets > 0:
            repaired += "]" * open_brackets
        if open_braces > 0:
            repaired += "}" * open_braces

        repaired = _repair_common_json_syntax(repaired)
        data = json.loads(repaired)
        if isinstance(data, dict):
            return StudyMaterialsResponse.model_validate(data)
    except Exception as second_err:
        logger.warning("Could not parse study materials JSON from LLM: %s", second_err)

    return None
