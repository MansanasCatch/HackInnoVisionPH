import {
  ActiveModelResponse,
  DeviceSpecsCreate,
  DeviceSpecsDetect,
  DeviceSpecsRead,
  GeneratedLearningResource,
  HealthResponse,
  KnowledgeMapResponse,
  LearningResourceRead,
  LearningResourceVersionRead,
  ModelSelectPayload,
  ModelSuggestionsResponse,
  OllamaModelsResponse,
  OnboardingCreate,
  OnboardingProfile,
  OnboardingUpdate,
  StudyAnswerCreate,
  StudySessionCompletePayload,
  StudySessionCompleteResponse,
  StudySessionRead,
  VersionProgressRead,
} from "./types";

const BASE_URL = "/api/v1";

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

/** Extract a human-readable message from the backend's error payload shapes. */
function extractErrorMessage(body: any, status: number): string {
  if (body && typeof body === "object") {
    // App errors: { error: { code, message } }
    if (body.error && typeof body.error === "object" && typeof body.error.message === "string") {
      return body.error.message;
    }
    // HTTPException: { detail: "..." }
    if (typeof body.detail === "string") return body.detail;
    // Validation errors: { detail: [{ loc, msg }] }
    if (Array.isArray(body.detail) && body.detail.length) {
      return body.detail
        .map((item: any) => {
          const field = Array.isArray(item?.loc) ? item.loc.filter((part: unknown) => part !== "body").join(".") : "";
          return field ? `${field}: ${item?.msg}` : String(item?.msg ?? "Invalid value");
        })
        .join("; ");
    }
    if (typeof body.message === "string") return body.message;
  }
  if (typeof body === "string" && body && !body.startsWith("<")) return body;
  return `HTTP error ${status}`;
}

async function handleResponse<T>(res: Response): Promise<T> {
  const contentType = res.headers.get("content-type") || "";
  if (!res.ok) {
    let errBody: any = null;
    try {
      errBody = contentType.includes("application/json") ? await res.json() : await res.text();
    } catch {
      errBody = null;
    }
    throw new ApiError(extractErrorMessage(errBody, res.status), res.status, errBody);
  }

  if (!contentType.includes("application/json")) {
    const text = await res.text();
    throw new ApiError(`Expected JSON but got ${contentType || "HTML"} from server`, res.status, text);
  }

  return res.json() as Promise<T>;
}

