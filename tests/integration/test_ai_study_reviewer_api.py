"""Integration tests for AI Study Reviewer Generation API."""

import io

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw


def _create_test_image(text: str) -> bytes:
    img = Image.new("RGB", (300, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((10, 30), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_generate_study_reviewer_with_text_file(client: TestClient) -> None:
    content = (
        b"Thermodynamics Lecture 1:\n"
        b"First Law of Thermodynamics: Energy cannot be created or destroyed, only transformed.\n"
        b"Second Law of Thermodynamics: The entropy of an isolated system always increases.\n"
        b"Heat and Work: Energy transfer mechanisms across system boundaries.\n"
    )
    files = [("files", ("thermo.txt", content, "text/plain"))]
    form_data = {"prompt": "Thermodynamics Chapter 1"}

    response = client.post("/api/v1/ai/generate-with-files", data=form_data, files=files)
    assert response.status_code == 200
    res = response.json()

    assert res["model_used"] is not None
    assert res["attached_files_count"] == 1
    assert "study_materials" in res
    assert res["study_materials"] is not None

    materials = res["study_materials"]
    assert materials["intent"] == "study_reviewer"
    assert "Thermodynamics" in materials["topic"]
    assert len(materials["reviewer"]["sections"]) > 0
    assert len(materials["flashcards"]) > 0
    assert len(materials["quizzes"]) > 0
    assert materials["exam"]["total_points"] > 0
    assert "source_coverage" in materials


def test_generate_with_adhoc_question_intent(client: TestClient) -> None:
    content = b"Photosynthesis occurs in the chloroplasts. Light reactions produce ATP and NADPH."
    files = [("files", ("botany.txt", content, "text/plain"))]
    form_data = {"prompt": "Where does photosynthesis occur in plant cells?"}

    response = client.post("/api/v1/ai/generate-with-files", data=form_data, files=files)
    assert response.status_code == 200
    res = response.json()

    materials = res.get("study_materials")
    assert materials is not None
    assert materials["intent"] == "question"
    assert materials["direct_answer"] is not None
    assert "chloroplast" in materials["direct_answer"].lower()


def test_generate_study_reviewer_with_image_ocr(client: TestClient) -> None:
    img_bytes = _create_test_image("Newtonian Gravity F=G(m1*m2)/r^2")
    files = [("files", ("gravity_slide.png", img_bytes, "image/png"))]
    form_data = {"prompt": "Gravitation"}

    response = client.post("/api/v1/ai/generate-with-files", data=form_data, files=files)
    assert response.status_code == 200
    res = response.json()

    assert res["attached_files_count"] == 1
    assert res["ingested_files"][0]["file_type"] == "image"
    assert res["study_materials"] is not None
    assert "warnings" in res


def test_generate_exam_with_dynamic_topic_and_empty_prompt(client: TestClient) -> None:
    content = (
        b"Cell Division and Mitosis:\n"
        b"Prophase: Chromosomes condense and spindle fibers form.\n"
        b"Metaphase: Chromosomes align along the equatorial metaphase plate.\n"
        b"Anaphase: Sister chromatids separate and move toward opposite poles.\n"
        b"Telophase: Nuclear envelopes reform around the separated chromatids.\n"
    )
    files = [("files", ("Cell_Division_Notes.txt", content, "text/plain"))]
    # Simulating UI input: user entered topic="Cell Division", prompt is empty/not passed
    form_data = {"topic": "Cell division", "prompt": ""}

    response = client.post("/api/v1/ai/generate-with-files", data=form_data, files=files)
    assert response.status_code == 200
    res = response.json()

    materials = res.get("study_materials")
    assert materials is not None
    assert "Cell division" in materials["topic"]
    assert materials["exam"]["total_questions"] >= 1
    assert materials["exam"]["total_points"] > 0
    assert "Cell division" in materials["exam"]["title"]

