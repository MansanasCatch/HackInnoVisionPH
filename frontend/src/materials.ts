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
  resourceId?: number;
  versionId?: number;
  onboardingId?: number;
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

export function toMaterialSet(
  res: AIGenerateResponse,
  topic: string,
  extra?: { resourceId?: number; versionId?: number; onboardingId?: number }
): MaterialSet | null {
  if (!res.study_materials) return null;
  return {
    topic: res.study_materials.topic || topic,
    model: res.model_used,
    seconds: res.execution_time_seconds,
    online: res.is_ollama_online,
    warnings: res.warnings || [],
    fileNames: (res.ingested_files || []).map((f) => f.filename),
    materials: res.study_materials,
    resourceId: extra?.resourceId,
    versionId: extra?.versionId,
    onboardingId: extra?.onboardingId,
  };
}

export function fromVersionToMaterialSet(
  version: { id: number; learning_resource_id: number; title: string; content: any },
  extra?: { sourceLabel?: string; onboardingId?: number }
): MaterialSet | null {
  if (!version.content || typeof version.content !== "object") return null;
  const content = version.content as StudyMaterialsResponse;
  return {
    topic: content.topic || version.title,
    model: "Saved resource",
    seconds: 0,
    online: true,
    warnings: [],
    fileNames: extra?.sourceLabel ? [extra.sourceLabel] : [],
    materials: content,
    resourceId: version.learning_resource_id,
    versionId: version.id,
    onboardingId: extra?.onboardingId,
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
  const rawPool = [
    ...(m?.quizzes || []),
    ...(m?.exam?.questions || []),
  ];
  const seen = new Set<string>();
  const pool = rawPool.filter((q) => {
    const key = (q.question || "").trim().toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
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

/**
 * Merges multiple MaterialSets into a single unified MaterialSet.
 * Pools reviewer sections, flashcards, quizzes, and exam questions,
 * creating a comprehensive master set of 20-30+ items for review and practice.
 */
export function combineMaterialSets(sets: MaterialSet[]): MaterialSet {
  if (sets.length === 0) {
    throw new Error("Cannot combine an empty list of material sets.");
  }
  if (sets.length === 1) {
    return sets[0];
  }

  const combinedTopic = sets.map((s) => s.topic).filter(Boolean).join(" & ");
  const combinedFileNames = Array.from(new Set(sets.flatMap((s) => s.fileNames)));
  const allSections = sets.flatMap((s) => s.materials.reviewer?.sections || []);
  const allKeyNotes = sets.flatMap((s) => s.materials.key_notes || []);
  const allFlashcards = sets.flatMap((s) => s.materials.flashcards || []);
  const allQuizzes = sets.flatMap((s) => s.materials.quizzes || []);
  const allExamQuestions = sets.flatMap((s) => s.materials.exam?.questions || []);

  const totalQuestions = allQuizzes.length + allExamQuestions.length;

  const combinedMaterials: StudyMaterialsResponse = {
    topic: combinedTopic,
    direct_answer: `Master Practice Review combining ${sets.length} study sets (${combinedTopic}).`,
    source_summary: `Combined from ${sets.length} saved study resources: ${sets.map((s) => s.topic).join(", ")}.`,
    summary: {
      title: `${combinedTopic} — Combined Master Review`,
      content: `Comprehensive master practice set pooling materials, flashcards, and quizzes from ${sets.length} study topics.`,
      estimated_reading_minutes: Math.max(5, Math.ceil(allSections.length * 2)),
    },
    key_notes: allKeyNotes,
    reviewer: {
      title: `${combinedTopic} (Combined Master Reviewer)`,
      sections: allSections,
    },
    flashcards: allFlashcards,
    quizzes: allQuizzes,
    exam: {
      title: `${combinedTopic} — Master Practice Exam`,
      total_questions: totalQuestions,
      time_limit_minutes: Math.max(20, Math.ceil(totalQuestions * 1.5)),
      questions: allExamQuestions,
    },
  };

  return {
    topic: `${combinedTopic} (Combined Set)`,
    model: "Master Combiner",
    seconds: 0,
    online: true,
    warnings: [],
    fileNames: combinedFileNames,
    materials: combinedMaterials,
    resourceId: undefined,
    versionId: undefined,
    onboardingId: sets[0].onboardingId,
  };
}

