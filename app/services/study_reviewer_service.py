"""Educational study prompt orchestration, intent classification, and deterministic fallback."""

import re
from typing import Literal

from app.schemas.ai import (
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

INTERROGATIVE_PATTERN = re.compile(
    r"^(what|how|why|when|where|who|which|can|could|is|are|do|does|did|will|would|explain|solve|calculate)\b",
    re.IGNORECASE,
)


def detect_prompt_intent(prompt: str) -> Literal["question", "study_reviewer"]:
    """Classify user intent between ad-hoc question vs study reviewer generation."""
    clean = prompt.strip()
    if not clean:
        return "study_reviewer"

    # Ends with question mark or starts with interrogative word
    if clean.endswith("?") or INTERROGATIVE_PATTERN.search(clean):
        return "question"

    return "study_reviewer"


def build_study_prompts(
    prompt: str,
    intent: Literal["question", "study_reviewer"],
    documents: list[ExtractedFileContent],
    notes_context: str | None = None,
    custom_system_prompt: str | None = None,
) -> tuple[str, str]:
    """Build grounded system and user prompts for educational study material generation."""
    system_prompt = (
        custom_system_prompt
        or (
            "You are an expert Educational Content Analyzer and Curriculum Study-Material Generator. "
            "Your objective is to generate accurate, high-yield, structured study materials grounded strictly "
            "in the uploaded source documents provided by the student or teacher.\n\n"
            "STRICT GROUNDING RULES:\n"
            "1. Ground every statement, definition, question, and answer in the uploaded source documents.\n"
            "2. Never hallucinate or invent unsupported facts.\n"
            "3. If a concept or formula is missing from the source text, explicitly list it in 'content_gaps' "
            "rather than inventing missing information.\n"
            "4. Return ONLY a valid, parseable JSON object matching the requested schema. No markdown code blocks, "
            "no conversational preamble, no closing text."
        )
    )

    doc_blocks: list[str] = []
    for idx, doc in enumerate(documents, 1):
        doc_blocks.append(
            f"=== SOURCE DOCUMENT {idx}: {doc.filename} (Type: {doc.file_type}, {doc.character_count} chars) ===\n"
            f"{doc.extracted_text.strip()}\n"
            f"=========================================================="
        )

    docs_section = "\n\n".join(doc_blocks) if doc_blocks else "[No attached documents provided]"
    notes_block = f"\n[ADDITIONAL CONTEXT / NOTES]:\n{notes_context.strip()}\n" if notes_context else ""

    instructions = (
        "TASK INSTRUCTIONS:\n"
        f"1. Target Topic / User Input: \"{prompt}\"\n"
        f"2. Detected Intent: \"{intent}\"\n"
    )
    if intent == "question":
        instructions += (
            "3. The user asked a specific question. In the JSON output, provide a direct, concise, and accurate "
            "answer in the 'direct_answer' field, and focus all accompanying reviewer notes, flashcards, and quizzes "
            "specifically around that question's subject.\n"
        )
    else:
        instructions += (
            "3. Provide a comprehensive study guide covering the main topic and all subtopics found in the source documents. "
            "Set 'direct_answer' to null.\n"
        )

    instructions += (
        "4. Output schema format:\n"
        "{\n"
        '  "intent": "' + intent + '",\n'
        '  "direct_answer": ' + ("\"<Direct Answer>\"" if intent == "question" else "null") + ",\n"
        '  "topic": "<Subject or Topic Name>",\n'
        '  "source_summary": "<Brief summary of uploaded documents>",\n'
        '  "reviewer": {\n'
        '    "title": "<Reviewer Title>",\n'
        '    "sections": [\n'
        '      {\n'
        '        "title": "<Section Title>",\n'
        '        "content": "<Detailed explanation>",\n'
        '        "key_points": ["<Key Point 1>", "<Key Point 2>"]\n'
        "      }\n"
        "    ]\n"
        "  },\n"
        '  "summary": { "content": "<Concise synthesis of central ideas>" },\n'
        '  "key_notes": [ { "topic": "<Topic>", "notes": ["<Note 1>", "<Note 2>"] } ],\n'
        '  "flashcards": [ { "question": "<Q>", "answer": "<A>", "topic": "<Topic>", "difficulty": "easy"|"medium"|"hard" } ],\n'
        '  "quizzes": [ { "type": "multiple_choice"|"true_false"|"identification"|"short_answer", "question": "<Q>", "options": ["A","B"], "correct_answer": "<Ans>", "explanation": "<Why>", "topic": "<Topic>", "difficulty": "medium" } ],\n'
        '  "exam": {\n'
        '    "title": "<Exam Title>",\n'
        '    "questions": [ { "type": "short_answer"|"multiple_choice", "question": "<Q>", "options": null, "correct_answer": "<Ans>", "explanation": "<Why>", "topic": "<Topic>", "difficulty": "hard", "points": 5 } ],\n'
        '    "total_questions": 1,\n'
        '    "total_points": 5\n'
        "  },\n"
        '  "source_coverage": {\n'
        '    "covered_topics": ["<Topic 1>", "<Topic 2>"],\n'
        '    "content_gaps": ["<Any missing source concept>"]\n'
        "  }\n"
        "}"
    )

    user_prompt = f"{docs_section}\n{notes_block}\n\n{instructions}"
    return system_prompt, user_prompt


def build_offline_fallback_study_materials(
    topic: str,
    intent: Literal["question", "study_reviewer"],
    documents: list[ExtractedFileContent],
    warning_msg: str,
) -> StudyMaterialsResponse:
    """Generate a deterministic, structured study materials tree from extracted document text."""
    # Concatenate text from documents
    all_text = " ".join(doc.extracted_text for doc in documents).strip()
    sentences = [s.strip() for s in re.split(r"[.\n]", all_text) if len(s.strip()) > 15]

    sample_summary = (
        ". ".join(sentences[:3]) + "."
        if sentences
        else f"Study materials derived from uploaded documents on {topic}."
    )

    first_fact = sentences[0] if sentences else f"Introduction to {topic}"
    second_fact = sentences[1] if len(sentences) > 1 else f"Core principles of {topic}"

    direct_ans = (
        f"Based on the source text: {first_fact}."
        if intent == "question"
        else None
    )

    return StudyMaterialsResponse(
        intent=intent,
        direct_answer=direct_ans,
        topic=topic,
        source_summary=f"Extracted content from {len(documents)} uploaded file(s).",
        reviewer=Reviewer(
            title=f"Reviewer: {topic}",
            sections=[
                ReviewerSection(
                    title=f"{topic} - Overview",
                    content=sample_summary,
                    key_points=[first_fact, second_fact],
                )
            ],
        ),
        summary=Summary(content=sample_summary),
        key_notes=[
            KeyNotesItem(
                topic=topic,
                notes=[first_fact, second_fact],
            )
        ],
        flashcards=[
            Flashcard(
                question=f"What is the key takeaway regarding {topic}?",
                answer=first_fact,
                topic=topic,
                difficulty="easy",
            )
        ],
        quizzes=[
            QuizQuestion(
                type="multiple_choice",
                question=f"Which fact regarding {topic} is supported by the document?",
                options=[first_fact, "Unsupported statement A", "Unsupported statement B"],
                correct_answer=first_fact,
                explanation="Directly referenced in the uploaded document text.",
                topic=topic,
                difficulty="medium",
            )
        ],
        exam=Exam(
            title=f"{topic} Examination",
            questions=[
                ExamQuestion(
                    type="short_answer",
                    question=f"Explain the primary concept of {topic} as described in the source.",
                    correct_answer=first_fact,
                    explanation="Synthesized from the uploaded lesson notes.",
                    topic=topic,
                    difficulty="hard",
                    points=5,
                )
            ],
            total_questions=1,
            total_points=5,
        ),
        source_coverage=SourceCoverage(
            covered_topics=[topic],
            content_gaps=[
                f"Note: {warning_msg}. Fallback structured study pack generated directly from document text."
            ],
        ),
    )
