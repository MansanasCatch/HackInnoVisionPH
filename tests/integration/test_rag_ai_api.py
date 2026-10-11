"""Integration tests for the Web Search & RAG retrieval endpoint."""

from fastapi.testclient import TestClient
import pytest

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_search_and_retrieve_endpoint_success(client):
    response = client.post(
        "/api/v1/ai/search-and-retrieve",
        json={
            "topic": "Cellular Respiration",
            "max_results": 3,
            "top_k_chunks": 4,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query"] == "Cellular Respiration"
    assert "source_engine" in data
    assert isinstance(data["retrieved_chunks"], list)
    assert len(data["retrieved_chunks"]) > 0
    assert "aggregated_context" in data
    assert len(data["aggregated_context"]) > 20


def test_search_and_retrieve_empty_topic_returns_400(client):
    response = client.post(
        "/api/v1/ai/search-and-retrieve",
        json={"topic": "   "},
    )
    assert response.status_code == 400
