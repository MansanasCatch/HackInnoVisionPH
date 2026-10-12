import json

import pytest
from pydantic import ValidationError

from app.core.exceptions import UnprocessableError
from app.schemas.ai import AIGenerateRequest, QuizQuestion
from app.services.generation_contract import generate_counted_materials, sample, valid_item


def package(start=0):
    return json.dumps(
        {
            "topic": "Biology",
            "source_summary": "Source facts",
            "reviewer": {"title": "Biology", "sections": []},
            "summary": {"content": "Biology overview"},
            "key_notes": [],
            "quizzes": [],
            "flashcards": [
                {"question": f"Explain concept {i}", "answer": f"Fact {i}", "topic": "Biology"}
                for i in range(start, start + 5)
            ],
            "exam": {"title": "Biology", "questions": []},
            "source_coverage": {},
        }
    )


@pytest.mark.parametrize("count", [10, 25, 50])
def test_exact_counts_and_bounded_batches(count):
    calls = []

    def call(system, prompt):
        calls.append((system, prompt))
        return package((len(calls) - 1) * 5)

    result = generate_counted_materials(
        request=AIGenerateRequest(item_count=count, material_types=["flashcards"]),
        topic="Biology",
        intent="study_reviewer",
        documents=[],
        call=call,
    )
    assert len(result.flashcards) == count
    assert len(calls) == count // 5
    assert not result.quizzes and not result.exam.questions
    assert "untrusted source data" in calls[0][0]


@pytest.mark.parametrize("raw", ["not JSON", package()])
def test_invalid_or_repeated_output_fails_without_padding(raw):
    with pytest.raises(UnprocessableError, match="no partial set was saved"):
        generate_counted_materials(
            request=AIGenerateRequest(material_types=["flashcards"]),
            topic="Biology",
            intent="study_reviewer",
            documents=[],
            call=lambda *_: raw,
        )


@pytest.mark.parametrize("count", [9, 51])
def test_count_range(count):
    with pytest.raises(ValidationError):
        AIGenerateRequest(item_count=count)


def test_multiple_choice_key_and_options():
    item = QuizQuestion(
        type="multiple_choice",
        question="Which?",
        options=["one", "two", "three", "four"],
        correct_answer="B",
        explanation="Source says two",
        topic="Numbers",
    )
    assert valid_item(item, "quizzes")
    assert item.correct_answer == "two"
    item.options = ["one", "one", "three", "four"]
    assert not valid_item(item, "quizzes")


def test_source_sampling_includes_end_and_middle():
    result = sample("a" * 1000 + "b" * 1000 + "c" * 1000, 600)
    assert "a" * 200 in result and "b" * 200 in result and "c" * 200 in result
    assert len(result) < 800


def test_offline_local_model_never_returns_fake_materials(monkeypatch):
    from app.services import local_ai_service

    class Repository:
        def get_latest_active_model(self):
            return "llama3.2:1b"

    monkeypatch.setattr(local_ai_service, "is_ollama_reachable", lambda: False)
    with pytest.raises(UnprocessableError, match="Local Ollama is unavailable"):
        local_ai_service.LocalAIService(Repository()).generate(
            AIGenerateRequest(topic="Biology", text_context="Cells have membranes.")
        )
