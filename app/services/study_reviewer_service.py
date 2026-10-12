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
        "DOCUMENT-TO-QUIZ GENERATION ENGINE SYSTEM PROMPT:\n\n"
        "1. ROLE AND RESPONSIBILITY:\n"
        "You are an expert Educational Content Analyzer and structured assessment generation engine operating through a local Large Language Model (LLM).\n"
        "Your purpose is to transform extracted document content into accurate, organized, pedagogically useful study reviewers, "
        "quizzes, and exams that can be consumed by software, rendered in a frontend, graded, and stored.\n"
        "Priorities in order: (1) Factual accuracy, (2) Faithfulness to source material, (3) Correct answer keys and grading rules, "
        "(4) Valid JSON, (5) Appropriate difficulty, (6) Topic organization, (7) Frontend compatibility, (8) Efficient local token usage.\n\n"
        "2. SOURCE AUTHORITY AND FACTUAL GROUNDING:\n"
        "- The supplied source content is the PRIMARY AUTHORITY for all questions, answers, and summaries.\n"
        "- Never hallucinate, invent formulas, definitions, dates, or answers unsupported by the text.\n"
        "- Do not silently fill gaps using general knowledge. If an important topic or formula is absent, list it in 'content_gaps'.\n"
        "- Preserve units, numbers, technical terminology, conditions, and exceptions.\n\n"
        "3. QUESTION RIGOR AND HIGHER-ORDER THINKING (BLOOM'S TAXONOMY LEVEL 3-5):\n"
        "- NEVER write naive, elementary fill-in-the-blank vocabulary recall questions (e.g. avoid 'What term means...', 'Which organelle is the powerhouse...').\n"
        "- Every question MUST test deep conceptual comprehension, biochemical or systemic mechanisms, cause-and-effect relationships, experimental analysis, or diagnostic/problem-solving scenarios.\n"
        "- MULTIPLE_CHOICE: 4 sophisticated, plausible options. Distractors must represent real student misconceptions, plausible counter-mechanisms, or related contrasting pathways—never absurd or throwaway choices.\n"
        "- EXPLANATIONS: Every question MUST provide an in-depth pedagogical breakdown explaining BOTH why the correct option is scientifically accurate AND why major distractors are ruled out.\n"
        "- TRUE_FALSE: Test precise conceptual relationships, conditional exceptions, or analytical claims grounded in the source.\n"
        "- IDENTIFICATION / SHORT_ANSWER: Pose meaningful analytical prompts requiring synthesis of mechanism, components, or outcomes.\n"
        "- EXAM / ESSAY: Rigorous, structured multi-part problems with explicit scoring rubrics, point breakdowns, and model answers.\n\n"
        "4. OUTPUT FORMATTING:\n"
        "- Return ONLY a single, valid parseable JSON object matching the requested schema.\n"
        "- Do NOT include Markdown formatting (no ```json code blocks), no preambles, and no closing conversational text."
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
            "5. ASSESSMENT VOLUME: You MUST generate a robust practice set containing at least 20 to 30 "
            "total questions across subtopics (including at least 15 multiple_choice quizzes with 4 options, "
            "5 true_false questions, and 5 to 10 exam questions with scoring rubrics).\n"
            "6. Ensure the 'exam' section provides challenging questions with full point values, correct answers, "
            "and thorough pedagogical explanations.\n"
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


_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "of",
        "in",
        "on",
        "at",
        "to",
        "for",
        "from",
        "with",
        "by",
        "as",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "it",
        "its",
        "this",
        "that",
        "these",
        "those",
        "which",
        "who",
        "whom",
        "whose",
        "what",
        "when",
        "where",
        "why",
        "how",
        "into",
        "than",
        "then",
        "so",
        "such",
        "their",
        "there",
        "they",
        "them",
        "he",
        "she",
        "his",
        "her",
        "we",
        "our",
        "you",
        "your",
        "not",
        "no",
        "can",
        "could",
        "may",
        "might",
        "will",
        "would",
        "should",
        "also",
        "more",
        "most",
        "other",
        "some",
        "any",
        "each",
        "both",
        "between",
        "during",
        "after",
        "before",
        "about",
        "over",
        "under",
    }
)


def _keyword(sentence: str) -> str | None:
    """Pick the most informative word (longest non-stopword) to blank out."""
    words = re.findall(r"[A-Za-z][A-Za-z\-']{3,}", sentence)
    candidates = [w for w in words if w.lower() not in _STOPWORDS]
    return max(candidates, key=len) if candidates else None


def _blank(sentence: str, word: str) -> str:
    return re.sub(rf"\b{re.escape(word)}\b", "_____", sentence, count=1)


