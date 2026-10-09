import {
  ActiveModelStatus,
  DeviceSpecs,
  DeviceSuggestions,
  GeneratedLearningResource,
  HealthResponse,
  KnowledgeMapResponse,
  LearningResourceRead,
  LearningResourceVersionRead,
  OnboardingCreate,
  OnboardingProfile,
  StudyAnswerCreate,
  StudySessionCompletePayload,
  StudySessionRead,
  VersionProgressRead,
} from "./types";

const BASE_URL = "/api/v1";

class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errBody: any = null;
    try {
      errBody = await res.json();
    } catch {
      errBody = await res.text();
    }
    const message =
      (errBody && typeof errBody === "object" && (errBody.detail || errBody.message)) ||
      `HTTP error ${res.status}`;
    throw new ApiError(message, res.status, errBody);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Health
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse<HealthResponse>(res);
  },

  // Onboarding
  async createOnboarding(data: OnboardingCreate): Promise<OnboardingProfile> {
    const res = await fetch(`${BASE_URL}/onboarding`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return handleResponse<OnboardingProfile>(res);
  },

  async getOnboardingByUser(username: string): Promise<OnboardingProfile | null> {
    const res = await fetch(`${BASE_URL}/onboarding/user/${encodeURIComponent(username)}`);
    if (res.status === 404) return null;
    return handleResponse<OnboardingProfile>(res);
  },

  async getOnboardingById(id: number): Promise<OnboardingProfile> {
    const res = await fetch(`${BASE_URL}/onboarding/${id}`);
    return handleResponse<OnboardingProfile>(res);
  },

  // Device & Models
  async detectDevice(): Promise<DeviceSpecs> {
    const res = await fetch(`${BASE_URL}/device/detect`);
    return handleResponse<DeviceSpecs>(res);
  },

  async getDeviceSuggestions(specs: DeviceSpecs): Promise<DeviceSuggestions> {
    const res = await fetch(`${BASE_URL}/device/suggestions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(specs),
    });
    return handleResponse<DeviceSuggestions>(res);
  },

  async saveDeviceSpecs(specs: DeviceSpecs): Promise<DeviceSpecs> {
    const res = await fetch(`${BASE_URL}/device`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(specs),
    });
    return handleResponse<DeviceSpecs>(res);
  },

  async selectModel(modelTag: string, onboardingId?: number): Promise<{ message: string; selected_model: string }> {
    const res = await fetch(`${BASE_URL}/device/select-model`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model_tag: modelTag, onboarding_id: onboardingId }),
    });
    return handleResponse<{ message: string; selected_model: string }>(res);
  },

  async getActiveModel(onboardingId?: number): Promise<ActiveModelStatus> {
    const url = onboardingId
      ? `${BASE_URL}/device/active-model?onboarding_id=${onboardingId}`
      : `${BASE_URL}/device/active-model`;
    const res = await fetch(url);
    return handleResponse<ActiveModelStatus>(res);
  },

  // Learning Resources & Generation
  async generateLearningResource(params: {
    onboarding_id: number;
    topic: string;
    notes?: string;
    resource_types?: string[];
    files?: File[];
  }): Promise<GeneratedLearningResource> {
    const formData = new FormData();
    formData.append("onboarding_id", String(params.onboarding_id));
    formData.append("topic", params.topic);
    if (params.notes) formData.append("notes", params.notes);
    if (params.resource_types) {
      params.resource_types.forEach((type) => formData.append("resource_types", type));
    }
    if (params.files) {
      params.files.forEach((file) => formData.append("files", file));
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000); // 3-minute timeout for LLM

    try {
      const res = await fetch(`${BASE_URL}/learning-resources/generate`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
      return await handleResponse<GeneratedLearningResource>(res);
    } finally {
      clearTimeout(timeoutId);
    }
  },

  async listLearningResources(onboardingId: number): Promise<LearningResourceRead[]> {
    const res = await fetch(`${BASE_URL}/learning-resources?onboarding_id=${onboardingId}`);
    return handleResponse<LearningResourceRead[]>(res);
  },

  async listVersions(resourceId: number): Promise<LearningResourceVersionRead[]> {
    const res = await fetch(`${BASE_URL}/learning-resources/${resourceId}/versions`);
    return handleResponse<LearningResourceVersionRead[]>(res);
  },

  async getVersionProgress(versionId: number, onboardingId: number): Promise<VersionProgressRead> {
    const res = await fetch(`${BASE_URL}/learning-resources/versions/${versionId}/progress?onboarding_id=${onboardingId}`);
    return handleResponse<VersionProgressRead>(res);
  },

  // Study Sessions
  async startStudySession(params: {
    onboarding_id: number;
    resource_version_id: number;
    mode: string;
    source: string;
  }): Promise<StudySessionRead> {
    const res = await fetch(`${BASE_URL}/study-sessions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });
    return handleResponse<StudySessionRead>(res);
  },

  async submitStudyAnswer(sessionId: number, answer: StudyAnswerCreate): Promise<any> {
    const res = await fetch(`${BASE_URL}/study-sessions/${sessionId}/answers`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answer),
    });
    return handleResponse<any>(res);
  },

  async completeStudySession(sessionId: number, payload: StudySessionCompletePayload): Promise<StudySessionRead> {
    const res = await fetch(`${BASE_URL}/study-sessions/${sessionId}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return handleResponse<StudySessionRead>(res);
  },

  async listStudySessions(onboardingId: number, limit: number = 50): Promise<StudySessionRead[]> {
    const res = await fetch(`${BASE_URL}/study-sessions?onboarding_id=${onboardingId}&limit=${limit}`);
    return handleResponse<StudySessionRead[]>(res);
  },

  // Knowledge Map
  async getKnowledgeMap(onboardingId: number): Promise<KnowledgeMapResponse> {
    const res = await fetch(`${BASE_URL}/knowledge-map?onboarding_id=${onboardingId}`);
    return handleResponse<KnowledgeMapResponse>(res);
  },
};
