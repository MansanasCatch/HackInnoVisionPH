import { describe, expect, it } from "vitest";
import {
  mapAgeRangeToNumber,
  mapFlashcardsFromMaterials,
  mapNotesFromMaterials,
  mapQuizQuestionsFromMaterials,
} from "./mappers";
import { StudyMaterialsResponse } from "./types";

describe("mappers", () => {
  it("maps age range to integers between 1 and 150", () => {
    expect(mapAgeRangeToNumber("Under 13")).toBe(12);
    expect(mapAgeRangeToNumber("13–17")).toBe(16);
    expect(mapAgeRangeToNumber("18–24")).toBe(21);
    expect(mapAgeRangeToNumber("25–34")).toBe(28);
    expect(mapAgeRangeToNumber("35–49")).toBe(40);
    expect(mapAgeRangeToNumber("50 or older")).toBe(55);
    expect(mapAgeRangeToNumber("Prefer not to say")).toBe(20);
    expect(mapAgeRangeToNumber("unknown")).toBe(20);
  });

  it("handles null or empty study materials gracefully", () => {
    const notes = mapNotesFromMaterials(null);
    expect(notes.title).toBe("Study Notes");
    expect(notes.sections).toEqual([]);

    const flashcards = mapFlashcardsFromMaterials(null);
    expect(flashcards).toEqual([]);

    const quiz = mapQuizQuestionsFromMaterials(null);
    expect(quiz).toEqual([]);
  });

  it("maps study materials with reviewer sections and flashcards", () => {
    const sample: Partial<StudyMaterialsResponse> = {
      topic: "Photosynthesis",
      summary: { content: "Process by which plants convert sunlight into chemical energy." },
      reviewer: {
        title: "Photosynthesis Comprehensive Guide",
        sections: [
          {
            title: "Light Reactions",
            content: "Takes place in thylakoids.",
            key_points: ["Water split", "ATP produced"],
          },
        ],
      },
      flashcards: [
        {
          question: "Where do light reactions occur?",
          answer: "Thylakoid membrane",
          topic: "Photosynthesis",
        },
      ],
    };

    const notes = mapNotesFromMaterials(sample);
    expect(notes.title).toBe("Photosynthesis Comprehensive Guide");
    expect(notes.summary).toContain("Process by which plants");
    expect(notes.sections.length).toBe(1);
    expect(notes.sections[0].title).toBe("Light Reactions");

    const flashcards = mapFlashcardsFromMaterials(sample);
    expect(flashcards).toEqual([
      ["Where do light reactions occur?", "Thylakoid membrane"],
    ]);
  });

  it("maps quizzes into choice options and identifies correct index", () => {
    const sample: Partial<StudyMaterialsResponse> = {
      topic: "Cell Biology",
      quizzes: [
        {
          type: "multiple_choice",
          question: "What is the powerhouse of the cell?",
          options: ["Ribosome", "Mitochondria", "Nucleus"],
          correct_answer: "Mitochondria",
          explanation: "Mitochondria produces cellular ATP.",
          topic: "Organelles",
        },
        {
          type: "true_false",
          question: "Plants have cell walls.",
          options: null,
          correct_answer: "True",
          explanation: "Plant cells are enclosed by a rigid cellulose cell wall.",
          topic: "Cell Structure",
        },
      ],
    };

    const questions = mapQuizQuestionsFromMaterials(sample);
    expect(questions.length).toBe(2);

    // First question
    expect(questions[0].question).toBe("What is the powerhouse of the cell?");
    expect(questions[0].options).toEqual(["Ribosome", "Mitochondria", "Nucleus"]);
    expect(questions[0].answer).toBe(1); // Mitochondria is index 1
    expect(questions[0].concept).toBe("Organelles");

    // Second question (synthesized true/false)
    expect(questions[1].question).toBe("Plants have cell walls.");
    expect(questions[1].options).toEqual(["True", "False"]);
    expect(questions[1].answer).toBe(0); // True is index 0
  });
});
