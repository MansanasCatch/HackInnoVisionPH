"""Unit tests for study reviewer schemas and enhanced response envelope."""

from app.schemas.ai import (
    AIGenerateResponse,
    Exam,
    ExamQuestion,
    ExtractedFileContent,
    Flashcard,
    KeyNotesItem,
    QuizQuestion,
    Reviewer,
    ReviewerSection,
    SourceCoverage,
    StudyMaterialsResponse,
    Summary,
)


def test_study_materials_response_serialization() -> None:
    data = {
        "intent": "study_reviewer",
        "direct_answer": None,
        "topic": "Newtonian Physics",
        "source_summary": "Lecture on motion and inertia.",
        "reviewer": {
            "title": "Comprehensive Physics Reviewer",
            "sections": [
                {
                    "title": "First Law of Motion",
                    "content": "An object at rest stays at rest unless acted upon by a net external force.",
                    "key_points": ["Inertia is mass-dependent", "F_net = 0 means a = 0"],
                }
            ],
        },
        "summary": {"content": "Summary of inertia and momentum."},
        "key_notes": [
            {"topic": "Inertia", "notes": ["Resistance to acceleration", "Directly proportional to mass"]}
        ],
        "flashcards": [
            {
                "question": "What is inertia?",
                "answer": "The tendency of an object to resist changes in its velocity.",
                "topic": "Inertia",
                "difficulty": "easy",
            }
        ],
        "quizzes": [
            {
                "type": "multiple_choice",
                "question": "What is the net force when acceleration is zero?",
                "options": ["0 N", "10 N", "9.8 N", "Unknown"],
                "correct_answer": "0 N",
                "explanation": "Newton's second law F=ma implies F=0 when a=0.",
                "topic": "First Law",
                "difficulty": "medium",
            }
        ],
        "exam": {
            "title": "Midterm Physics Examination",
            "questions": [
                {
                    "type": "short_answer",
                    "question": "State Newton's first law.",
                    "correct_answer": "An object maintains its state of rest or uniform motion unless acted upon by a force.",
                    "explanation": "Fundamental law of inertia.",
                    "topic": "Newton's Laws",
                    "difficulty": "hard",
                    "points": 5,
                }
            ],
            "total_questions": 1,
            "total_points": 5,
        },
        "source_coverage": {
            "covered_topics": ["First Law of Motion", "Inertia"],
            "content_gaps": ["Friction coefficients not covered in source"],
        },
    }

    model = StudyMaterialsResponse.model_validate(data)
    assert model.topic == "Newtonian Physics"
    assert len(model.reviewer.sections) == 1
    assert model.flashcards[0].difficulty == "easy"
    assert model.quizzes[0].options is not None
    assert model.exam.total_points == 5
    assert len(model.source_coverage.content_gaps) == 1


def test_enhanced_ai_generate_response_envelope() -> None:
    envelope = AIGenerateResponse(
        model_used="llama3.2:3b",
        response_text="Generated successfully",
        prompt="Reviewer for Physics",
        attached_files_count=1,
        ingested_files=[
            ExtractedFileContent(
                filename="physics.txt",
                file_type="txt",
                content_type="text/plain",
                character_count=150,
                extracted_text="Sample physics text",
            )
        ],
        is_ollama_online=True,
        execution_time_seconds=2.45,
        study_materials=None,
        warnings=["⚠️ Model nearing context window"],
    )

    dumped = envelope.model_dump()
    assert dumped["model_used"] == "llama3.2:3b"
    assert dumped["warnings"] == ["⚠️ Model nearing context window"]
    assert dumped["study_materials"] is None
