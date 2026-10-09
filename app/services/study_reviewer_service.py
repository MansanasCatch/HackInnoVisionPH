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


def infer_topic_from_documents(
    topic: str | None,
    documents: list[ExtractedFileContent],
    fallback_title: str = "General Studies",
) -> str:
    """Derive topic from user input topic, prompt, document header, or filename."""
    if topic and topic.strip():
        return topic.strip()

    # If fallback_title was passed (e.g. from prompt) and isn't generic
    if fallback_title and fallback_title.strip() and fallback_title != "General Studies":
        return fallback_title.strip()

    if not documents:
        return fallback_title

    first_doc = documents[0]
    # Check document header lines first
    for line in first_doc.extracted_text.splitlines():
        line_str = line.strip()
        # Strip trailing colon from section headers if present
        if line_str and 3 <= len(line_str) <= 60 and not line_str.startswith("="):
            return line_str.rstrip(":")

    # Fall back to filename
    cleaned_name = re.sub(r"\.[a-zA-Z0-9]+$", "", first_doc.filename)
    cleaned_name = re.sub(r"[_\-]+", " ", cleaned_name).strip()
    if cleaned_name and len(cleaned_name) >= 3:
        return cleaned_name.title()

    return fallback_title


def synthesize_dynamic_exam_prompt(
    user_prompt: str,
    documents: list[ExtractedFileContent],
    topic: str | None = None,
) -> str:
    """Dynamically craft an exam reviewer prompt grounded in uploaded document contents."""
    derived_topic = infer_topic_from_documents(topic, documents)
    clean_prompt = user_prompt.strip() if user_prompt else ""

    doc_titles = [doc.filename for doc in documents] if documents else ["provided materials"]
    doc_summary = ", ".join(doc_titles[:3])

    if not clean_prompt:
        return (
            f"Generate a rigorous exam and comprehensive study reviewer on '{derived_topic}' "
            f"derived strictly from the uploaded document(s): {doc_summary}. "
            "Ensure the exam contains multiple choice and short answer questions "
            "with points and explanations."
        )

    # If the user provided a topic or custom request, combine it dynamically
    if derived_topic.lower() not in clean_prompt.lower():
        return (
            f"{clean_prompt} for '{derived_topic}', based strictly on the uploaded source "
            f"materials ({doc_summary})."
        )

    return clean_prompt


