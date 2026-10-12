"""Pydantic schemas for Local AI generation, document ingestion, and study materials."""

from typing import Literal

from pydantic import BaseModel, Field


class ExtractedFileContent(BaseModel):
    """Schema for extracted content from an uploaded document."""

    filename: str = Field(description="Original uploaded filename")
    file_type: str = Field(description="File category: pdf, word, excel, csv, image, text")
    content_type: str = Field(description="MIME type")
    character_count: int = Field(description="Total extracted character length")
    extracted_text: str = Field(description="Extracted clean text content")
    base64_data: str | None = Field(default=None, description="Base64 encoded string if image file")


class DocumentExtractResponse(BaseModel):
    """Schema for document extraction result."""

    success: bool = Field(default=True, description="Whether extraction succeeded")
    total_files: int = Field(description="Number of files processed")
    files: list[ExtractedFileContent] = Field(
        default_factory=list, description="Extracted content per file"
    )


class AIGenerateRequest(BaseModel):
    """Payload for text prompt AI generation."""

    prompt: str = Field(
        default="",
        description=(
            "Prompt text or question for the AI (if blank, dynamically generated from documents)"
        ),
    )
    topic: str | None = Field(
        default=None,
        description=(
            "Specific study topic (e.g. 'Cell division', 'Mechanics'). Auto-inferred if omitted."
        ),
    )
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


# ---------------------------------------------------------------------------
# Structured Educational Study Materials Schemas
# ---------------------------------------------------------------------------


class ReviewerSection(BaseModel):
    """A thematic section of the comprehensive reviewer."""

    title: str = Field(description="Section heading / subtopic")
    content: str = Field(description="Detailed conceptual explanation")
    key_points: list[str] = Field(default_factory=list, description="Essential key points")


class Reviewer(BaseModel):
    """Comprehensive study guide."""

    title: str = Field(description="Reviewer title")
    sections: list[ReviewerSection] = Field(default_factory=list)


class Summary(BaseModel):
    """High-yield synthesis of core concepts."""

    content: str = Field(description="Concise summary of the source material")


class KeyNotesItem(BaseModel):
    """Organized, quick-reference notes item."""

    topic: str = Field(description="Concept or subtopic name")
    notes: list[str] = Field(default_factory=list, description="Bulleted takeaway points")


class Flashcard(BaseModel):
    """Question-and-answer pair for active recall."""

    question: str = Field(description="Question or prompt")
    answer: str = Field(description="Accurate factual answer grounded in source documents")
    topic: str = Field(description="Associated subject topic")
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class QuizQuestion(BaseModel):
    """Assessment question with options and explanation."""

    type: Literal["multiple_choice", "true_false", "identification", "short_answer"]
    question: str = Field(description="Question text")
    options: list[str] | None = Field(
        default=None, description="Options list for multiple choice questions"
    )
    correct_answer: str = Field(description="Correct answer according to source document")
    explanation: str = Field(description="Pedagogical explanation of why the answer is correct")
    topic: str = Field(description="Subject topic")
    difficulty: Literal["easy", "medium", "hard"] = "medium"


class ExamQuestion(BaseModel):
    """In-depth examination question with points."""

    type: Literal["multiple_choice", "true_false", "identification", "short_answer", "essay"]
    question: str = Field(description="Exam question prompt")
    options: list[str] | None = Field(default=None, description="Options if multiple choice")
    correct_answer: str = Field(description="Expected answer based on source material")
    explanation: str = Field(description="Scoring criteria or explanation")
    topic: str = Field(description="Subject topic")
    difficulty: Literal["easy", "medium", "hard"] = "hard"
    points: int = Field(default=1, ge=1, description="Point value of the question")


class Exam(BaseModel):
    """Comprehensive examination."""

    title: str = Field(description="Exam title")
    questions: list[ExamQuestion] = Field(default_factory=list)
    total_questions: int = Field(default=0, ge=0)
    total_points: int = Field(default=0, ge=0)


class SourceCoverage(BaseModel):
    """Audit of topics covered vs gaps identified in source material."""

    covered_topics: list[str] = Field(default_factory=list)
    content_gaps: list[str] = Field(
        default_factory=list,
        description=(
            "Explicit gaps identified in source documents instead of inventing missing information"
        ),
    )


class StudyMaterialsResponse(BaseModel):
    """Complete structured educational study materials package."""

    intent: Literal["question", "study_reviewer"] = "study_reviewer"
    direct_answer: str | None = Field(
        default=None,
        description="Immediate factual answer if the user asked a specific ad-hoc question",
    )
    topic: str = Field(description="Selected subject or main topic")
    source_summary: str = Field(description="Overview of the uploaded documents")
    reviewer: Reviewer
    summary: Summary
    key_notes: list[KeyNotesItem] = Field(default_factory=list)
    flashcards: list[Flashcard] = Field(default_factory=list)
    quizzes: list[QuizQuestion] = Field(default_factory=list)
    exam: Exam
    source_coverage: SourceCoverage


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
    study_materials: StudyMaterialsResponse | None = Field(
        default=None,
        description="Structured educational reviewer, flashcards, quizzes, and exams",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="User warnings regarding token budgeting, OCR notices, or truncation",
    )


class RAGSearchRequest(BaseModel):
    """Request model for topic web search and RAG retrieval."""

    topic: str = Field(description="Search topic or question to research online")
    max_results: int = Field(default=5, ge=1, le=10, description="Max search results to retrieve")
    top_k_chunks: int = Field(default=6, ge=1, le=12, description="Top ranked chunks to return")


class RAGChunkItem(BaseModel):
    """Individual retrieved and scored chunk."""

    chunk_id: int
    title: str
    url: str
    content: str
    score: float


class RAGSearchResponse(BaseModel):
    """Response model containing retrieved and ranked RAG chunks."""

    success: bool = True
    query: str
    source_engine: str = "Authoritative Multi-Source Web RAG"
    search_engine: str = "Authoritative Multi-Source Web RAG"
    total_sources: int = 0
    total_chunks: int = 0
    retrieved_chunks: list[RAGChunkItem] = Field(default_factory=list)
    aggregated_context: str = ""

