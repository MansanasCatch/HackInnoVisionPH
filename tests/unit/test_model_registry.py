"""Unit tests for the model capability registry."""

from app.services.model_registry import ModelProfile, get_model_profile


def test_get_model_profile_known_models() -> None:
    # Llama 3.2 3B
    profile_3b = get_model_profile("llama3.2:3b")
    assert profile_3b.context_tokens == 128000
    assert profile_3b.max_output_tokens >= 4096
    assert 0.2 <= profile_3b.default_temp <= 0.35

    # Llama 3 8B
    profile_l3 = get_model_profile("llama3:latest")
    assert profile_l3.context_tokens == 8192
    assert profile_l3.max_output_tokens == 4096

    # Qwen 2.5
    profile_qwen = get_model_profile("qwen2.5:0.5b")
    assert profile_qwen.context_tokens >= 32768
    assert profile_qwen.default_temp == 0.2


def test_get_model_profile_fallback_for_unknown() -> None:
    profile_unknown = get_model_profile("custom-finetune:latest")
    assert isinstance(profile_unknown, ModelProfile)
    assert profile_unknown.context_tokens >= 8192
    assert profile_unknown.max_output_tokens >= 2048
    assert 0.0 <= profile_unknown.default_temp <= 1.0
