"""Token estimation and dynamic budget allocation service."""

import math

from app.services.model_registry import ModelProfile

# Standard character-to-token heuristic ratio for mixed English/technical text
CHARS_PER_TOKEN = 3.8

# Safety margin reserved for prompt templates, JSON syntax, and framing overhead
SAFETY_MARGIN_TOKENS = 500

# Minimum output token floor so the model never generates zero tokens
MIN_OUTPUT_TOKENS = 512


def estimate_tokens(text: str) -> int:
    """Fast estimation of token count from string content."""
    if not text:
        return 0
    # Heuristic: roughly 3.8 characters per token with word-boundary weight
    return max(1, math.ceil(len(text) / CHARS_PER_TOKEN))


def calculate_safe_token_budget(
    model: ModelProfile,
    input_tokens: int,
    requested_max_tokens: int | None = None,
) -> int:
    """Calculate the maximum safe output tokens without overflowing the model's context.

    Ensures the response budget fits within:
    context_tokens - input_tokens - SAFETY_MARGIN_TOKENS
    and does not exceed the model's physical max_output_tokens limit.
    """
    available_context = max(
        MIN_OUTPUT_TOKENS, model.context_tokens - input_tokens - SAFETY_MARGIN_TOKENS
    )
    safe_max_output = min(model.max_output_tokens, available_context)

    if requested_max_tokens is not None and requested_max_tokens > 0:
        # Cap user request by the safe physical ceiling
        return min(requested_max_tokens, safe_max_output)

    return safe_max_output


def check_capacity_warnings(model: ModelProfile, input_tokens: int) -> list[str]:
    """Emit user warnings if input document size approaches model context limits."""
    warnings: list[str] = []
    ratio = input_tokens / max(1, model.context_tokens)

    if ratio >= 0.75:
        percent = round(ratio * 100)
        warnings.append(
            f"⚠️ Input files consume ~{input_tokens} tokens ({percent}% of model "
            f"'{model.model_name}' context limit of {model.context_tokens} tokens). "
            "Output token budget was automatically clamped to prevent truncation."
        )

    return warnings
