"""Integration tests for Local AI and File Ingestion API endpoints."""

import io

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject


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


def _create_sample_pdf_bytes(text: str = "Cell division and Mitosis") -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 100 700 Td ({text}) Tj ET".encode("latin1"))
    font_obj = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"),
        NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    font_ref = writer._add_object(font_obj)
    page[NameObject("/Resources")] = DictionaryObject({
        NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})
    })
    page[NameObject("/Contents")] = writer._add_object(stream)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extract_text_from_pdf_returns_json(client: TestClient) -> None:
    pdf_bytes = _create_sample_pdf_bytes("Cell division and Mitosis")
    files = [("files", ("mitosis_notes.pdf", pdf_bytes, "application/pdf"))]
    response = client.post("/api/v1/ai/extract-text", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_files"] == 1
    assert len(data["files"]) == 1
    file_info = data["files"][0]
    assert file_info["filename"] == "mitosis_notes.pdf"
    assert file_info["file_type"] == "pdf"
    assert file_info["content_type"] == "application/pdf"
    assert "Cell division and Mitosis" in file_info["extracted_text"]
    assert file_info["character_count"] > 0


def test_extract_text_empty_files_returns_400(client: TestClient) -> None:
    response = client.post("/api/v1/ai/extract-text", files=[])
    assert response.status_code == 400

