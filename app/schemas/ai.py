"""Pydantic schemas for Local AI generation and document ingestion."""

from pydantic import BaseModel, Field


class ExtractedFileContent(BaseModel):
    """Schema for extracted content from an uploaded document."""

    filename: str = Field(description="Original uploaded filename")
    file_type: str = Field(description="File category: pdf, word, excel, csv, image, text")
    content_type: str = Field(description="MIME type")
    character_count: int = Field(description="Total extracted character length")
    extracted_text: str = Field(description="Extracted clean text content")
    base64_data: str | None = Field(default=None, description="Base64 encoded string if image file")


class AIGenerateRequest(BaseModel):
    """Payload for text prompt AI generation."""

    prompt: str = Field(min_length=1, description="Prompt text / question for the AI")
    onboarding_id: int | None = Field(
        default=None, description="Onboarding account ID to retrieve active model selection"
    )
    model_override: str | None = Field(
        default=None, description="Optional override for model selection"
    )
    system_prompt: str | None = Field(
        default=None, description="Optional system instruction for the AI model"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=2048, ge=1, le=8192, description="Maximum tokens to generate")
    text_context: str | None = Field(default=None, description="Additional context or notes text")


class AIGenerateResponse(BaseModel):
    """Schema returned by Local AI endpoints."""

    model_used: str = Field(description="Model tag used for generation, e.g. llama3.2:1b")
    response_text: str = Field(description="AI generated response string")
    prompt: str = Field(description="Original user prompt")
    attached_files_count: int = Field(description="Total attached files parsed and ingested")
    ingested_files: list[ExtractedFileContent] = Field(
        default_factory=list, description="Extracted file summaries"
    )
    is_ollama_online: bool = Field(description="Whether local Ollama service was reachable")
    execution_time_seconds: float = Field(description="Total processing time in seconds")
