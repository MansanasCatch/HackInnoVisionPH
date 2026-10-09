"""Unit tests for educational prompt builder, intent classifier, and offline fallback."""

from app.schemas.ai import ExtractedFileContent, StudyMaterialsResponse
from app.services.study_reviewer_service import (
    build_offline_fallback_study_materials,
    build_study_prompts,
    detect_prompt_intent,
)


def test_detect_prompt_intent_question() -> None:
    assert detect_prompt_intent("What is the formula for kinetic energy?") == "question"
    assert detect_prompt_intent("Can you explain how mitosis works in page 2?") == "question"
    assert detect_prompt_intent("Why is water polar?") == "question"
    assert detect_prompt_intent("Solve equation 4?") == "question"


def test_detect_prompt_intent_study_reviewer() -> None:
    assert detect_prompt_intent("Reviewer for General Chemistry") == "study_reviewer"
    assert detect_prompt_intent("Thermodynamics Chapter 3") == "study_reviewer"
    assert detect_prompt_intent("Create flashcards and quiz for Biology") == "study_reviewer"


def test_build_study_prompts_structure() -> None:
    doc = ExtractedFileContent(
        filename="bio.txt",
        file_type="txt",
        content_type="text/plain",
        character_count=100,
        extracted_text="Mitochondria produces ATP through the citric acid cycle.",
    )
    system_prompt, user_prompt = build_study_prompts(
        prompt="Cellular Respiration",
        intent="study_reviewer",
        documents=[doc],
        notes_context="Midterm exam next week",
    )

    assert "educational content analyzer" in system_prompt.lower()
    assert "json" in system_prompt.lower()
    assert "Mitochondria produces ATP" in user_prompt
    assert "Midterm exam next week" in user_prompt
    assert "content_gaps" in user_prompt or "content_gaps" in system_prompt


def test_build_offline_fallback_study_materials() -> None:
    doc = ExtractedFileContent(
        filename="solar.txt",
        file_type="txt",
        content_type="text/plain",
        character_count=200,
        extracted_text=(
            "Solar Photovoltaics: Converts sunlight directly into electricity using semiconductors."
        ),
    )
    fallback = build_offline_fallback_study_materials(
        topic="Solar Energy",
        intent="study_reviewer",
        documents=[doc],
        warning_msg="Ollama offline",
    )

    assert isinstance(fallback, StudyMaterialsResponse)
    assert fallback.topic == "Solar Energy"
    assert len(fallback.reviewer.sections) > 0
    assert len(fallback.flashcards) > 0
    assert len(fallback.source_coverage.content_gaps) > 0
    assert "offline" in fallback.source_coverage.content_gaps[0].lower()


def test_synthesize_dynamic_exam_prompt_from_documents() -> None:
    from app.services.study_reviewer_service import synthesize_dynamic_exam_prompt

    doc1 = ExtractedFileContent(
        filename="Physics_Chapter_4_Mechanics.pdf",
        file_type="pdf",
        content_type="application/pdf",
        character_count=500,
        extracted_text=(
            "Chapter 4: Newton's Laws of Motion and Gravitational Force.\n"
            "An object in motion stays in motion unless acted upon by an external net force.\n"
            "Force equals mass times acceleration (F = ma)."
        ),
    )

    # Empty user prompt -> dynamic synthesis generates exam prompt based on doc contents
    prompt = synthesize_dynamic_exam_prompt(
        user_prompt="",
        documents=[doc1],
    )
    assert "Newton's Laws" in prompt or "Mechanics" in prompt
    assert "exam" in prompt.lower()

    # User already asked for an exam -> keeps/enriches context
    custom_prompt = synthesize_dynamic_exam_prompt(
        user_prompt="Provide a hard mock exam",
        documents=[doc1],
    )
    assert "Provide a hard mock exam" in custom_prompt
    assert "Newton's Laws" in custom_prompt or "Mechanics" in custom_prompt

