# Zero-Dependency RAG Web Search, 20-30 Item Practice Sets, and Multi-Set Combiner Specification

## 1. Overview & Objective
This specification describes the architectural addition of a zero-dependency Retrieval-Augmented Generation (RAG) system with online topic research, 20-30 question practice quiz sets, and a multi-set combiner in Calibrat8.

Because Calibrat8 is targeted to run as a standalone desktop executable (`.exe`) on diverse hardware without requiring Docker, external databases, or heavy native C++ extensions, all retrieval, chunking, and web searching are implemented using Python's standard library with zero external runtime dependencies.

---

## 2. Core Subsystems & Components

### 2.1 Online Web Search Engine (`app/services/rag_service.py`)
- **Dual-Engine Search**:
  1. **SearXNG Support**: If `SEARXNG_URL` is set or an instance responds at `http://localhost:8080`, queries its `/search?q={query}&format=json` endpoint.
  2. **Direct Educational Web Search Fallback (Zero-Config)**: Uses Python's standard library `urllib.request` to query open public endpoints (Wikipedia OpenSearch and Summary APIs + DuckDuckGo HTML/Instant API) with a 5-second timeout and custom User-Agent.
- **Web Result Normalization**:
  - Extracts clean text, titles, source URLs, and section summaries.
  - Returns a normalized list of `SearchResult(title, snippet, url, content)`.

### 2.2 Pure-Python In-Memory RAG Engine (`app/services/rag_service.py`)
- **Semantic Chunking**:
  - Splits source articles and user documents into coherent passages (250–400 words / paragraphs) with 50-word sliding overlap.
  - Preserves source provenance (`source_title`, `chunk_id`).
- **BM25 / Keyword Retrieval**:
  - Implements lightweight BM25 scoring in pure Python (`math.log`, term frequency, document length normalization).
  - Given a topic query, ranks all candidate chunks and retrieves top $K$ (default: 6) authoritative passages.
- **Prompt Injection**:
  - Assembles the retrieved passages into an authoritative grounded context block:
    ```
    === GROUNDED RAG SOURCES FOR TOPIC: {topic} ===
    [SOURCE 1]: {title} ({url})
    {chunk_content}
    ================================================
    ```

### 2.3 20–30 Item Practice Set Generator (`app/services/study_reviewer_service.py`)
- **Question Volume Scaling**:
  - System prompt and schema updated to require 20 to 30 comprehensive practice questions:
    - 15 Multiple Choice questions with 4 plausible options, designated correct option, and detailed explanation.
    - 5 True / False conceptual check questions.
    - 5 to 10 Identification / Short Answer questions with complete answer rubrics.
- **Deterministic Offline Fallback**:
  - If Local LLM is offline or times out, the deterministic fallback synthesizes a rich, curriculum-balanced pool of 20–30 items derived from the indexed RAG passages or user documents.

### 2.4 Saved Resources Multi-Select & Set Combiner (`frontend/src/App.tsx`)
- **UI State in `ResourceLibrary`**:
  - Each saved resource card/pill has a selection checkbox.
  - A **"Select All"** toggle selects or deselects all saved sets.
  - A dynamic button: **"Combine Selected Sets ({selectedCount})"** appears when $\ge 1$ sets are selected.
- **Combination Logic (`combineStudySets`)**:
  - Merges key notes into a combined syllabus list.
  - Combines flashcards without duplicate questions.
  - Merges quiz items into a unified practice exam with 20–30+ questions.
  - Instantly loads the combined set into the Flashcard and Quiz viewers.

---

## 3. API Contracts & Endpoints

### 3.1 Web Search & RAG Endpoint (`POST /api/v1/ai/search-and-retrieve`)
- **Request Body**:
  ```json
  {
    "topic": "Cellular Respiration & Energy",
    "max_results": 5,
    "top_k_chunks": 6
  }
  ```
- **Response Model**:
  ```json
  {
    "success": true,
    "query": "Cellular Respiration & Energy",
    "source_engine": "searxng" | "wikipedia_fallback",
    "total_sources": 3,
    "retrieved_chunks": [
      {
        "chunk_id": 1,
        "title": "Cellular respiration",
        "url": "https://en.wikipedia.org/wiki/Cellular_respiration",
        "content": "Cellular respiration is a set of metabolic reactions...",
        "score": 4.82
      }
    ],
    "aggregated_context": "..."
  }
  ```

### 3.2 Enhanced Generation with Web RAG (`POST /api/v1/ai/generate-study-reviewer`)
- Accepts `browse_online: bool = False` or `rag_context: str | None`.
- When `browse_online` is `true`, automatically queries `search_and_retrieve(topic)` and injects the retrieved context into the Local LLM before generating the 20–30 item practice set.

---

## 4. Verification & Testing Strategy
1. **Unit Tests (`tests/unit/test_rag_service.py`)**:
   - Verify BM25 chunk ranking and score ordering.
   - Verify fallback web search querying without external servers.
   - Verify chunking preserves sentence boundaries.
2. **Integration Tests (`tests/integration/test_rag_ai_api.py`)**:
   - Test `/api/v1/ai/search-and-retrieve` returns valid JSON with ranked chunks.
   - Test generating 20–30 item practice set with web search RAG enabled.
3. **Frontend E2E Test (`frontend/test_rag_and_combiner.cjs`)**:
   - Test typing topic and clicking "Browse online".
   - Test RAG extraction rendering the retrieved context.
   - Test selecting multiple saved sets in `ResourceLibrary` and clicking "Combine Selected Sets".
   - Verify quiz viewer displays the combined question count (20+ items).
