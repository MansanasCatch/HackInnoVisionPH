"""Unit tests for token estimation and dynamic budgeting."""

from app.services.model_registry import ModelProfile
from app.services.token_manager import (
    calculate_safe_token_budget,
    check_capacity_warnings,
    estimate_tokens,
)


def test_estimate_tokens() -> None:
    text = "Hello world! This is a test sentence for token calculation."
    tokens = estimate_tokens(text)
    assert tokens > 0
    assert 10 <= tokens <= 25


def test_calculate_safe_token_budget() -> None:
    profile = ModelProfile(
        model_name="test-model",
        context_tokens=8192,
        max_output_tokens=4096,
        default_temp=0.3,
    )

    # When input is 2000 tokens, safe budget should be min(4096, 8192 - 2000 - 500) = 4096
    budget = calculate_safe_token_budget(profile, input_tokens=2000, requested_max_tokens=None)
    assert budget == 4096

    # When input is 6000 tokens, safe budget is clamped:
    # 8192 - 6000 - 500 = 1692
    tight_budget = calculate_safe_token_budget(
        profile, input_tokens=6000, requested_max_tokens=None
    )
    assert tight_budget == 1692

    # When user requests an explicit lower budget, respect it
    user_budget = calculate_safe_token_budget(profile, input_tokens=2000, requested_max_tokens=1000)
    assert user_budget == 1000


def test_check_capacity_warnings() -> None:
    profile = ModelProfile(
        model_name="test-model",
        context_tokens=8192,
        max_output_tokens=4096,
        default_temp=0.3,
    )

    # Input <= 75% -> no warnings
    warnings_low = check_capacity_warnings(profile, input_tokens=4000)
    assert len(warnings_low) == 0

    # Input > 75% (8192 * 0.75 = 6144) -> warning emitted
    warnings_high = check_capacity_warnings(profile, input_tokens=6500)
    assert len(warnings_high) == 1
    assert "context" in warnings_high[0].lower()
