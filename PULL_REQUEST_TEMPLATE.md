# feat: implement AI study reviewer generation API with OCR and dynamic token budgeting

## Summary of Changes

This Pull Request introduces the **AI Study Reviewer Generation API** for InnoVisionPH. It enables local LLMs (via Ollama) to ingest multi-format educational documents (PDF, DOCX, TXT, MD, CSV, XLSX, and images via OCR) and generate structured, grounded study materials—including comprehensive reviewers, summaries, key concept notes, flashcards, quizzes, scenario-based exams, and source coverage metrics.

### Key Additions & Enhancements

1. **Structured Educational Pydantic Schemas (`app/schemas/ai.py`)**
   - Added models: `Reviewer`, `Summary`, `KeyNotesItem`, `Flashcard`, `QuizQuestion`, `ExamQuestion`, `Exam`, `SourceCoverage`, and `StudyMaterialsResponse`.
   - Updated `AIGenerateResponse` to optionally include structured `study_materials` and runtime capacity `warnings`.

2. **Model Capability Registry & Dynamic Token Budgeting (`app/services/model_registry.py`, `app/services/token_manager.py`)**
   - Profiles context window limitations, max output limits, and parameter sizes for local Ollama models (`gemma:2b`, `llama3:8b`, `mistral:7b`, etc.).
   - Implements dynamic `num_predict` allocation and calculates prompt token budgets using word-to-token heuristics (~1.33 tokens/word).
   - Generates capacity warnings when incoming prompt tokens exceed 75% of a model's context window.

3. **Offline Document OCR Ingestion (`app/services/file_parser.py`)**
   - Integrated `rapidocr-onnxruntime` and `Pillow` to support image formats (`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`).
   - Uses lazy initialization to keep startup lightweight and extracts structured line-by-line text without cloud dependencies.

4. **JSON Sanitization & Repair Service (`app/services/json_repair_service.py`)**
   - Strips markdown code blocks (````json ... ````), conversational preambles, and trailing commentary.
   - Automatically repairs trailing commas and balances unclosed brackets/braces from token-limited generations.
   - Validates sanitized JSON directly against target Pydantic models.

5. **Study Reviewer Orchestration & Fallback Engine (`app/services/study_reviewer_service.py`)**
   - Auto-detects user intent (distinguishes general questions from study reviewer generation).
   - Enforces zero-hallucination system prompts with strict grounding rules based purely on uploaded files.
   - Provides deterministic offline fallback study materials if Ollama is offline or unconfigured.

6. **API Endpoint & Service Wiring (`app/services/local_ai_service.py`, `app/api/v1/endpoints/ai.py`)**
   - Configures Ollama structured JSON format and options.
   - Added 25MB file upload limit validation with descriptive HTTP 400 responses.
   - Extended endpoint to support image MIME types (`image/png`, `image/jpeg`, etc.).

7. **Comprehensive Test Suite & Architecture Docs**
   - Added 40/40 passing unit and integration tests across all schemas, token calculations, OCR extraction, JSON repair, and API endpoints.
   - Included architectural specification (`docs/superpowers/specs/2026-10-10-ai-study-reviewer-generation-design.md`) and implementation plan (`docs/superpowers/plans/2026-10-10-ai-study-reviewer-generation.md`).