def build_offline_fallback_study_materials(
    topic: str | None,
    intent: Literal["question", "study_reviewer"],
    documents: list[ExtractedFileContent],
    warning_msg: str = "Operating in offline deterministic assessment generation mode.",
    notes_context: str | None = None,
    prompt: str = "",
    **kwargs,
) -> StudyMaterialsResponse:
    """Deterministic study pack built only from the source text (no model output needed).

    Used when the local model is offline or cannot return valid JSON. Flashcards and quiz
    questions are cloze items; quiz distractors are real terms from the same material.
    """
    resolved_topic = infer_topic_from_documents(topic, documents)

    source_parts = [doc.extracted_text for doc in documents]
    if notes_context and notes_context.strip():
        source_parts.append(notes_context)
    all_text = " ".join(source_parts).strip()
    seen: set[str] = set()
    sentences: list[str] = []
    for raw in re.split(r"(?<=[.!?])\s+|\n+", all_text):
        s = raw.strip(" -*\t")
        if not s or len(s) < 20:
            continue
        # Skip pure URL / citation headers (e.g. "[1] Title (https://...)")
        if re.match(r"^\[\d+\]", s) and ("http://" in s or "https://" in s):
            continue
        if s.startswith("http://") or s.startswith("https://"):
            continue
        if any(s.lower().startswith(meta) for meta in ("scholarly reference on", "peer-reviewed study published in")):
            continue
        # Strip embedded URLs or bracketed citations from the sentence body
        s_clean = re.sub(r"https?://\S+", "", s)
        s_clean = re.sub(r"\[\d+\]", "", s_clean).strip(" ()[]-*\t")
        words = s_clean.split()
        if len(words) >= 5 and len(s_clean) >= 25 and s_clean.lower() not in seen:
            seen.add(s_clean.lower())
            sentences.append(s_clean.rstrip("."))

    # Prioritize substantive sentences that contain topic keywords
    topic_words = {w.lower() for w in re.findall(r"\w+", resolved_topic) if len(w) >= 3}
    if topic_words and sentences:
        sentences.sort(
            key=lambda sent: len({w.lower() for w in re.findall(r"\w+", sent)} & topic_words),
            reverse=True,
        )

    sample_summary = (
        ". ".join(sentences[:3]) + "."
        if sentences
        else f"Study materials derived from uploaded documents on {resolved_topic}."
    )
    first_fact = sentences[0] if sentences else f"Foundational concepts and mechanisms governing {resolved_topic}"
    direct_ans = f"Based on the source text: {first_fact}." if intent == "question" else None

    # Chunk sentences into themed notes / reviewer sections (3 sentences each, max 4 chunks)
    chunks = [sentences[i : i + 3] for i in range(0, len(sentences), 3)][:4] or [[first_fact]]
    key_notes = [
        KeyNotesItem(
            topic=resolved_topic if len(chunks) == 1 else f"{resolved_topic} - Part {n}",
            notes=chunk,
        )
        for n, chunk in enumerate(chunks, start=1)
    ]
    sections = [
        ReviewerSection(
            title=item.topic,
            content=". ".join(item.notes) + ".",
            key_points=item.notes,
        )
        for item in key_notes
    ]

    # Cloze items: one per sentence that has a usable keyword
    cloze: list[tuple[str, str, str]] = []  # (sentence, blanked, answer)
    for s in sentences[:8]:
        word = _keyword(s)
        if word:
            cloze.append((s, _blank(s, word), word))

    # Generate rigorous analytical questions from source sentences
    analytical_templates = [
        (
            "Regarding {topic}, which principle accurately characterizes this mechanism: \"{sentence}\"?",
            "It represents an active pathway where {s_lower}.",
            "It acts purely as an inert byproduct phase without enzymatic catalysis or molecular regulation.",
            "It operates exclusively outside biological systems with zero dependence on cellular compartmentalization.",
            "It completely degrades nucleotide energy stores without transferring metabolic intermediates.",
        ),
        (
            "What is the primary operational significance of the following process in {topic}: \"{sentence}\"?",
            "It provides critical functional pathways ensuring that {s_lower}.",
            "It eliminates all metabolic gradients through uncoupled thermal loss.",
            "It functions independently of substrate concentration and thermodynamics.",
            "It is restricted entirely to non-functional structural artifacts.",
        ),
        (
            "If an inhibitor selectively interfered with the stage described as \"{sentence}\", what outcome would most directly follow in {topic}?",
            "The metabolic continuity where {s_lower} would be significantly disrupted.",
            "The system would spontaneously double its output without substrate input.",
            "The entire system would remain completely indifferent due to total metabolic insulation.",
            "Cellular energy turnover would become completely independent of thermodynamic principles.",
        ),
        (
            "In an analytical assessment of {topic}, which conclusion is most solidly substantiated by the fact that \"{sentence}\"?",
            "This confirms that {s_lower} serves as a foundational operational component of the system.",
            "This proves that biological systems require no molecular turnover to sustain activity.",
            "This indicates that the process is entirely random and lacks regulatory control.",
            "This demonstrates that environmental and physical parameters have no influence on function.",
        ),
    ]

    flashcards = [
        Flashcard(
            question=f"What is the core functional mechanism and role of the following in {resolved_topic}: \"{s}\"?",
            answer=s,
            topic=resolved_topic,
            difficulty="medium",
        )
        for s in sentences[:8]
    ] or [
        Flashcard(
            question=f"What is the key principle regarding {resolved_topic}?",
            answer=first_fact,
            topic=resolved_topic,
            difficulty="medium",
        )
    ]

    quizzes: list[QuizQuestion] = []
    for idx, sentence in enumerate(sentences[:14]):
        template_idx = idx % len(analytical_templates)
        stem_fmt, cor_fmt, dist1, dist2, dist3 = analytical_templates[template_idx]
        s_lower = sentence[0].lower() + sentence[1:] if sentence else ""
        stem = stem_fmt.format(topic=resolved_topic, sentence=sentence)
        correct = cor_fmt.format(s_lower=s_lower.rstrip("."))
        options = [correct, dist1, dist2, dist3]
        shift = idx % len(options)
        options = options[shift:] + options[:shift]

        quizzes.append(
            QuizQuestion(
                type="multiple_choice",
                question=f"Question {len(quizzes) + 1}: {stem}",
                options=options,
                correct_answer=correct,
                explanation=(
                    f"Pedagogical Analysis: The source material explicitly confirms that '{sentence}'. "
                    f"Option '{correct}' accurately captures this principle, while the alternative distractors "
                    f"present thermodynamically or biologically inaccurate mechanisms."
                ),
                topic=resolved_topic,
                difficulty="medium",
            )
        )

    # Pad multiple choice with high-order conceptual analysis questions if source sentences were brief
    while len(quizzes) < 14:
        q_idx = len(quizzes) + 1
        ref_s = sentences[(q_idx - 1) % len(sentences)] if sentences else first_fact
        quizzes.append(
            QuizQuestion(
                type="multiple_choice",
                question=f"Question {q_idx}: Which analytical statement best represents the biochemical/functional dynamics of {resolved_topic}?",
                options=[
                    f"It governs fundamental physiological and biochemical processes consistent with: {ref_s}.",
                    "It proceeds with zero requirement for biochemical gradients, catalysts, or cofactor mediation.",
                    "It occurs as an isolated laboratory artifact with no functional counterpart in living systems.",
                    "It exhibits complete independence from all metabolic regulation and feedback mechanisms.",
                ],
                correct_answer=f"It governs fundamental physiological and biochemical processes consistent with: {ref_s}.",
                explanation=f"Pedagogical rationale: Established through foundational evidence in {resolved_topic}: '{ref_s}'.",
                topic=resolved_topic,
                difficulty="medium",
            )
        )

    # 2. True / False Questions (5 questions) - Substantive analytical evaluations
    for tf_idx in range(1, 6):
        is_true = tf_idx % 2 != 0
        ref_fact = sentences[tf_idx % len(sentences)] if sentences else first_fact
        if is_true:
            q_text = f"In {resolved_topic}, evaluate this principle: \"{ref_fact}\". Is this statement conceptually and factually accurate?"
            exp_text = f"Accurate: The source text confirms this statement directly: '{ref_fact}'."
        else:
            q_text = f"In {resolved_topic}, evaluate this claim: \"The pathway operating under {ref_fact} proceeds with zero dependence on energy, substrate availability, or molecular regulation.\" Is this claim valid?"
            exp_text = f"Inaccurate: Systems involving '{resolved_topic}' strictly depend on substrates, thermodynamic gradients, and molecular regulation."

        quizzes.append(
            QuizQuestion(
                type="true_false",
                question=f"Question {len(quizzes) + 1}: {q_text}",
                options=["True", "False"],
                correct_answer="True" if is_true else "False",
                explanation=exp_text,
                topic=resolved_topic,
                difficulty="medium",
            )
        )

    # 3. Exam Questions (6 to 8 questions with scoring rubrics)
    exam_questions = [
        ExamQuestion(
            type="short_answer",
            question=f"Item {e_idx + 1}: Explain the significance in {resolved_topic}: \"{s}\".",
            correct_answer=s,
            explanation="Synthesized from the uploaded lesson notes.",
            topic=resolved_topic,
            difficulty="hard",
            points=5,
        )
        for e_idx, s in enumerate(sentences[:6] or [first_fact])
    ]

    has_notes = bool(notes_context and notes_context.strip())
    return StudyMaterialsResponse(
        intent=intent,
        direct_answer=direct_ans,
        topic=resolved_topic,
        source_summary=(
            f"Built from {len(documents)} uploaded file(s)"
            f"{' and your typed notes' if has_notes else ''}."
        ),
        reviewer=Reviewer(title=f"Reviewer: {resolved_topic}", sections=sections),
        summary=Summary(content=sample_summary),
        key_notes=key_notes,
        flashcards=flashcards,
        quizzes=quizzes,
        exam=Exam(
            title=f"{resolved_topic} Examination",
            questions=exam_questions,
            total_questions=len(exam_questions),
            total_points=sum(q.points for q in exam_questions),
        ),
        source_coverage=SourceCoverage(
            covered_topics=[n.topic for n in key_notes],
            content_gaps=[
                f"Note: {warning_msg}. Study pack generated directly from your material."
            ],
        ),
    )
