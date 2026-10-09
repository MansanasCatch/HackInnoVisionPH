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
    StudyMaterialsResponse,
)
from app.services.file_parser import parse_uploaded_file
from app.services.json_repair_service import clean_and_parse_study_json
from app.services.model_registry import get_model_profile
from app.services.ollama_service import OLLAMA_BASE_URL, is_ollama_reachable
from app.services.study_reviewer_service import (
    build_offline_fallback_study_materials,
    build_study_prompts,
    detect_prompt_intent,
    infer_topic_from_documents,
    synthesize_dynamic_exam_prompt,
)
from app.services.token_manager import (
    calculate_safe_token_budget,
    check_capacity_warnings,
    estimate_tokens,
)

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
        """Generate response text and structured study materials using the active model."""
        start_time = time.monotonic()

        # 1. Resolve target model and profile
        target_model = self.get_active_model_for_account(
            onboarding_id=request.onboarding_id, model_override=request.model_override
        )
        model_profile = get_model_profile(target_model)

        # 2. Process and extract uploaded file contents (including image OCR)
        ingested_files: list[ExtractedFileContent] = []
        if uploaded_files:
            for fname, content_bytes, content_type in uploaded_files:
                parsed = parse_uploaded_file(fname, content_bytes, content_type)
                ingested_files.append(parsed)

        # 3. Detect intent and build grounded educational prompt dynamically
        dynamic_prompt = synthesize_dynamic_exam_prompt(
            user_prompt=request.prompt,
            documents=ingested_files,
            topic=request.topic,
        )
        resolved_topic = infer_topic_from_documents(
            request.topic, ingested_files, fallback_title=request.prompt
        )

        intent = detect_prompt_intent(request.prompt)
        sys_prompt, user_prompt = build_study_prompts(
            prompt=dynamic_prompt,
            intent=intent,
            documents=ingested_files,
            topic=resolved_topic,
            notes_context=request.text_context,
            custom_system_prompt=request.system_prompt,
        )

        # 4. Token estimation, capacity checks, and dynamic budget allocation
        input_tokens = estimate_tokens(f"{sys_prompt}\n{user_prompt}")
        warnings: list[str] = check_capacity_warnings(model_profile, input_tokens)

        # Dynamic max token budget calculation
        requested_tokens = request.max_tokens if request.max_tokens != 2048 else None
        dynamic_max_tokens = calculate_safe_token_budget(
            model=model_profile,
            input_tokens=input_tokens,
            requested_max_tokens=requested_tokens,
        )

        # Dynamic temperature optimization (factual educational defaults)
        eff_temperature = (
            model_profile.default_temp
            if request.temperature == 0.7
            else max(0.0, min(1.5, request.temperature))
        )

        # 5. Execute generation via Ollama (or offline fallback)
        ollama_online = is_ollama_reachable()
        response_text = ""
        study_materials: StudyMaterialsResponse | None = None

        images_payload: list[str] = [
            f.base64_data for f in ingested_files if f.file_type == "image" and f.base64_data
        ]

        if ollama_online:
            raw_output = self._call_ollama_generate(
                model=target_model,
                prompt=user_prompt,
                system_prompt=sys_prompt,
                temperature=eff_temperature,
                max_tokens=dynamic_max_tokens,
                images=images_payload,
                format_json=True,
            )
            response_text = raw_output

            # Attempt JSON parsing and repair
            parsed_materials = clean_and_parse_study_json(raw_output)
            if parsed_materials is not None:
                study_materials = parsed_materials
            else:
                # LLM output could not be parsed (e.g. 404 model not pulled or bad output)
                logger.warning(
                    "Model '%s' output could not be parsed into study materials. "
                    "Using deterministic fallback.",
                    target_model,
                )
                study_materials = build_offline_fallback_study_materials(
                    topic=resolved_topic,
                    intent=intent,
                    documents=ingested_files,
                    warning_msg=(
                        f"Model '{target_model}' output unparseable or error: "
                        f"{raw_output[:60]}"
                    ),
                    notes_context=request.text_context,
                )
                warnings.append(
                    f"Notice: Model '{target_model}' did not return valid JSON. "
                    "Fallback study materials generated."
                )
        else:
            response_text = self._build_offline_fallback_response(
                model=target_model,
                prompt=dynamic_prompt,
                ingested_files=ingested_files,
            )
            study_materials = build_offline_fallback_study_materials(
                topic=resolved_topic,
                intent=intent,
                documents=ingested_files,
                warning_msg="Local Ollama server offline",
                notes_context=request.text_context,
            )
            warnings.append(
                "Local Ollama server is offline. "
                "Deterministic study reviewer generated from your material."
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
            study_materials=study_materials,
            warnings=warnings,
        )

    def _call_ollama_generate(
        self,
        model: str,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.25,
        max_tokens: int = 4096,
        images: list[str] | None = None,
        format_json: bool = True,
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
            if format_json:
                payload["format"] = "json"
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
