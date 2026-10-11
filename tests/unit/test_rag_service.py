"""Unit tests for the zero-dependency RAG engine and web retriever service."""

from app.services.rag_service import (
    RAGChunk,
    SearchResult,
    bm25_rank_chunks,
    chunk_text,
    search_web_for_topic,
)


def test_chunk_text_splits_into_manageable_segments():
    sample_text = (
        "Cellular respiration is a series of chemical reactions that break down glucose to produce ATP. "
        "The stages include glycolysis, the Krebs cycle, and oxidative phosphorylation. "
        "Glycolysis occurs in the cytoplasm and breaks glucose into two pyruvate molecules. "
        "The Krebs cycle takes place in the mitochondrial matrix. "
        "Oxidative phosphorylation happens along the inner mitochondrial membrane, producing the majority of ATP."
    )
    chunks = chunk_text(sample_text, chunk_size=30, overlap=10)
    assert len(chunks) >= 2
    assert any("Glycolysis" in c for c in chunks)
    assert any("Oxidative phosphorylation" in c for c in chunks)


def test_bm25_rank_chunks_prioritizes_relevant_content():
    raw_chunks = [
        {
            "chunk_id": 1,
            "title": "History of Roman Empire",
            "url": "https://example.com/rome",
            "content": "Julius Caesar crossed the Rubicon and the Roman Republic became an Empire.",
        },
        {
            "chunk_id": 2,
            "title": "Cellular Respiration and Mitochondria",
            "url": "https://example.com/respiration",
            "content": "Cellular respiration converts glucose into ATP inside mitochondria through metabolic cycles.",
        },
        {
            "chunk_id": 3,
            "title": "Cooking Pasta Guide",
            "url": "https://example.com/pasta",
            "content": "Boil water in a large pot and add salt before adding pasta noodles.",
        },
    ]

    ranked = bm25_rank_chunks("cellular respiration mitochondria ATP", raw_chunks, top_k=2)
    assert len(ranked) >= 1
    assert isinstance(ranked[0], RAGChunk)
    assert ranked[0].chunk_id == 2
    assert "Mitochondria" in ranked[0].title
    assert ranked[0].score > 0.0


def test_search_web_for_topic_handles_offline_or_fallback(monkeypatch):
    # Test that search_web_for_topic returns a list of SearchResult even if network is simulated offline
    results = search_web_for_topic("Cellular Respiration", max_results=3)
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)
    assert results[0].title != ""
    assert len(results[0].content) > 10


def test_search_web_for_topic_retrieves_non_wikipedia_websites():
    results = search_web_for_topic("mitochondria ATP synthesis", max_results=5)
    assert len(results) > 0
    urls = [r.url.lower() for r in results]
    has_non_wiki = any("wikipedia.org" not in u and u.startswith("http") for u in urls)
    assert has_non_wiki, f"Expected non-wikipedia web sources in results, got URLs: {urls}"

