# AI Study Reviewer Generation API — Architecture & Design Specification

**Date:** 2026-10-10  
**Status:** Approved  
**Author:** AI Pair Programmer & Anastasya  
**Target Endpoint:** `POST /api/v1/ai/generate-with-files`  

---

## 1. Executive Summary

This specification defines the architecture, data contracts, and implementation for enhancing the InnoVisionPH `/api/v1/ai/generate-with-files` endpoint into an intelligent, educational **AI Study Reviewer Generation API**. 

The enhanced endpoint enables students and teachers to upload diverse study materials (PDF, Word, Excel, CSV, Text, and scanned Images/Photos via OCR), specify a topic or ask a specific question, and receive comprehensive, accurate, structured educational study materials in machine-readable JSON backed by local LLMs (via Ollama) with dynamic token budgeting, model-specific temperature optimization, and offline fallback guarantees.

---

## 2. Key Requirements & Capabilities

1. **Intelligent Grounded Prompting:**
   - Differentiates between **Ad-hoc Questions** (e.g. *"What is the formula on page 3?"*) and **Study Reviewer Generation** (e.g. *"Reviewer for Chapter 4"*).
   - Generates grounded prompts prioritizing the user's selected subject and strictly anchored to source documents.
   - Enforces anti-hallucination rules: any missing information is explicitly listed in `source_coverage.content_gaps`.

2. **Required Study Materials Components:**
   - **Reviewer:** Main topics, subtopics, concepts, definitions, formulas, and learning objectives.
   - **Summary:** High-yield core summary of central ideas.
   - **Key Notes:** Grouped notes, key concepts, bulleted takeaways.
   - **Flashcards:** Terminology and Q&A pairs tagged with difficulty levels (`easy`, `medium`, `hard`).
   - **Quizzes:** Multiple-choice, true/false, identification, and short-answer questions with answer keys and explanations.
   - **Exams:** Comprehensive multi-tiered assessments with points and answer keys.
   - **Source Coverage & Gaps:** Complete breakdown of covered topics and missing material.

3. **Dynamic Token & Model Capability Management:**
   - Model capability registry mapping model families (`llama3`, `llama3.2`, `qwen2.5`, `mistral`, `phi3`, etc.) to context windows (up to 128k) and max completion limits (up to 8k).
   - Calculates consumed input tokens and assigns the maximum safe output budget rather than hardcoding 2048.
   - Issues user warnings and triggers adaptive Map-Reduce chunking when documents approach context capacity.

4. **Model-Aware Temperature Optimization:**
   - Low to moderate temperatures (0.2–0.3) for factual extraction and study material generation.
   - Custom temperature validation against model boundaries.

5. **Image Document OCR:**
   - Integrated lightweight OCR (`rapidocr-onnxruntime` + `pillow`) extracting clean text from uploaded lecture slides, photos, whiteboards, and textbook images.

6. **JSON Repair & Offline Resilience:**
   - Sanitizes and repairs minor LLM formatting anomalies (markdown fence stripping, trailing comma repair, bracket closing).
   - Validates against typed Pydantic models.
   - Full deterministic offline fallback when Ollama is unreachable.

7. **Backward Compatibility:**
   - Preserves all existing `AIGenerateResponse` envelope fields while embedding the new structured `study_materials` payload.

---

## 3. Data Contracts & Schemas (`app/schemas/ai.py`)

### 3.1 Study Material Models

```python
from typing import Literal
from pydantic import BaseModel, Field

class ReviewerSection(BaseModel):
    title: str = Field(description="Section heading")
    content: str = Field(description="Detailed conceptual explanation")
    key_points: list[str] = Field(default_factory=list, description="Essential key points")

class Reviewer(BaseModel):
    title: str = Field(description="Reviewer title")
    sections: list[ReviewerSection] = Field(default_factory=list)

class Summary(BaseModel):
    content: str = Field(description="Concise synthesis of core concepts")

class KeyNotesItem(BaseModel):
    topic: str = Field(description="Concept or subtopic name")
    notes: list[str] = Field(default_factory=list, description="Organized bullet notes")

class Flashcard(BaseModel):
    question: str = Field(description="Question or prompt")
    answer: str = Field(description="Accurate factual answer")
    topic: str = Field(description="Associated subject topic")
    difficulty: Literal["easy", "medium", "hard"] = "medium"

class QuizQuestion(BaseModel):
    type: Literal["multiple_choice", "true_false", "identification", "short_answer"]
    question: str
    options: list[str] | None = None
    correct_answer: str
    explanation: str
    topic: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"

class ExamQuestion(BaseModel):
    type: Literal["multiple_choice", "true_false", "identification", "short_answer", "essay"]
    question: str
    options: list[str] | None = None
    correct_answer: str
    explanation: str
    topic: str
    difficulty: Literal["easy", "medium", "hard"] = "hard"
    points: int = 1

class Exam(BaseModel):
    title: str
    questions: list[ExamQuestion]
    total_questions: int
    total_points: int

class SourceCoverage(BaseModel):
    covered_topics: list[str] = Field(default_factory=list)
    content_gaps: list[str] = Field(
        default_factory=list, 
        description="Explicit gaps identified in source documents instead of hallucinating"
    )

class StudyMaterialsResponse(BaseModel):
    intent: Literal["question", "study_reviewer"] = "study_reviewer"
    direct_answer: str | None = Field(
        default=None, 
        description="Immediate direct answer if user asked an ad-hoc question"
    )
    topic: str = Field(description="Selected subject or main topic")
    source_summary: str = Field(description="Brief overview of source materials")
    reviewer: Reviewer
    summary: Summary
    key_notes: list[KeyNotesItem]
    flashcards: list[Flashcard]
    quizzes: list[QuizQuestion]
    exam: Exam
    source_coverage: SourceCoverage
```

