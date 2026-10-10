import {
  FlashcardItem,
  QuizQuestionItem,
  ReviewerSection,
  StudyMaterialsResponse,
} from "./types";

export interface MappedNoteSection {
  title: string;
  content: string;
  keyPoints: string[];
}

export interface MappedNotes {
  title: string;
  summary: string;
  sections: MappedNoteSection[];
}

export interface MappedFlashcard {
  question: string;
  answer: string;
  topic?: string;
  difficulty?: string;
}

export interface MappedQuizQuestion {
  question: string;
  options: string[];
  answer: number;
  correctAnswerText: string;
  concept: string;
  explanation: string;
}

/**
 * Extracts and maps structured notes/reviewer content from backend study materials.
 */
export function mapNotesFromMaterials(
  materials: Partial<StudyMaterialsResponse> | null | undefined
): MappedNotes {
  if (!materials) {
    return {
      title: "Study Notes",
      summary: "",
      sections: [],
    };
  }

  const title = materials.reviewer?.title || materials.topic || "Study Notes";
  const summary = materials.summary?.content || materials.source_summary || "";

  const sections: MappedNoteSection[] = [];

  if (materials.reviewer?.sections && Array.isArray(materials.reviewer.sections)) {
    materials.reviewer.sections.forEach((sec: ReviewerSection) => {
      sections.push({
        title: sec.title,
        content: sec.content,
        keyPoints: sec.key_points || [],
      });
    });
  } else if (materials.key_notes && Array.isArray(materials.key_notes)) {
    materials.key_notes.forEach((kn) => {
      sections.push({
        title: kn.topic,
        content: kn.notes.join("\n"),
        keyPoints: kn.notes,
      });
    });
  }

  return { title, summary, sections };
}

/**
 * Extracts flashcards as [question, answer] tuples or objects for the viewer.
 */
export function mapFlashcardsFromMaterials(
  materials: Partial<StudyMaterialsResponse> | null | undefined
): [string, string][] {
  if (!materials?.flashcards || !Array.isArray(materials.flashcards)) {
    return [];
  }
  return materials.flashcards
    .filter((fc: FlashcardItem) => fc.question && fc.answer)
    .map((fc: FlashcardItem) => [fc.question, fc.answer]);
}

/**
 * Maps backend quizzes or exam questions into the frontend QuizViewer format.
 */
export function mapQuizQuestionsFromMaterials(
  materials: Partial<StudyMaterialsResponse> | null | undefined
): MappedQuizQuestion[] {
  if (!materials) return [];

  const rawQuestions: Array<any> = [];

  if (materials.quizzes && Array.isArray(materials.quizzes)) {
    rawQuestions.push(...materials.quizzes);
  }
  if (materials.exam?.questions && Array.isArray(materials.exam.questions)) {
    rawQuestions.push(...materials.exam.questions);
  }

  const mapped: MappedQuizQuestion[] = [];

  for (const q of rawQuestions) {
    if (!q.question) continue;

    let options = Array.isArray(q.options) && q.options.length > 0 ? [...q.options] : [];
    const correctText = String(q.correct_answer || "").trim();

    // If options are missing (e.g. true/false or open ended), synthesize meaningful choices
    if (options.length === 0) {
      if (q.type === "true_false" || correctText.toLowerCase() === "true" || correctText.toLowerCase() === "false") {
        options = ["True", "False"];
      } else {
        options = [correctText, "Not applicable", "Other"];
      }
    }

    // Determine 0-based index of the correct answer
    let answerIndex = options.findIndex(
      (opt) => opt.toLowerCase().trim() === correctText.toLowerCase()
    );
    if (answerIndex === -1) {
      // If letter index like 'A', 'B', 'C'
      const match = correctText.match(/^[A-Da-d]$/);
      if (match) {
        answerIndex = match[0].toUpperCase().charCodeAt(0) - 65;
        if (answerIndex >= options.length) answerIndex = 0;
      } else {
        // Option not directly found, ensure correct answer is option 0 or appended
        options.unshift(correctText);
        answerIndex = 0;
      }
    }

    mapped.push({
      question: q.question,
      options,
      answer: answerIndex,
      correctAnswerText: correctText,
      concept: q.topic || materials.topic || "Core Concept",
      explanation: q.explanation || "Review source material for details.",
    });
  }

  return mapped;
}

/**
 * Maps the age range string from ProfileSetup into an integer 1-150.
 */
export function mapAgeRangeToNumber(ageRange: string): number {
  switch (ageRange) {
    case "Under 13":
      return 12;
    case "13–17":
      return 16;
    case "18–24":
      return 21;
    case "25–34":
      return 28;
    case "35–49":
      return 40;
    case "50 or older":
      return 55;
    case "Prefer not to say":
    default:
      return 20;
  }
}

/**
 * Maps a numeric age from the backend back to the closest ProfileSetup age range label.
 */
export function mapAgeToRange(age: number | null | undefined): string {
  if (age == null || !Number.isFinite(age)) return "Prefer not to say";
  if (age < 13) return "Under 13";
  if (age <= 17) return "13–17";
  if (age <= 24) return "18–24";
  if (age <= 34) return "25–34";
  if (age <= 49) return "35–49";
  return "50 or older";
}
