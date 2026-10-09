"""Integration tests for Local AI and File Ingestion API endpoints."""

from fastapi.testclient import TestClient


def test_ai_generate_json_endpoint(client: TestClient) -> None:
    payload = {
        "prompt": "What are the core concepts of physics?",
        "text_context": "Chapter 1: Kinematics and Dynamics",
    }
    response = client.post("/api/v1/ai/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "model_used" in data
    assert "response_text" in data
    assert data["prompt"] == "What are the core concepts of physics?"


def test_ai_generate_with_files_multipart(client: TestClient) -> None:
    file_content = b"Biology Chapter 1: DNA structure and replication."
    files = [("files", ("dna_notes.txt", file_content, "text/plain"))]
    data = {"prompt": "Summarize the attached biology notes."}

    response = client.post("/api/v1/ai/generate-with-files", data=data, files=files)
    assert response.status_code == 200
    res = response.json()
    assert res["attached_files_count"] == 1
    assert res["ingested_files"][0]["filename"] == "dna_notes.txt"
    assert "DNA structure" in res["ingested_files"][0]["extracted_text"]


