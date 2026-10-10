import type {
  AIGenerateResponse,
  DocumentExtractResponse,
  StudyMaterialsResponse,
} from "./api/types";

/** What the UI keeps in memory after /ai/generate-with-files succeeds. */
export type MaterialSet = {
  topic: string;
  model: string;
  seconds: number;
  online: boolean;
  warnings: string[];
  fileNames: string[];
  materials: StudyMaterialsResponse;
};

export type QuizItem = {
  question: string;
  options: string[];
  answer: number;
  concept: string;
  explanation: string;
};

export type CardItem = { front: string; back: string; concept: string };

/** Keep prompts inside what small local models can digest. */
export const MAX_CONTEXT_CHARS = 12000;

export function toMaterialSet(res: AIGenerateResponse, topic: string): MaterialSet | null {
  if (!res.study_materials) return null;
  return {
    topic: res.study_materials.topic || topic,
    model: res.model_used,
    seconds: res.execution_time_seconds,
    online: res.is_ollama_online,
    warnings: res.warnings || [],
    fileNames: (res.ingested_files || []).map((f) => f.filename),
    materials: res.study_materials,
  };
}

/** Text shown as the tutor's reply: direct answer → summary → first reviewer section → raw text. */
export function tutorReply(res: AIGenerateResponse): string {
  const sm = res.study_materials;
  const text =
    sm?.direct_answer?.trim() ||
    sm?.summary?.content?.trim() ||
    sm?.reviewer?.sections?.[0]?.content?.trim() ||
    "";
  if (text) return text;
  // Raw output is JSON in study mode; never show a JSON blob to the learner.
  const raw = (res.response_text || "").trim();
  return raw.startsWith("{") ? "I couldn't format an answer this time. Please try rephrasing." : raw;
}

/** The backend only treats a prompt as a direct question when it looks like one. */
export function asQuestion(text: string): string {
  const clean = text.trim();
  return /[?？]$/.test(clean) ? clean : `${clean}?`;
}

/**
 * Combine typed notes with extracted file text (already parsed by /ai/extract-text) so files
 * are not parsed or OCR'd a second time by /ai/generate-with-files.
 */
export function buildTextContext(notes: string, extracted?: DocumentExtractResponse | null): string {
  const parts: string[] = [];
  if (notes.trim()) parts.push(notes.trim());
  for (const file of extracted?.files || []) {
    const text = (file.extracted_text || "").trim();
    if (!text) continue;
    if (notes.includes(text.slice(0, 200))) continue; // already auto-filled into notes
    parts.push(`--- ${file.filename} ---\n${text}`);
  }
  return parts.join("\n\n").slice(0, MAX_CONTEXT_CHARS);
}

export function toCards(m: Partial<StudyMaterialsResponse> | undefined): CardItem[] {
  return (m?.flashcards || [])
    .filter((c) => c.question && c.answer)
    .map((c) => ({ front: c.question, back: c.answer, concept: c.topic || "Core concept" }));
}

function resolveAnswerIndex(options: string[], correct: string): number {
  const norm = (s: string) => s.trim().toLowerCase().replace(/[.)\s]+$/, "");
  const target = norm(correct);
  const exact = options.findIndex((o) => norm(o) === target);
  if (exact >= 0) return exact;
  const letter = /^([a-d])(?:[.)]|$)/i.exec(correct.trim());
  if (letter) return letter[1].toUpperCase().charCodeAt(0) - 65;
  const partial = options.findIndex((o) => norm(o).includes(target) || target.includes(norm(o)));
  return partial;
}

/** Only questions we can render as multiple choice; others are skipped rather than mis-graded. */
export function toQuizItems(m: Partial<StudyMaterialsResponse> | undefined): QuizItem[] {
  const pool = [
    ...(m?.quizzes || []),
    ...(m?.quizzes?.length ? [] : m?.exam?.questions || []),
  ];
  const items: QuizItem[] = [];
  for (const q of pool) {
    const options =
      q.options && q.options.length >= 2
        ? q.options
        : q.type === "true_false"
          ? ["True", "False"]
          : [];
    if (!q.question || options.length < 2) continue;
    const answer = resolveAnswerIndex(options, q.correct_answer || "");
    if (answer < 0 || answer >= options.length) continue;
    items.push({
      question: q.question,
      options,
      answer,
      concept: q.topic || "Core concept",
      explanation: q.explanation || `Correct answer: ${options[answer]}`,
    });
  }
  return items;
}
