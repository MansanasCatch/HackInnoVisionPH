# AI Study Reviewer Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the `/api/v1/ai/generate-with-files` endpoint into a robust, educational AI Study Reviewer Generation API that extracts text and image OCR from uploaded documents, detects user intent, dynamically budgets tokens and temperatures according to model profiles, and outputs validated structured JSON study materials with offline fallback.

**Architecture:** Layered Clean Architecture. Add `model_registry.py`, `token_manager.py`, `json_repair_service.py`, and `study_reviewer_service.py` to `app/services/`. Enhance `file_parser.py` with image OCR via RapidOCR, and wire everything into `local_ai_service.py` and the FastAPI presentation layer.

**Tech Stack:** FastAPI, Pydantic v2, RapidOCR-ONNXRuntime, Pillow, Ollama HTTP API, Pytest.

**Spec:** [docs/superpowers/specs/2026-10-10-ai-study-reviewer-generation-design.md](file:///c:/Users/Anastasya/Desktop/hackaton/InnoVisionPH/docs/superpowers/specs/2026-10-10-ai-study-reviewer-generation-design.md)

## Global Constraints
- Target endpoint: `POST /api/v1/ai/generate-with-files` (`multipart/form-data`).
- Envelope response model: `AIGenerateResponse` retaining all existing fields for backward compatibility while adding `study_materials: StudyMaterialsResponse | None = None` and `warnings: list[str] = []`.
- Output must be strict, valid JSON without unescaped fences or markdown prefixes.
- Zero external C binaries required for OCR; use self-contained ONNX (`rapidocr-onnxruntime`).
- All tests must pass warning-free (`filterwarnings = ["error"]`).

## Review Focus
1. **Model Tag Variation:** Handles non-standard model tags gracefully with safe default fallback profile (8k context, 4k completion, 0.3 temp).
2. **Image with Zero Readable Text:** Does not raise 500 error; annotates `"[No readable text detected in image]"` and continues document processing.
3. **Truncated/Malformed LLM JSON:** Extracts JSON object, strips markdown fences, repairs trailing commas and unclosed brackets, and falls back to deterministic structured study materials if unparseable.
4. **Oversized Input Context:** Emits warning when input tokens exceed 75% of context window and clamps output tokens safely without crashing.
5. **Ollama Server Offline:** Returns `200 OK` with `is_ollama_online=False`, warning message, and deterministic structured study reviewer derived from document headings and text.

---

### Task 1: Schemas & Dependencies Setup

**Files:**
- Modify: `requirements.txt`
- Modify: `app/schemas/ai.py`
- Test: `tests/unit/test_study_schemas.py`

**Interfaces:**
- Produces: `ReviewerSection`, `Reviewer`, `Summary`, `KeyNotesItem`, `Flashcard`, `QuizQuestion`, `ExamQuestion`, `Exam`, `SourceCoverage`, `StudyMaterialsResponse`, updated `AIGenerateResponse` in `app.schemas.ai`.

- [ ] **Step 1: Install OCR dependencies and update requirements.txt**
  Add `rapidocr-onnxruntime==1.4.4` and `pillow==12.3.0` to `requirements.txt` and install via `uv pip install -r requirements.txt --python .venv\Scripts\python.exe`.

- [ ] **Step 2: Write failing unit test for study schemas**
  Create `tests/unit/test_study_schemas.py` testing validation of `StudyMaterialsResponse` and the enhanced `AIGenerateResponse` with `study_materials` and `warnings`.

- [ ] **Step 3: Run test to verify it fails**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_study_schemas.py`
  Expected: FAIL with `ImportError: cannot import name 'StudyMaterialsResponse'`

- [ ] **Step 4: Implement educational schemas in `app/schemas/ai.py`**
  Add all study models and update `AIGenerateResponse` with optional `study_materials: StudyMaterialsResponse | None = None` and `warnings: list[str] = []`.

- [ ] **Step 5: Run test to verify it passes**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_study_schemas.py`
  Expected: PASS

- [ ] **Step 6: Commit**
  ```bash
  git add requirements.txt app/schemas/ai.py tests/unit/test_study_schemas.py
  git commit -m "feat(ai): define structured study materials schemas and update dependencies"
  ```

---

### Task 2: Model Capability Registry & Dynamic Token Budget Manager

**Files:**
- Create: `app/services/model_registry.py`
- Create: `app/services/token_manager.py`
- Test: `tests/unit/test_model_registry.py`
- Test: `tests/unit/test_token_manager.py`

**Interfaces:**
- Produces:
  - `get_model_profile(model_tag: str) -> ModelProfile` in `app.services.model_registry`.
  - `estimate_tokens(text: str) -> int`, `calculate_safe_token_budget(model: ModelProfile, input_tokens: int, requested_max_tokens: int | None) -> int`, and `check_capacity_warnings(model: ModelProfile, input_tokens: int) -> list[str]` in `app.services.token_manager`.

- [ ] **Step 1: Write failing tests for model registry and token manager**
  Create `tests/unit/test_model_registry.py` testing lookup for `llama3.2:3b`, `qwen2.5`, and unknown models.
  Create `tests/unit/test_token_manager.py` testing token estimation, safe budget clamping, and capacity warning generation.

- [ ] **Step 2: Run tests to verify failure**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_model_registry.py tests/unit/test_token_manager.py`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `app/services/model_registry.py`**
  Implement `ModelProfile(context_tokens, max_output_tokens, default_temp)` and `get_model_profile(model_tag)` with families for Llama 3, Llama 3.2, Qwen, Mistral, Phi-3, and safe fallback.

- [ ] **Step 4: Implement `app/services/token_manager.py`**
  Implement `estimate_tokens`, `calculate_safe_token_budget`, and `check_capacity_warnings` with 75% capacity threshold warnings.

- [ ] **Step 5: Run tests to verify pass**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_model_registry.py tests/unit/test_token_manager.py`
  Expected: PASS

- [ ] **Step 6: Commit**
  ```bash
  git add app/services/model_registry.py app/services/token_manager.py tests/unit/test_model_registry.py tests/unit/test_token_manager.py
  git commit -m "feat(ai): add model capability registry and dynamic token budget manager"
  ```

---

### Task 3: Image OCR Ingestion in File Parser

**Files:**
- Modify: `app/services/file_parser.py`
- Test: `tests/unit/test_file_parser_ocr.py`

**Interfaces:**
- Consumes: RapidOCR-ONNXRuntime and Pillow.
- Produces: `parse_uploaded_file(filename, content, content_type) -> ExtractedFileContent` with OCR text extraction for image types (`png`, `jpg`, `jpeg`, `webp`, `bmp`).

- [ ] **Step 1: Write failing test for image OCR parsing**
  Create `tests/unit/test_file_parser_ocr.py` that generates a synthetic test image using Pillow with text `"Physics 101: Energy Conservation"`, passes it to `parse_uploaded_file`, and asserts that the text is extracted. Also test an empty/blank image.

- [ ] **Step 2: Run test to verify failure**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_file_parser_ocr.py`
  Expected: FAIL (currently images only populate `base64_data`, `extracted_text` remains placeholder)

- [ ] **Step 3: Implement RapidOCR extraction in `app/services/file_parser.py`**
  Add `_extract_text_from_image(image_bytes: bytes) -> str` using `RapidOCR()`. Update `parse_uploaded_file` to populate `extracted_text` with recognized text lines while preserving `base64_data`.

- [ ] **Step 4: Run test to verify pass**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_file_parser_ocr.py tests/unit/test_file_parser.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add app/services/file_parser.py tests/unit/test_file_parser_ocr.py
  git commit -m "feat(ai): implement rapid OCR for image document ingestion"
  ```

---

### Task 4: JSON Repair and Validation Service

**Files:**
- Create: `app/services/json_repair_service.py`
- Test: `tests/unit/test_json_repair.py`

**Interfaces:**
- Produces: `clean_and_parse_study_json(raw_text: str) -> StudyMaterialsResponse | None` in `app.services.json_repair_service`.

- [ ] **Step 1: Write failing test for JSON cleaning and repair**
  Create `tests/unit/test_json_repair.py` testing:
  - Markdown fence stripping (` ```json ... ``` `).
  - Trailing comma removal in lists and objects.
  - Bracket completion for truncated strings.
  - Validation into `StudyMaterialsResponse`.
  - Non-JSON garbage returning `None`.

- [ ] **Step 2: Run test to verify failure**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_json_repair.py`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `app/services/json_repair_service.py`**
  Implement regex fence extraction, bracket balancing, trailing comma sanitation, and Pydantic validation.

- [ ] **Step 4: Run test to verify pass**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_json_repair.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add app/services/json_repair_service.py tests/unit/test_json_repair.py
  git commit -m "feat(ai): implement robust JSON sanitizer, repair, and validator"
  ```

---

### Task 5: Study Reviewer Prompt Orchestrator & Offline Fallback

**Files:**
- Create: `app/services/study_reviewer_service.py`
- Test: `tests/unit/test_study_reviewer_service.py`

**Interfaces:**
- Produces:
  - `detect_prompt_intent(prompt: str) -> Literal["question", "study_reviewer"]`
  - `build_study_prompts(prompt: str, intent: str, documents: list[ExtractedFileContent], notes_context: str | None) -> tuple[str, str]` (returns system prompt and user prompt)
  - `build_offline_fallback_study_materials(topic: str, intent: str, documents: list[ExtractedFileContent], warning_msg: str) -> StudyMaterialsResponse`

- [ ] **Step 1: Write failing tests for intent detection, prompt building, and offline fallback**
  Create `tests/unit/test_study_reviewer_service.py` verifying:
  - "What is the speed of light?" -> `intent == "question"`.
  - "Reviewer for Cellular Biology" -> `intent == "study_reviewer"`.
  - System prompt includes anti-hallucination rules and schema guidelines.
  - Offline fallback generates valid, renderable `StudyMaterialsResponse` with summary, key notes, and gap notification.

- [ ] **Step 2: Run test to verify failure**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_study_reviewer_service.py`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement `app/services/study_reviewer_service.py`**
  Implement intent classifier, educational prompt generator, and deterministic offline study materials synthesizer.

- [ ] **Step 4: Run test to verify pass**
  Run: `.venv\Scripts\python.exe -m pytest tests/unit/test_study_reviewer_service.py`
  Expected: PASS

- [ ] **Step 5: Commit**
  ```bash
  git add app/services/study_reviewer_service.py tests/unit/test_study_reviewer_service.py
  git commit -m "feat(ai): implement educational prompt orchestrator and deterministic fallback"
  ```

---

### Task 6: Wire Pipeline into `LocalAIService` & API Endpoints

**Files:**
- Modify: `app/services/local_ai_service.py`
- Modify: `app/api/v1/endpoints/ai.py`
- Test: `tests/integration/test_ai_study_reviewer_api.py`

**Interfaces:**
- Consumes: All services from Tasks 1–5.
- Produces: Fully integrated `POST /api/v1/ai/generate-with-files` returning `AIGenerateResponse` populated with `study_materials` and `warnings`.

- [ ] **Step 1: Write integration tests for the endpoint**
  Create `tests/integration/test_ai_study_reviewer_api.py` testing:
  - Calling `POST /api/v1/ai/generate-with-files` with a study topic and text file.
  - Calling with an image containing text.
  - Calling with an ad-hoc question.
  - Verifying `study_materials` is populated and valid.
  - Verifying `warnings` captures token or offline notices.

- [ ] **Step 2: Run integration tests to verify failure**
  Run: `.venv\Scripts\python.exe -m pytest tests/integration/test_ai_study_reviewer_api.py`
  Expected: FAIL

- [ ] **Step 3: Update `LocalAIService` in `app/services/local_ai_service.py`**
  Integrate `get_model_profile`, `calculate_safe_token_budget`, `check_capacity_warnings`, `build_study_prompts`, `clean_and_parse_study_json`, and `build_offline_fallback_study_materials`. Ensure temperature and `num_predict` dynamically adapt to model capabilities.

- [ ] **Step 4: Update endpoint in `app/api/v1/endpoints/ai.py`**
  Validate file sizes and non-empty documents; pass parameters to `service.generate`.

- [ ] **Step 5: Run integration tests to verify pass**
  Run: `.venv\Scripts\python.exe -m pytest tests/integration/test_ai_study_reviewer_api.py`
  Expected: PASS

- [ ] **Step 6: Commit**
  ```bash
  git add app/services/local_ai_service.py app/api/v1/endpoints/ai.py tests/integration/test_ai_study_reviewer_api.py
  git commit -m "feat(ai): integrate study reviewer pipeline into local AI service and endpoint"
  ```

---

### Task 7: Full Test Suite Verification & Live Verification

**Files:**
- None (verification & regression)

- [ ] **Step 1: Run full test suite**
  Run: `.venv\Scripts\python.exe -m pytest`
  Verify all existing and new tests pass with 0 failures and 0 warnings.

- [ ] **Step 2: Run linter and formatting check**
  Run: `.venv\Scripts\python.exe -m ruff check .`
  Verify zero lint errors.

- [ ] **Step 3: Live end-to-end verification**
  Send a live multipart POST request with a document to `http://127.0.0.1:8000/api/v1/ai/generate-with-files` and verify the returned `study_materials` payload.

- [ ] **Step 4: Final commit and summary**
  ```bash
  git commit --allow-empty -m "chore(ai): verify full study reviewer generation suite"
  ```
