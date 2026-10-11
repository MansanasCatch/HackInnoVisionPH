# Zero-Dependency RAG Web Search, 20-30 Item Practice Sets, and Multi-Set Combiner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-dependency in-memory RAG pipeline with online topic search (SearXNG + public educational fallback), 20–30 item practice quiz synthesis, and a saved resources multi-select combiner.

**Architecture:** A pure-Python standard-library BM25 RAG engine and HTTP retriever in `app/services/rag_service.py` connects to FastAPI endpoints. The assessment engine in `app/services/study_reviewer_service.py` scales output to 20–30 items. The React frontend adds a "Browse online" mode in `/ingest` and multi-selection combination in `/library`.

**Tech Stack:** Python 3.12 (standard library `urllib.request`, `math`, `collections`), FastAPI, React 19, TypeScript, Vite, Playwright.

**Spec:** [`docs/superpowers/specs/2026-10-11-rag-web-search-practice-combiner-design.md`](file:///c:/Users/Anastasya/Desktop/hackaton/InnoVisionPH/docs/superpowers/specs/2026-10-11-rag-web-search-practice-combiner-design.md)

## Global Constraints
- Zero external Python dependencies for search or vector storage (must run in standalone `.exe` without Docker).
- All web search network requests must have a strict 5-second timeout and custom User-Agent.
- Quiz practice sets generated must contain at least 20 items (target 20–30).
- Saved resources multi-select must preserve original sets while creating a combined practice set.

## Review Focus
1. Offline network failure when browsing online: gracefully fall back to local documents and display clear notice.
2. Malformed search payload: return clean empty chunk list without unhandled 500 exceptions.
3. Combining sets with disjoint subjects: combine smoothly without duplicate question IDs.
4. Token budget overflow with 20–30 questions: ensure chunk prompt adheres to safe token allocation.
5. Zero saved resources selected: keep combiner action disabled until at least 1 set is selected.

---

### Task 1: Zero-Dependency RAG & Web Search Engine

**Files:**
- Create: `app/services/rag_service.py`
- Test: `tests/unit/test_rag_service.py`

**Interfaces:**
- Produces:
  - `class RAGChunk(chunk_id: int, title: str, url: str, content: str, score: float)`
  - `class SearchResult(title: str, snippet: str, url: str, content: str)`
  - `search_web_for_topic(query: str, max_results: int = 5) -> list[SearchResult]`
  - `chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]`
  - `bm25_rank_chunks(query: str, chunks: list[dict], top_k: int = 6) -> list[RAGChunk]`

- [ ] **Step 1: Write failing unit tests in `tests/unit/test_rag_service.py`**
  Assert BM25 ranking orders relevant chunks first, chunking preserves sentences, and fallback search handles timeouts.

- [ ] **Step 2: Run test to verify it fails**
  Run: `.venv\Scripts\python -m pytest tests/unit/test_rag_service.py -v`
  Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.rag_service'`

- [ ] **Step 3: Implement `app/services/rag_service.py`**
  Implement `chunk_text`, `bm25_rank_chunks`, and `search_web_for_topic` using standard library `urllib.request`, `math`, `re`, and `collections.Counter`.

- [ ] **Step 4: Run test to verify it passes**
  Run: `.venv\Scripts\python -m pytest tests/unit/test_rag_service.py -v`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run: `git add app/services/rag_service.py tests/unit/test_rag_service.py && git commit -m "feat(rag): add zero-dependency BM25 RAG engine and web retriever"`

---

### Task 2: Web Search & RAG API Endpoints

**Files:**
- Modify: `app/schemas/ai.py`
- Modify: `app/api/v1/endpoints/ai.py`
- Test: `tests/integration/test_rag_ai_api.py`

**Interfaces:**
- Consumes: `app.services.rag_service`
- Produces: `POST /api/v1/ai/search-and-retrieve`, returns `RAGSearchResponse`

- [ ] **Step 1: Write failing integration test in `tests/integration/test_rag_ai_api.py`**
  Test calling `/api/v1/ai/search-and-retrieve` with a topic query returns 200 with ranked chunks and aggregated context.

- [ ] **Step 2: Run test to verify it fails**
  Run: `.venv\Scripts\python -m pytest tests/integration/test_rag_ai_api.py -v`
  Expected: FAIL with 404 Not Found

- [ ] **Step 3: Implement endpoint in `app/api/v1/endpoints/ai.py` and schemas in `app/schemas/ai.py`**
  Add `RAGSearchRequest` and `RAGSearchResponse` schemas, and add `search_and_retrieve` route.

- [ ] **Step 4: Run test to verify it passes**
  Run: `.venv\Scripts\python -m pytest tests/integration/test_rag_ai_api.py -v`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run: `git add app/schemas/ai.py app/api/v1/endpoints/ai.py tests/integration/test_rag_ai_api.py && git commit -m "feat(api): add /ai/search-and-retrieve RAG endpoint"`

---

### Task 3: 20–30 Item Practice Set Generator

**Files:**
- Modify: `app/services/study_reviewer_service.py`
- Test: `tests/unit/test_study_reviewer_20_items.py`

**Interfaces:**
- Produces: `build_study_prompts` requiring 20–30 questions; `build_offline_fallback_study_materials` generating $\ge 20$ questions.

- [ ] **Step 1: Write failing test in `tests/unit/test_study_reviewer_20_items.py`**
  Assert generated offline study materials contain at least 20 total quiz and exam items.

- [ ] **Step 2: Run test to verify it fails**
  Run: `.venv\Scripts\python -m pytest tests/unit/test_study_reviewer_20_items.py -v`
  Expected: FAIL (current fallback produces only 3 questions)

- [ ] **Step 3: Update `app/services/study_reviewer_service.py`**
  Scale prompt instructions to request 20–30 items (15 multiple choice, 5 true/false, 5–10 short answer/identification), and expand the deterministic fallback question pool to 20–30 items across subtopics.

- [ ] **Step 4: Run test to verify it passes**
  Run: `.venv\Scripts\python -m pytest tests/unit/test_study_reviewer_20_items.py -v`
  Expected: PASS

- [ ] **Step 5: Commit**
  Run: `git add app/services/study_reviewer_service.py tests/unit/test_study_reviewer_20_items.py && git commit -m "feat(ai): scale practice quiz generator to 20-30 items"`

---

### Task 4: Frontend Online Web Search & RAG Trigger in Ingestion

**Files:**
- Modify: `frontend/src/api/types.ts`
- Modify: `frontend/src/api/client.ts`
- Modify: `frontend/src/App.tsx`

**Interfaces:**
- Produces: `api.searchAndRetrieve(topic)` in frontend API client; "Browse online" button in `/ingest`.

- [ ] **Step 1: Add types and client methods in `frontend/src/api/types.ts` and `frontend/src/api/client.ts`**
  Define `RAGSearchResponse` and `searchAndRetrieve(topic: string)`.

- [ ] **Step 2: Add "Browse online" action in `ContentIngestion` inside `frontend/src/App.tsx`**
  When selected, calls `api.searchAndRetrieve(topic)`, displays retrieved web sources banner, and feeds extracted text into notes for resource generation.

- [ ] **Step 3: Verify frontend build**
  Run: `npm --prefix frontend run build`
  Expected: exit code 0

- [ ] **Step 4: Commit**
  Run: `git add frontend/src/api/types.ts frontend/src/api/client.ts frontend/src/App.tsx && git commit -m "feat(frontend): add browse online RAG search in content ingestion"`

---

### Task 5: Frontend Saved Resources Multi-Select & Set Combiner

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/materials.ts`

**Interfaces:**
- Produces: `combineMaterialSets(sets: MaterialSet[]) -> MaterialSet`
- Produces: Multi-select checkboxes, "Select All", and "Combine Selected Sets" in `ResourceLibrary`.

- [ ] **Step 1: Implement `combineMaterialSets` in `frontend/src/materials.ts`**
  Merges `reviewer.sections`, `flashcards`, and `quizzes` across multiple sets, updating total count to 20–30+ items.

- [ ] **Step 2: Add selection checkboxes and combine button in `ResourceLibrary` in `frontend/src/App.tsx`**
  Support selecting all or picking specific sets. Clicking "Combine Selected Sets ({N})" merges them and opens the 20+ question practice quiz.

- [ ] **Step 3: Verify frontend build**
  Run: `npm --prefix frontend run build`
  Expected: exit code 0

- [ ] **Step 4: Commit**
  Run: `git add frontend/src/materials.ts frontend/src/App.tsx && git commit -m "feat(frontend): add saved resources multi-select and set combiner"`

---

### Task 6: End-to-End Automated Verification

**Files:**
- Create: `frontend/test_rag_and_combiner.cjs`

- [ ] **Step 1: Write Playwright test script `frontend/test_rag_and_combiner.cjs`**
  Verify:
  1. Searching online for a topic fetches RAG chunks.
  2. Generated quiz contains 20+ practice questions.
  3. Selecting multiple saved sets and clicking "Combine Selected Sets" loads combined 20+ question exam.
  4. Capture visual screenshots.

- [ ] **Step 2: Run Playwright test script**
  Run: `node frontend/test_rag_and_combiner.cjs`
  Expected: exit code 0 with all assertions passing.

- [ ] **Step 3: Run full backend pytest suite**
  Run: `.venv\Scripts\python -m pytest tests -v`
  Expected: all tests pass with 0 regressions.

- [ ] **Step 4: Commit and push**
  Run: `git add frontend/test_rag_and_combiner.cjs && git commit -m "test(e2e): verify RAG online retrieval, 20-30 items, and set combiner"`