/** fetch wrapper that converts network failures/timeouts into a typed ApiError (status 0). */
async function request(url: string, init: RequestInit = {}, timeoutMs = 20000): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: init.signal ?? controller.signal });
  } catch (err) {
    const aborted = err instanceof DOMException && err.name === "AbortError";
    throw new ApiError(
      aborted
        ? "The Calibrat8 backend took too long to respond. Please try again."
        : "Can't reach the Calibrat8 backend. Make sure `python run.py` is running.",
      0,
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

function jsonInit(method: string, body: unknown): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

/** Turn any thrown value into a short user-facing message. */
export function describeApiError(err: unknown): string {
  if (err instanceof ApiError) return err.message;
  if (err instanceof Error) return err.message;
  return "Something went wrong. Please try again.";
}

export const api = {
  // Health
  async getHealth(): Promise<HealthResponse> {
    const res = await fetch(`${BASE_URL}/health`);
    return handleResponse<HealthResponse>(res);
  },

  // AI Inference
  async aiGenerate(data: import("./types").AIGenerateRequest): Promise<import("./types").AIGenerateResponse> {
    const res = await fetch(`${BASE_URL}/ai/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return handleResponse<import("./types").AIGenerateResponse>(res);
  },

  // Onboarding
  async createOnboarding(data: OnboardingCreate): Promise<OnboardingProfile> {
    const res = await request(`${BASE_URL}/onboarding`, jsonInit("POST", data));
    return handleResponse<OnboardingProfile>(res);
  },

  async listOnboarding(limit = 100, offset = 0): Promise<OnboardingProfile[]> {
    const res = await request(`${BASE_URL}/onboarding?limit=${limit}&offset=${offset}`);
    return handleResponse<OnboardingProfile[]>(res);
  },

  async getOnboardingByUser(username: string): Promise<OnboardingProfile | null> {
    const res = await request(`${BASE_URL}/onboarding/user/${encodeURIComponent(username)}`);
    if (res.status === 404) return null;
    return handleResponse<OnboardingProfile>(res);
  },

  async getOnboardingById(id: number): Promise<OnboardingProfile | null> {
    const res = await request(`${BASE_URL}/onboarding/${id}`);
    if (res.status === 404) return null;
    return handleResponse<OnboardingProfile>(res);
  },

  async updateOnboarding(id: number, data: OnboardingUpdate): Promise<OnboardingProfile> {
    const res = await request(`${BASE_URL}/onboarding/${id}`, jsonInit("PUT", data));
    return handleResponse<OnboardingProfile>(res);
  },

  async deleteOnboarding(id: number): Promise<void> {
    const res = await request(`${BASE_URL}/onboarding/${id}`, { method: "DELETE" });
    if (!res.ok && res.status !== 204 && res.status !== 404) {
      let errBody: any = null;
      try {
        errBody = await res.json();
      } catch {
        errBody = null;
      }
      throw new ApiError(extractErrorMessage(errBody, res.status), res.status, errBody);
    }
  },

  // Device & AI Model Setup
  async detectDevice(): Promise<DeviceSpecsDetect> {
    const res = await request(`${BASE_URL}/device/detect`, { method: "POST" });
    return handleResponse<DeviceSpecsDetect>(res);
  },

  async getDeviceSuggestions(params: {
    ram_gb?: number | null;
    vram_gb?: number | null;
    gpu_name?: string | null;
    onboarding_id?: number | null;
  } = {}): Promise<ModelSuggestionsResponse> {
    const query = new URLSearchParams();
    if (params.ram_gb != null && params.ram_gb >= 0.5) query.append("ram_gb", String(params.ram_gb));
    if (params.vram_gb != null && params.vram_gb >= 0) query.append("vram_gb", String(params.vram_gb));
    if (params.gpu_name) query.append("gpu_name", params.gpu_name);
    if (params.onboarding_id != null) query.append("onboarding_id", String(params.onboarding_id));
    const queryString = query.toString() ? `?${query.toString()}` : "";
    const res = await request(`${BASE_URL}/device/suggestions${queryString}`);
    return handleResponse<ModelSuggestionsResponse>(res);
  },

  async saveDeviceSpecs(payload: DeviceSpecsCreate): Promise<DeviceSpecsRead> {
    const res = await request(`${BASE_URL}/device`, jsonInit("POST", payload));
    return handleResponse<DeviceSpecsRead>(res);
  },

  async getDeviceByAccount(onboardingId: number): Promise<DeviceSpecsRead | null> {
    const res = await request(`${BASE_URL}/device/account/${onboardingId}`);
    if (res.status === 404) return null;
    return handleResponse<DeviceSpecsRead>(res);
  },

  async selectModel(payload: ModelSelectPayload): Promise<DeviceSpecsRead> {
    const res = await request(`${BASE_URL}/device/select-model`, jsonInit("POST", { auto_pull: true, ...payload }));
    return handleResponse<DeviceSpecsRead>(res);
  },

  async getActiveModel(onboardingId?: number | null): Promise<ActiveModelResponse> {
    const url = onboardingId != null
      ? `${BASE_URL}/device/active-model?onboarding_id=${onboardingId}`
      : `${BASE_URL}/device/active-model`;
    const res = await request(url);
    return handleResponse<ActiveModelResponse>(res);
  },

  async listOllamaModels(): Promise<OllamaModelsResponse> {
    const res = await request(`${BASE_URL}/device/ollama/models`);
    return handleResponse<OllamaModelsResponse>(res);
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

  async getVersionProgress(resourceId: number, versionId: number, onboardingId: number): Promise<VersionProgressRead> {
    const res = await fetch(`${BASE_URL}/learning-resources/${resourceId}/versions/${versionId}/progress?onboarding_id=${onboardingId}`);
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

  async completeStudySession(sessionId: number, payload: StudySessionCompletePayload): Promise<StudySessionCompleteResponse> {
    const res = await fetch(`${BASE_URL}/study-sessions/${sessionId}/complete`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return handleResponse<StudySessionCompleteResponse>(res);
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