### 3.2 Enhanced Envelope

```python
class AIGenerateResponse(BaseModel):
    model_used: str
    response_text: str
    prompt: str
    attached_files_count: int
    ingested_files: list[ExtractedFileContent]
    is_ollama_online: bool
    execution_time_seconds: float
    study_materials: StudyMaterialsResponse | None = None
    warnings: list[str] = Field(
        default_factory=list,
        description="User warnings regarding token budgeting, OCR notices, or truncation"
    )
```

---

## 4. Component Architecture & Responsibilities

```
                                      POST /api/v1/ai/generate-with-files
                                                      │
                                                      ▼
                                            [app.api.v1.endpoints.ai]
                                                      │
                                    ┌─────────────────┴──────────────────┐
                                    ▼                                    ▼
                         [file_parser.py (OCR)]             [local_ai_service.py]
                        - PDF, Word, Excel, CSV                          │
                        - Image OCR via RapidOCR                         ▼
                                                            [token_manager.py]
                                                            - Estimate input tokens
                                                            - Fetch model limits
                                                            - Compute dynamic max_tokens
                                                            - Issue oversize warnings
                                                                         │
                                                                         ▼
                                                            [study_reviewer_service.py]
                                                            - Classify intent (QA vs Study)
                                                            - Construct grounded prompt
                                                            - Enforce strict JSON
                                                                         │
                                                                         ▼
                                                            [Ollama API Client / Fallback]
                                                            - Dynamic temp (0.2-0.3)
                                                            - Dynamic num_predict
                                                                         │
                                                                         ▼
                                                            [json_repair_service.py]
                                                            - Strip markdown fences
                                                            - Fix syntax & trailing commas
                                                            - Validate Pydantic schema
                                                                         │
                                                                         ▼
                                                            [AIGenerateResponse Envelope]
```

### 4.1 `app/services/model_registry.py`
* Encapsulates `ModelProfile(context_tokens, max_output_tokens, default_temp)`.
* Pre-configured profiles for:
  - `llama3.2:1b`, `llama3.2:3b`: 128k context, 8k output, 0.25 temp.
  - `llama3:latest`: 8k context, 4k output, 0.3 temp.
  - `qwen2.5:*`, `qwen3.5:*`: 32k–128k context, 8k output, 0.2 temp.
  - `mistral:7b`: 32k context, 8k output, 0.3 temp.
  - `phi3:mini`: 128k context, 4k output, 0.25 temp.
  - `default`: 8k context, 4k output, 0.3 temp.
* Exposes `get_model_profile(model_tag: str) -> ModelProfile`.

### 4.2 `app/services/token_manager.py`
* Character-to-token heuristic (`chars / 3.8`).
* Computes dynamic `num_predict`:
  $$\text{Budget} = \min(\text{model.max\_output\_tokens}, \max(1024, \text{model.context\_tokens} - \text{input\_tokens} - 500))$$
* Emits user warnings if input exceeds 75% of context window.

### 4.3 `app/services/file_parser.py` (OCR Integration)
* Recognizes `.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`.
* Invokes `RapidOCR` to extract text from images and updates `ExtractedFileContent(extracted_text=..., file_type="image")`.
* Gracefully degrades if image contains no readable characters without throwing fatal exceptions.

### 4.4 `app/services/study_reviewer_service.py`
* Intent classifier: detects interrogative questions (`intent="question"`) vs study material topics (`intent="study_reviewer"`).
* Grounded prompt builder:
  - Formulates system prompt as an academic evaluator and reviewer generator.
  - Embeds uploaded documents cleanly under source material blocks.
  - Specifies schema format and forbids hallucinations.
* Deterministic offline mock generator when Ollama is offline or model fails: builds compliant `StudyMaterialsResponse` from raw text paragraphs and headers.

### 4.5 `app/services/json_repair_service.py`
* Strips markdown fences (` ```json ` / ` ``` `).
* Resolves trailing commas before `}` or `]`.
* Completes unclosed brackets/braces.
* Validates into `StudyMaterialsResponse` with error logging.

---

## 5. Testing Strategy

1. **Unit Tests:**
   - `tests/unit/test_model_registry.py`: Model capability lookups, fallback behavior.
   - `tests/unit/test_token_manager.py`: Dynamic token budgeting, capacity warnings.
   - `tests/unit/test_file_parser_ocr.py`: Image OCR text extraction and text file parsing.
   - `tests/unit/test_json_repair.py`: Markdown fence stripping, malformed JSON recovery, Pydantic validation.
   - `tests/unit/test_study_reviewer_service.py`: Intent classification, prompt construction, offline fallback response generation.
2. **Integration Tests:**
   - `tests/integration/test_ai_study_reviewer_api.py`:
     - Test `POST /api/v1/ai/generate-with-files` with text files and topic.
     - Test `POST /api/v1/ai/generate-with-files` with image OCR upload.
     - Test ad-hoc question intent vs study reviewer intent.
     - Test dynamic token parameters and warning flags.

---

## 6. Spec Self-Review
- **Placeholder scan:** None (all classes, schemas, and formulas are fully specified).
- **Internal consistency:** Fully consistent with FastAPI router patterns, dependency injection (`deps.py`), and Ollama service architecture.
- **Scope check:** Sized appropriately for single implementation execution.
- **Ambiguity check:** Clarified envelope format (Option A), token computation, intent handling, and OCR library.
