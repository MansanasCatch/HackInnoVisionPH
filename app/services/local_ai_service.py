"""Local AI Service orchestrating model retrieval and document context ingestion."""

import json
import time
import urllib.request
from typing import Any

from app.core.logging import get_logger
from app.repositories.device_repository import AbstractDeviceRepository
from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
    ExtractedFileContent,
)
from app.services.file_parser import parse_uploaded_file
from app.services.ollama_service import OLLAMA_BASE_URL, is_ollama_reachable

logger = get_logger(__name__)


class LocalAIService:
    """Local AI inference orchestrator using configured device specs active models."""

    def __init__(self, device_repository: AbstractDeviceRepository) -> None:
        self._device_repo = device_repository

    def get_active_model_for_account(
        self, onboarding_id: int | None = None, model_override: str | None = None
    ) -> str:
        """Resolve target model tag from override, device specs, or system selection."""
        if model_override:
            return model_override

        if onboarding_id is not None:
            device = self._device_repo.get_by_onboarding_id(onboarding_id)
            if device is not None:
                return device.selected_model

        return self._device_repo.get_latest_active_model()

    def generate(
        self,
        request: AIGenerateRequest,
        uploaded_files: list[tuple[str, bytes, str | None]] | None = None,
    ) -> AIGenerateResponse:
        """Generate response text using the active local model and ingested file context."""
        start_time = time.monotonic()

        # 1. Resolve target model
        target_model = self.get_active_model_for_account(
            onboarding_id=request.onboarding_id, model_override=request.model_override
        )

        # 2. Process and extract uploaded file contents
        ingested_files: list[ExtractedFileContent] = []
        if uploaded_files:
            for fname, content_bytes, content_type in uploaded_files:
                parsed = parse_uploaded_file(fname, content_bytes, content_type)
                ingested_files.append(parsed)

        # 3. Build formatted context
        full_prompt = self._build_grounded_prompt(
            prompt=request.prompt,
            text_context=request.text_context,
            ingested_files=ingested_files,
        )

        # 4. Execute AI Generation via Ollama (or fallback)
        ollama_online = is_ollama_reachable()
        response_text = ""
        images_payload: list[str] = []

        # Collect base64 images if present for multimodal models
        for file in ingested_files:
            if file.file_type == "image" and file.base64_data:
                images_payload.append(file.base64_data)

        if ollama_online:
            response_text = self._call_ollama_generate(
                model=target_model,
                prompt=full_prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                images=images_payload,
            )
        else:
            response_text = self._build_offline_fallback_response(
                model=target_model,
                prompt=request.prompt,
                ingested_files=ingested_files,
            )

        elapsed = round(time.monotonic() - start_time, 3)

        return AIGenerateResponse(
            model_used=target_model,
            response_text=response_text,
            prompt=request.prompt,
            attached_files_count=len(ingested_files),
            ingested_files=ingested_files,
            is_ollama_online=ollama_online,
            execution_time_seconds=elapsed,
        )

    def _build_grounded_prompt(
        self,
        prompt: str,
        text_context: str | None,
        ingested_files: list[ExtractedFileContent],
    ) -> str:
        """Construct prompt grounded with ingested documents and notes context."""
        parts: list[str] = []

        if ingested_files or text_context:
            parts.append("=== INGESTED STUDY MATERIALS & FILE CONTEXT ===")

            if text_context:
                parts.append(f"[Attached Notes Context]\n{text_context.strip()}\n")

            for idx, f in enumerate(ingested_files, 1):
                parts.append(
                    f"[Attached File {idx}: {f.filename} "
                    f"(Type: {f.file_type}, {f.character_count} chars)]\n"
                    f"{f.extracted_text.strip()}\n"
                )

            parts.append("================================================\n")

        parts.append(f"USER PROMPT / TASK:\n{prompt}")
        return "\n".join(parts)

    def _call_ollama_generate(
        self,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        images: list[str] | None = None,
    ) -> str:
        """Call Ollama /api/generate REST API endpoint."""
        try:
            url = f"{OLLAMA_BASE_URL}/api/generate"
            payload: dict[str, Any] = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }
            if system_prompt:
                payload["system"] = system_prompt
            if images:
                payload["images"] = images

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}, method="POST"
            )
            with urllib.request.urlopen(req, timeout=120.0) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "").strip()
        except Exception as err:
            logger.error("Error generating text with Ollama model '%s': %s", model, err)
            return (
                f"[Ollama Call Warning]: Model '{model}' failed or pulling. Error: {err}\n\n"
                f"Generated Prompt Ready for Model:\n{prompt}"
            )

    def _build_offline_fallback_response(
        self,
        model: str,
        prompt: str,
        ingested_files: list[ExtractedFileContent],
    ) -> str:
        """Generate structured response when Ollama local server is offline or unreachable."""
        files_summary = ""
        if ingested_files:
            file_names = ", ".join(f"'{f.filename}' ({f.file_type})" for f in ingested_files)
            files_summary = (
                f"\n\n📂 Ingested File Context ({len(ingested_files)} files):\n{file_names}"
            )

        return (
            f"🤖 [Local AI Engine - Model: {model}]\n"
            f"(Note: Local Ollama server at {OLLAMA_BASE_URL} is offline.\n"
            f"The system successfully ingested your prompt and documents.)\n\n"
            f'📝 User Prompt: "{prompt}"{files_summary}\n\n'
            f"💡 Ensure Ollama is started (`ollama serve`). "
            f"Active model '{model}' is set in Device Specs."
        )
