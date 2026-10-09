"""Unit tests for JSON sanitizer, repair, and Pydantic validator."""

import json

from app.schemas.ai import StudyMaterialsResponse
from app.services.json_repair_service import clean_and_parse_study_json

SAMPLE_VALID_STUDY_DICT = {
    "intent": "study_reviewer",
    "direct_answer": None,
    "topic": "Cell Biology",
    "source_summary": "Notes on cellular respiration and organelles.",
    "reviewer": {
        "title": "Cell Biology Reviewer",
        "sections": [
            {
                "title": "Mitochondria",
                "content": "Powerhouse of the cell generating ATP through respiration.",
                "key_points": ["Double membrane", "ATP synthesis"],
            }
        ],
    },
    "summary": {"content": "Overview of organelles and ATP synthesis."},
    "key_notes": [{"topic": "ATP", "notes": ["Cellular energy currency"]}],
    "flashcards": [
        {
            "question": "What is the primary function of mitochondria?",
            "answer": "Generate ATP for cellular activities.",
            "topic": "Organelles",
            "difficulty": "easy",
        }
    ],
    "quizzes": [
        {
            "type": "multiple_choice",
            "question": "Which molecule is the main energy currency of the cell?",
            "options": ["ATP", "DNA", "RNA", "Lipid"],
            "correct_answer": "ATP",
            "explanation": "ATP stores readily releasable energy.",
            "topic": "Energy",
            "difficulty": "easy",
        }
    ],
    "exam": {
        "title": "Cell Biology Final Exam",
        "questions": [
            {
                "type": "short_answer",
                "question": "Explain the role of ATP synthase.",
                "correct_answer": "Enzyme that synthesizes ATP using proton gradient.",
                "explanation": "Located in inner mitochondrial membrane.",
                "topic": "Bioenergetics",
                "difficulty": "hard",
                "points": 5,
            }
        ],
        "total_questions": 1,
        "total_points": 5,
    },
    "source_coverage": {
        "covered_topics": ["Mitochondria", "ATP"],
        "content_gaps": ["Chloroplasts not discussed in source"],
    },
}


def test_clean_and_parse_pure_json() -> None:
    import json

    raw = json.dumps(SAMPLE_VALID_STUDY_DICT)
    result = clean_and_parse_study_json(raw)
    assert result is not None
    assert isinstance(result, StudyMaterialsResponse)
    assert result.topic == "Cell Biology"


def test_clean_and_parse_markdown_fenced_json() -> None:
    dumped = json.dumps(SAMPLE_VALID_STUDY_DICT)
    raw = f"Here is the study material:\n```json\n{dumped}\n```\nHope this helps!"
    result = clean_and_parse_study_json(raw)
    assert result is not None
    assert result.topic == "Cell Biology"


def test_clean_and_parse_with_trailing_commas() -> None:
    # Introduce trailing commas
    raw = """
    ```json
    {
      "intent": "study_reviewer",
      "direct_answer": null,
      "topic": "Cell Biology",
      "source_summary": "Notes.",
      "reviewer": {
        "title": "Reviewer",
        "sections": [
          {
            "title": "Mitochondria",
            "content": "Generates ATP.",
            "key_points": ["ATP",],
          },
        ]
      },
      "summary": { "content": "Summary." },
      "key_notes": [ { "topic": "ATP", "notes": ["Energy",] }, ],
      "flashcards": [],
      "quizzes": [],
      "exam": {
        "title": "Exam",
        "questions": [],
        "total_questions": 0,
        "total_points": 0,
      },
      "source_coverage": { "covered_topics": [], "content_gaps": [], }
    }
    ```
    """
    result = clean_and_parse_study_json(raw)
    assert result is not None
    assert result.topic == "Cell Biology"


def test_clean_and_parse_invalid_garbage_returns_none() -> None:
    raw = "This is pure text with no JSON at all. Error 404."
    result = clean_and_parse_study_json(raw)
    assert result is None
