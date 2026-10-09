"""Model recommendation engine providing dropdown options with suitability reasons."""

from app.schemas.device import ModelOption, ModelSuggestionsResponse

MODEL_CATALOG = [
    {
        "model_name": "qwen2.5:0.5b",
        "display_name": "Qwen 2.5 (0.5B)",
        "size_gb": 0.4,
        "min_ram_gb": 2.0,
        "min_vram_gb": 0.0,
        "tier": "Low",
        "desc": "Ultra-compact sub-billion model.",
    },
    {
        "model_name": "tinyllama:1.1b",
        "display_name": "TinyLlama (1.1B)",
        "size_gb": 0.7,
        "min_ram_gb": 4.0,
        "min_vram_gb": 0.0,
        "tier": "Low",
        "desc": "Ultra-lightweight model ideal for entry-level laptops with limited RAM.",
    },
    {
        "model_name": "llama3.2:1b",
        "display_name": "Llama 3.2 (1B)",
        "size_gb": 1.3,
        "min_ram_gb": 6.0,
        "min_vram_gb": 0.0,
        "tier": "Medium",
        "desc": "Optimal balance of speed and language quality for standard laptops.",
    },
    {
        "model_name": "gemma2:2b",
        "display_name": "Gemma 2 (2B)",
        "size_gb": 1.6,
        "min_ram_gb": 8.0,
        "min_vram_gb": 0.0,
        "tier": "Medium",
        "desc": "Google's lightweight model with strong comprehension.",
    },
    {
        "model_name": "phi3:mini",
        "display_name": "Phi-3 Mini (3.8B)",
        "size_gb": 2.3,
        "min_ram_gb": 8.0,
        "min_vram_gb": 2.0,
        "tier": "Medium",
        "desc": "Microsoft's high-reasoning model for mid-range hardware.",
    },
    {
        "model_name": "llama3.2:3b",
        "display_name": "Llama 3.2 (3B)",
        "size_gb": 2.0,
        "min_ram_gb": 12.0,
        "min_vram_gb": 3.0,
        "tier": "High",
        "desc": "High-capacity model for laptops with 12GB+ RAM or dedicated GPU.",
    },
    {
        "model_name": "mistral:7b",
        "display_name": "Mistral (7B)",
        "size_gb": 4.1,
        "min_ram_gb": 16.0,
        "min_vram_gb": 4.0,
        "tier": "High",
        "desc": "Pro-tier 7B parameter model requiring 16GB+ system RAM or dedicated VRAM.",
    },
]


def recommend_models_for_hardware(
    ram_gb: float,
    vram_gb: float = 0.0,
    gpu_name: str | None = None,
) -> ModelSuggestionsResponse:
    """Analyze hardware specs and return list of model options with reasons for applicability."""
    options: list[ModelOption] = []
    top_recommended = "llama3.2:1b"

    # Determine top tier recommendation
    if ram_gb >= 15.0 or (vram_gb >= 4.0):
        top_recommended = "llama3.2:3b"
    elif ram_gb >= 7.5:
        top_recommended = "llama3.2:1b"
    else:
        top_recommended = "qwen2.5:0.5b"

    for entry in MODEL_CATALOG:
        m_name = entry["model_name"]
        min_ram = entry["min_ram_gb"]
        min_vram = entry["min_vram_gb"]
        size_gb = entry["size_gb"]
        tier = entry["tier"]

        is_recommended = False
        reasons = []

        # Check memory fit
        if ram_gb < min_ram and vram_gb < min_vram:
            is_recommended = False
            reasons.append(
                f"Requires at least {min_ram}GB RAM (device has {ram_gb}GB). May cause slowdowns."
            )
        elif vram_gb >= min_vram and min_vram > 0:
            is_recommended = True
            reasons.append(f"Fits in dedicated VRAM ({vram_gb}GB VRAM >= {min_vram}GB required).")
        elif ram_gb >= min_ram:
            is_recommended = True
            reasons.append(
                f"Fits in system RAM ({ram_gb}GB RAM >= {min_ram}GB required). CPU mode ready."
            )

        if m_name == top_recommended:
            is_recommended = True
            reasons.insert(
                0, f"★ Optimal match for your hardware ({ram_gb}GB RAM, {gpu_name or 'CPU'})."
            )

        reason_str = " ".join(reasons) if reasons else entry["desc"]

        options.append(
            ModelOption(
                model_name=m_name,
                display_name=entry["display_name"],
                size_gb=size_gb,
                min_ram_gb=min_ram,
                min_vram_gb=min_vram,
                tier=tier,
                is_recommended=is_recommended,
                reason=reason_str,
            )
        )

    summary = (
        f"Device Specs: {ram_gb}GB RAM, {cpu_cores_desc(ram_gb)}, "
        f"GPU: {gpu_name or 'Integrated'} ({vram_gb}GB VRAM)"
    )

    return ModelSuggestionsResponse(
        recommended_model=top_recommended,
        device_summary=summary,
        models=options,
    )


def cpu_cores_desc(ram: float) -> str:
    return "Standard System" if ram < 8 else "High Performance System"
