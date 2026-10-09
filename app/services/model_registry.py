"""Model capability registry mapping local LLM model families to context and token limits."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProfile:
    """Capability specification for an LLM model."""

    model_name: str
    context_tokens: int
    max_output_tokens: int
    default_temp: float
    description: str = ""


# Default safe fallback profile
DEFAULT_MODEL_PROFILE = ModelProfile(
    model_name="default",
    context_tokens=8192,
    max_output_tokens=4096,
    default_temp=0.3,
    description="Standard safe configuration for local models",
)

# Known model capability catalog
_MODEL_PROFILES: dict[str, ModelProfile] = {
    # Llama 3.2 family (128k context)
    "llama3.2": ModelProfile(
        model_name="llama3.2",
        context_tokens=128000,
        max_output_tokens=8192,
        default_temp=0.25,
        description="Meta Llama 3.2 with extended 128k context window",
    ),
    "llama3.2:1b": ModelProfile(
        model_name="llama3.2:1b",
        context_tokens=128000,
        max_output_tokens=8192,
        default_temp=0.25,
        description="Llama 3.2 1B lightweight model",
    ),
    "llama3.2:3b": ModelProfile(
        model_name="llama3.2:3b",
        context_tokens=128000,
        max_output_tokens=8192,
        default_temp=0.25,
        description="Llama 3.2 3B high capability local model",
    ),
    # Llama 3 family (8k context)
    "llama3": ModelProfile(
        model_name="llama3",
        context_tokens=8192,
        max_output_tokens=4096,
        default_temp=0.3,
        description="Meta Llama 3 8B model",
    ),
    "llama3:latest": ModelProfile(
        model_name="llama3:latest",
        context_tokens=8192,
        max_output_tokens=4096,
        default_temp=0.3,
        description="Meta Llama 3 latest tag",
    ),
    # Qwen 2.5 & 3.5 family (32k - 128k context)
    "qwen2.5": ModelProfile(
        model_name="qwen2.5",
        context_tokens=32768,
        max_output_tokens=8192,
        default_temp=0.2,
        description="Alibaba Qwen 2.5 with high JSON and multilingual fidelity",
    ),
    "qwen3.5": ModelProfile(
        model_name="qwen3.5",
        context_tokens=65536,
        max_output_tokens=8192,
        default_temp=0.2,
        description="Alibaba Qwen 3.5 model",
    ),
    # Mistral 7B (32k context)
    "mistral": ModelProfile(
        model_name="mistral",
        context_tokens=32768,
        max_output_tokens=8192,
        default_temp=0.3,
        description="Mistral 7B model",
    ),
    # Phi-3 family (128k context)
    "phi3": ModelProfile(
        model_name="phi3",
        context_tokens=128000,
        max_output_tokens=4096,
        default_temp=0.25,
        description="Microsoft Phi-3 Mini with 128k context",
    ),
    # Gemma 2 family (8k context)
    "gemma2": ModelProfile(
        model_name="gemma2",
        context_tokens=8192,
        max_output_tokens=4096,
        default_temp=0.3,
        description="Google Gemma 2 model",
    ),
}


def get_model_profile(model_tag: str) -> ModelProfile:
    """Resolve capability profile for a given model tag or family."""
    clean_tag = model_tag.strip().lower()

    # Exact match check
    if clean_tag in _MODEL_PROFILES:
        return _MODEL_PROFILES[clean_tag]

    # Prefix/Family check (e.g. qwen2.5:0.5b matches qwen2.5)
    for prefix, profile in _MODEL_PROFILES.items():
        if clean_tag.startswith(prefix):
            return profile

    # Safe fallback
    return DEFAULT_MODEL_PROFILE
