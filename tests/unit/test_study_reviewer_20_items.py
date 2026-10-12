"""Unit tests verifying that the study reviewer generates 20-30 practice items."""

from app.schemas.ai import ExtractedFileContent
from app.services.study_reviewer_service import (
    build_offline_fallback_study_materials,
    build_study_prompts,
)


def test_build_study_prompts_requests_20_to_30_questions():
    docs = [
        ExtractedFileContent(
            filename="biology_chapter4.pdf",
            file_type="PDF",
            content_type="application/pdf",
            character_count=1200,
            extracted_text="Cellular respiration glycolysis Krebs cycle ATP synthesis mitochondria electron transport chain.",
        )
    ]
    sys_prompt, user_prompt = build_study_prompts(
        prompt="Prepare comprehensive practice exam",
        intent="study_reviewer",
        documents=docs,
        topic="Cellular Respiration",
    )
    assert "20 to 30" in sys_prompt or "20 to 30" in user_prompt or "at least 20" in user_prompt


def test_fallback_generates_at_least_20_practice_items():
    docs = [
        ExtractedFileContent(
            filename="respiration.txt",
            file_type="TEXT",
            content_type="text/plain",
            character_count=500,
            extracted_text="Glycolysis converts glucose into pyruvate. Mitochondria generate ATP through oxidative phosphorylation.",
        )
    ]
    materials = build_offline_fallback_study_materials(
        prompt="Study exam",
        intent="study_reviewer",
        documents=docs,
        topic="Cellular Respiration",
    )

    total_questions = len(materials.quizzes) + len(materials.exam.questions)
    assert total_questions >= 20, f"Expected at least 20 total practice questions, got {total_questions}"


def test_fallback_questions_are_substantive_not_naive_cloze():
    docs = [
        ExtractedFileContent(
            filename="respiration.txt",
            file_type="TEXT",
            content_type="text/plain",
            character_count=500,
            extracted_text="Glycolysis converts glucose into pyruvate in the cytoplasm. Mitochondria generate ATP through oxidative phosphorylation across the inner membrane.",
        )
    ]
    materials = build_offline_fallback_study_materials(
        prompt="Study exam",
        intent="study_reviewer",
        documents=docs,
        topic="Cellular Respiration",
    )
    for q in materials.quizzes:
        assert "Which term completes this statement?" not in q.question, f"Found naive cloze: {q.question}"
        assert "_____" not in q.question, f"Found blank cloze: {q.question}"
        assert len(q.explanation) > 15, f"Explanation too short: {q.explanation}"

