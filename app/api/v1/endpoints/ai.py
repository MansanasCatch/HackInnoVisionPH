"""Endpoints for Local AI generation and document ingestion (lessons, notes, files)."""

from typing import Annotated, Literal

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.api.deps import LocalAIServiceDep
from app.api.uploads import read_uploads
from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
    DocumentExtractResponse,
    RAGChunkItem,
    RAGSearchRequest,
    RAGSearchResponse,
)
from app.services.file_parser import parse_uploaded_file

router = APIRouter(prefix="/ai", tags=["Local AI & File Ingestion"])


@router.post(
    "/extract-text",
    response_model=DocumentExtractResponse,
    summary="Extract clean text from uploaded documents (PDF, Word, Excel, CSV, Image, Text)",
    description=(
        "Extracts textual content, page numbers, and metadata from uploaded files "
        "and returns structured JSON."
    ),
)
async def extract_text(
    files: Annotated[
        UploadFile | list[UploadFile] | None,
        File(description="Attached document or PDF files to extract"),
    ] = None,
) -> DocumentExtractResponse:
    """Extract text from uploaded documents and return structured JSON."""
    uploaded = await read_uploads(files)
    if not uploaded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file must be provided for extraction.",
        )

    extracted_files = [
        parse_uploaded_file(filename=filename, content_bytes=content, content_type=ct)
        for filename, content, ct in uploaded
    ]

    return DocumentExtractResponse(
        success=True,
        total_files=len(extracted_files),
        files=extracted_files,
    )


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
        Form(description="Topic from user UI (e.g. 'Cell division'). Auto-inferred if blank."),
    ] = None,
    onboarding_id: Annotated[int | None, Form(description="Onboarding account ID")] = None,
    model_override: Annotated[str | None, Form(description="Optional model tag override")] = None,
    system_prompt: Annotated[str | None, Form(description="Optional system prompt")] = None,
    text_context: Annotated[
        str | None, Form(description="Free-text notes the learner typed or pasted")
    ] = None,
    temperature: Annotated[float, Form(description="Temperature sampling")] = 0.7,
    max_tokens: Annotated[int, Form(description="Max generation tokens")] = 2048,
    item_count: Annotated[int, Form(ge=10, le=50)] = 10,
    material_types: Annotated[
        list[Literal["key_notes", "flashcards", "quizzes", "exam"]] | None, Form()
    ] = None,
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
        item_count=item_count,
        material_types=material_types or ["key_notes", "flashcards", "quizzes", "exam"],
    )

    return service.generate(request=req, uploaded_files=uploaded_files)


@router.post(
    "/search-and-retrieve",
    response_model=RAGSearchResponse,
    summary="Search web and retrieve authoritative RAG chunks for topic",
    description=("Topic search using SearXNG or Wikipedia fallback with pure Python BM25 ranking."),
)
def search_and_retrieve(request: RAGSearchRequest) -> RAGSearchResponse:
    """Execute topic search and extract top-ranked RAG passages."""
    from app.services.rag_service import bm25_rank_chunks, chunk_text, search_web_for_topic

    query = request.topic.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A non-empty search topic must be provided.",
        )

    # 1. Web research
    web_results = search_web_for_topic(query, max_results=request.max_results)

    # 2. Semantic chunking
    raw_chunks: list[dict] = []
    chunk_counter = 1
    for res in web_results:
        text_segments = chunk_text(res.content, chunk_size=250, overlap=40)
        for segment in text_segments:
            raw_chunks.append(
                {
                    "chunk_id": chunk_counter,
                    "title": res.title,
                    "url": res.url,
                    "content": segment,
                }
            )
            chunk_counter += 1

    # 3. BM25 Ranking
    scored_chunks = bm25_rank_chunks(query, raw_chunks, top_k=request.top_k_chunks)

    # Fallback to direct snippet if ranking returned empty
    if not scored_chunks and web_results:
        scored_chunks = [
            RAGChunkItem(
                chunk_id=idx,
                title=res.title,
                url=res.url,
                content=res.content[:600],
                score=1.0,
            )
            for idx, res in enumerate(web_results[: request.top_k_chunks], 1)
        ]

    chunk_models = [
        RAGChunkItem(
            chunk_id=c.chunk_id,
            title=c.title,
            url=c.url,
            content=c.content,
            score=c.score,
        )
        if not isinstance(c, RAGChunkItem)
        else c
        for c in scored_chunks
    ]

    detected_sources = set()
    for c in chunk_models:
        u_lower = c.url.lower()
        if any(
            d in u_lower
            for d in ("doi.org", "oup.com", "springer", "sciencedirect", "wiley", "nature.com")
        ):
            detected_sources.add("CrossRef Academic")
        elif any(d in u_lower for d in ("nih.gov", "pubmed", "pmc")):
            detected_sources.add("PubMed Central")
        elif "wikipedia.org" in u_lower:
            detected_sources.add("Wikipedia")
        elif "8080" in u_lower:
            detected_sources.add("SearXNG")
        elif u_lower.startswith("http"):
            detected_sources.add("Authoritative Web")

    if detected_sources:
        source_engine = " & ".join(sorted(detected_sources)) + " (BM25 RAG)"
    else:
        source_engine = "Authoritative Multi-Source Web RAG (BM25)"

    aggregated = "\n\n".join(
        f"[{idx}] {c.title} ({c.url})\n{c.content}" for idx, c in enumerate(chunk_models, 1)
    )

    return RAGSearchResponse(
        success=True,
        query=query,
        source_engine=source_engine,
        search_engine=source_engine,
        total_sources=len(web_results),
        total_chunks=len(chunk_models),
        retrieved_chunks=chunk_models,
        aggregated_context=aggregated,
    )
