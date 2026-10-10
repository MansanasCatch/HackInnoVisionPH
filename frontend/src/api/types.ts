// ---------------------------------------------------------------------------
// Onboarding (mirrors app/schemas/onboarding.py)
// ---------------------------------------------------------------------------

export interface OnboardingProfile {
  id: number;
  username: string;
  age: number;
  interests: string[];
  created_at: string;
  updated_at: string;
}

export interface OnboardingCreate {
  username: string;
  age: number;
  interests: string[];
}

export interface OnboardingUpdate {
  username?: string | null;
  age?: number | null;
  interests?: string[] | null;
}

// ---------------------------------------------------------------------------
// Device & AI Model Setup (mirrors app/schemas/device.py)
// ---------------------------------------------------------------------------

/** Auto-detected host hardware specs (GET/POST /device/detect). */
export interface DeviceSpecsDetect {
  ram_gb: number;
  gpu_name: string | null;
  vram_gb: number;
  cpu_cores: number;
  storage_free_gb: number;
  os_name: string;
}

/** Payload for POST /device. */
export interface DeviceSpecsCreate {
  onboarding_id: number;
  ram_gb: number;
  gpu_name?: string | null;
  vram_gb?: number;
  cpu_cores: number;
  storage_free_gb: number;
  os_name?: string;
  selected_model?: string | null;
}

export type ModelPullStatus = "completed" | "pulling" | "pending" | "not_pulled" | "offline" | "failed" | string;

/** Saved device specs for an account (POST /device, GET /device/account/{id}, POST /device/select-model). */
export interface DeviceSpecsRead {
  id: number;
  onboarding_id: number;
  ram_gb: number;
  gpu_name: string | null;
  vram_gb: number;
  cpu_cores: number;
  storage_free_gb: number;
  os_name: string;
  selected_model: string;
  pull_status: ModelPullStatus;
  pull_percentage: number;
  pull_status_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface ModelOption {
  model_name: string;
  display_name: string;
  size_gb: number;
  min_ram_gb: number;
  min_vram_gb: number;
  tier: string;
  is_recommended: boolean;
  reason: string;
}

/** GET /device/suggestions */
export interface ModelSuggestionsResponse {
  recommended_model: string;
  device_summary: string;
  models: ModelOption[];
}

/** Payload for POST /device/select-model. */
export interface ModelSelectPayload {
  onboarding_id: number;
  selected_model: string;
  auto_pull?: boolean;
}

/** GET /device/active-model */
export interface ActiveModelResponse {
  onboarding_id: number | null;
  active_model: string;
  pull_status: ModelPullStatus;
  pull_percentage: number;
  pull_status_message: string | null;
  is_ollama_online: boolean;
}

/** GET /device/ollama/models */
export interface OllamaModelsResponse {
  is_online: boolean;
  installed_models: string[];
  count: number;
}

export interface FlashcardItem {
  question: string;
  answer: string;
  topic?: string;
  difficulty?: string;
}

export interface QuizQuestionItem {
  type: string;
  question: string;
  options: string[] | null;
  correct_answer: string;
  explanation: string;
  topic?: string;
  difficulty?: string;
}

export interface ExamQuestionItem {
  id: number;
  type: string;
  question: string;
  options: string[] | null;
  correct_answer: string;
  explanation: string;
  topic?: string;
  difficulty?: string;
  points: number;
}

export interface ExamPackage {
  title: string;
  questions: ExamQuestionItem[];
  total_questions: number;
  total_points: number;
}

export interface ReviewerSection {
  title: string;
  content: string;
  key_points: string[];
}

export interface ReviewerPackage {
  title: string;
  sections: ReviewerSection[];
}

export interface KeyNoteItem {
  topic: string;
  notes: string[];
}

export interface StudyMaterialsResponse {
  intent: string;
  direct_answer: string;
  topic: string;
  source_summary: string;
  reviewer: ReviewerPackage;
  summary: { content: string };
  key_notes: KeyNoteItem[];
  flashcards: FlashcardItem[];
  quizzes: QuizQuestionItem[];
  exam: ExamPackage;
  source_coverage: {
    covered_topics: string[];
    content_gaps: string[];
  };
}

export interface LearningResourceRead {
  id: number;
  onboarding_id: number;
  title: string;
  subject: string;
  source_label: string;
  created_at: string;
  updated_at: string;
}

export interface LearningResourceVersionRead {
  id: number;
  learning_resource_id: number;
  version_number: number;
  title: string;
  summary: string;
  content: StudyMaterialsResponse | Record<string, any>;
  resource_types: string[];
  topics: string[];
  is_current: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenerationInfo {
  model_used: string;
  is_ollama_online: boolean;
  execution_time_seconds: number;
  warnings: string[];
}

export interface GeneratedLearningResource {
  resource: LearningResourceRead;
  version: LearningResourceVersionRead;
  generation: GenerationInfo;
}

export interface VersionProgressRead {
  onboarding_id: number;
  resource_version_id: number;
  first_time_for_version: boolean;
  attempts_count: number;
  latest_score: number | null;
  best_score: number | null;
  latest_accuracy: number;
  mastery_state: string;
  first_started_at: string | null;
  last_studied_at: string | null;
}

export interface StudySessionRead {
  id: number;
  onboarding_id: number;
  resource_version_id: number;
  mode: string;
  source: string;
  score: number | null;
  time_spent_seconds: number;
  is_completed: boolean;
  started_at: string;
  completed_at: string | null;
}

export interface StudyAnswerCreate {
  question_id: string;
  concept_id: string;
  concept_name: string;
  student_answer: string;
  correct_answer: string;
  is_correct: boolean;
  time_taken_seconds?: number;
  confidence?: number;
  hints_used?: number;
}

export interface StudySessionCompletePayload {
  score: number;
  total_items?: number;
  correct_items?: number;
  time_spent_seconds?: number;
}

export interface KnowledgeMapItem {
  concept_id: string;
  concept_name: string;
  accuracy: number;
  answers: number;
  sessions: number;
  state: "strong" | "developing" | "needs_practice";
  last_seen: string | null;
}

export interface KnowledgeMapResponse {
  onboarding_id: number;
  items: KnowledgeMapItem[];
}

export interface HealthResponse {
  status: string;
  database: string;
  ollama: string;
  installed_models: string[];
}

export interface AIGenerateRequest {
  prompt: string;
  topic?: string;
  onboarding_id?: number;
  model_override?: string;
  system_prompt?: string;
  temperature?: number;
}

export interface AIGenerateResponse {
  response: string;
  model_used: string;
  prompt_tokens?: number | null;
  completion_tokens?: number | null;
  total_tokens?: number | null;
  execution_time_seconds: number;
  is_ollama_online: boolean;
}
