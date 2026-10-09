"""Endpoints for Local AI generation and document ingestion (lessons, notes, files)."""

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.api.deps import LocalAIServiceDep
from app.api.uploads import read_uploads
from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
)

router = APIRouter(prefix="/ai", tags=["Local AI & File Ingestion"])


@router.post(
    "/generate",
    response_model=AIGenerateResponse,
    summary="Generate response with Local AI",
    description="Query Local AI using the active model set in Device Specs for the account.",
)
def generate_text_with_local_ai(
    request: AIGenerateRequest,
    service: LocalAIServiceDep,
) -> AIGenerateResponse:
    """Generate response text with Local AI."""
    return service.generate(request=request)


@router.post(
    "/generate-with-files",
    response_model=AIGenerateResponse,
    summary="Generate Local AI response with file ingestion",
    description="Upload files (Image, PDF, Excel, Word, Text) to ingest into Local AI prompt.",
)
async def generate_with_files(
    service: LocalAIServiceDep,
    prompt: Annotated[
        str,
        Form(
            description=(
                "Prompt text or question for the AI. If left empty, dynamically auto-generated "
                "from the topic and uploaded documents."
            )
        ),
    ] = "",
    topic: Annotated[
        str | None,
        Form(
            description="Topic from user UI (e.g. 'Cell division'). Auto-inferred if blank."
        ),
    ] = None,
    onboarding_id: Annotated[int | None, Form(description="Onboarding account ID")] = None,
    model_override: Annotated[str | None, Form(description="Optional model tag override")] = None,
    system_prompt: Annotated[str | None, Form(description="Optional system prompt")] = None,
    text_context: Annotated[
        str | None, Form(description="Free-text notes the learner typed or pasted")
    ] = None,
    temperature: Annotated[float, Form(description="Temperature sampling")] = 0.7,
    max_tokens: Annotated[int, Form(description="Max generation tokens")] = 2048,
    files: Annotated[
        UploadFile | list[UploadFile] | None,
        File(description="Attached document or image file to ingest"),
    ] = None,
) -> AIGenerateResponse:
    """Generate Local AI response grounded by attached file contents."""
    uploaded_files = await read_uploads(files)

    req = AIGenerateRequest(
        prompt=prompt,
        topic=topic,
        onboarding_id=onboarding_id,
        model_override=model_override,
        system_prompt=system_prompt,
        text_context=text_context,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return service.generate(request=req, uploaded_files=uploaded_files)