def build_study_prompts(
    prompt: str,
    intent: Literal["question", "study_reviewer"],
    documents: list[ExtractedFileContent],
    topic: str | None = None,
    notes_context: str | None = None,
    custom_system_prompt: str | None = None,
) -> tuple[str, str]:
    """Build grounded system and user prompts for educational study material generation."""
    system_prompt = custom_system_prompt or (
        "You are an expert Educational Content Analyzer and Curriculum Study-Material Generator. "
        "Your objective is to generate accurate, high-yield, structured study materials grounded "
        "strictly in the uploaded source documents provided by the student or teacher.\n\n"
        "STRICT GROUNDING RULES:\n"
        "1. Ground every statement, definition, question, and answer in the "
        "uploaded source documents.\n"
        "2. Never hallucinate or invent unsupported facts.\n"
        "3. If a concept or formula is missing from the source text, explicitly list it in "
        "'content_gaps' rather than inventing missing information.\n"
        "4. Return ONLY a valid, parseable JSON object matching the requested schema. "
        "No markdown code blocks, no conversational preamble, no closing text."
    )

    doc_blocks: list[str] = []
    for idx, doc in enumerate(documents, 1):
        header = (
            f"=== SOURCE DOCUMENT {idx}: {doc.filename} "
            f"(Type: {doc.file_type}, {doc.character_count} chars) ==="
        )
        doc_blocks.append(
            f"{header}\n"
            f"{doc.extracted_text.strip()}\n"
            "=========================================================="
        )

    docs_section = "\n\n".join(doc_blocks) if doc_blocks else "[No attached documents provided]"
    notes_block = (
        f"\n[ADDITIONAL CONTEXT / NOTES]:\n{notes_context.strip()}\n" if notes_context else ""
    )

    resolved_topic = infer_topic_from_documents(
        topic, documents, fallback_title=prompt or "General Studies"
    )
    instructions = (
        "TASK INSTRUCTIONS:\n"
        f'1. Target Topic / Curriculum Subject: "{resolved_topic}"\n'
        f'2. User Request / Objective: "{prompt}"\n'
        f'3. Detected Intent: "{intent}"\n'
    )
    if intent == "question":
        instructions += (
            "4. The user asked a specific question. In the JSON output, provide a direct, concise, "
            "and accurate answer in the 'direct_answer' field, and focus all accompanying reviewer "
            "notes, flashcards, quizzes, and exam specifically around that question's subject.\n"
        )
    else:
        instructions += (
            "4. Provide a comprehensive study guide and rigorous mock exam covering the main topic "
            "and all subtopics found in the source documents. Set 'direct_answer' to null.\n"
            "5. Ensure the 'exam' section provides challenging questions (multiple choice and "
            "short answer/essay) with full point values, correct answers, and thorough "
            "pedagogical explanations.\n"
        )

    ans_placeholder = '"<Direct Answer>"' if intent == "question" else "null"
    instructions += (
        "4. Output schema format:\n"
        "{\n"
        f'  "intent": "{intent}",\n'
        f'  "direct_answer": {ans_placeholder},\n'
        '  "topic": "<Subject or Topic Name>",\n'
        '  "source_summary": "<Brief summary of uploaded documents>",\n'
        '  "reviewer": {\n'
        '    "title": "<Reviewer Title>",\n'
        '    "sections": [\n'
        "      {\n"
        '        "title": "<Section Title>",\n'
        '        "content": "<Detailed explanation>",\n'
        '        "key_points": ["<Key Point 1>", "<Key Point 2>"]\n'
        "      }\n"
        "    ]\n"
        "  },\n"
        '  "summary": { "content": "<Concise synthesis of central ideas>" },\n'
        '  "key_notes": [ { "topic": "<Topic>", "notes": ["<Note 1>", "<Note 2>"] } ],\n'
        '  "flashcards": [ { "question": "<Q>", "answer": "<A>", "topic": "<Topic>", '
        '"difficulty": "easy"|"medium"|"hard" } ],\n'
        '  "quizzes": [ { "type": "multiple_choice"|"true_false"|"identification", '
        '"question": "<Q>", "options": ["A","B"], "correct_answer": "<Ans>", '
        '"explanation": "<Why>", "topic": "<Topic>", "difficulty": "medium" } ],\n'
        '  "exam": {\n'
        '    "title": "<Exam Title>",\n'
        '    "questions": [ { "type": "short_answer"|"multiple_choice", "question": "<Q>", '
        '"options": null, "correct_answer": "<Ans>", "explanation": "<Why>", '
        '"topic": "<Topic>", "difficulty": "hard", "points": 5 } ],\n'
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
    topic: str | None,
    intent: Literal["question", "study_reviewer"],
    documents: list[ExtractedFileContent],
    warning_msg: str,
) -> StudyMaterialsResponse:
    """Generate a deterministic, structured study materials tree from extracted document text."""
    resolved_topic = infer_topic_from_documents(topic, documents)

    # Concatenate text from documents
    all_text = " ".join(doc.extracted_text for doc in documents).strip()
    sentences = [s.strip() for s in re.split(r"[.\n]", all_text) if len(s.strip()) > 15]

    sample_summary = (
        ". ".join(sentences[:3]) + "."
        if sentences
        else f"Study materials derived from uploaded documents on {resolved_topic}."
    )

    first_fact = sentences[0] if sentences else f"Introduction to {resolved_topic}"
    second_fact = sentences[1] if len(sentences) > 1 else f"Core principles of {resolved_topic}"

    direct_ans = f"Based on the source text: {first_fact}." if intent == "question" else None

    return StudyMaterialsResponse(
        intent=intent,
        direct_answer=direct_ans,
        topic=resolved_topic,
        source_summary=f"Extracted content from {len(documents)} uploaded file(s).",
        reviewer=Reviewer(
            title=f"Reviewer: {resolved_topic}",
            sections=[
                ReviewerSection(
                    title=f"{resolved_topic} - Overview",
                    content=sample_summary,
                    key_points=[first_fact, second_fact],
                )
            ],
        ),
        summary=Summary(content=sample_summary),
        key_notes=[
            KeyNotesItem(
                topic=resolved_topic,
                notes=[first_fact, second_fact],
            )
        ],
        flashcards=[
            Flashcard(
                question=f"What is the key takeaway regarding {resolved_topic}?",
                answer=first_fact,
                topic=resolved_topic,
                difficulty="easy",
            )
        ],
        quizzes=[
            QuizQuestion(
                type="multiple_choice",
                question=f"Which fact regarding {resolved_topic} is supported by the document?",
                options=[first_fact, "Unsupported statement A", "Unsupported statement B"],
                correct_answer=first_fact,
                explanation="Directly referenced in the uploaded document text.",
                topic=resolved_topic,
                difficulty="medium",
            )
        ],
        exam=Exam(
            title=f"{resolved_topic} Examination",
            questions=[
                ExamQuestion(
                    type="short_answer",
                    question=(
                        f"Explain the primary concept of '{resolved_topic}' "
                        "described in the source."
                    ),
                    correct_answer=first_fact,
                    explanation="Synthesized from the uploaded lesson notes.",
                    topic=resolved_topic,
                    difficulty="hard",
                    points=5,
                )
            ],
            total_questions=1,
            total_points=5,
        ),
        source_coverage=SourceCoverage(
            covered_topics=[resolved_topic],
            content_gaps=[
                f"Note: {warning_msg}. Fallback structured study pack generated "
                "directly from document text."
            ],
        ),
    )
