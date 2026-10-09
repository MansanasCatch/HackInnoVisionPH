/**
 * Lumi — Local AI Tutor Application
 *
 * Incremental vanilla JavaScript implementation translating the Figma Make
 * React application into the repository's frontend architecture.
 *
 * Responsibilities:
 *  - Lumi onboarding / welcome-back landing page (matching provided screenshot)
 *  - 5-step personalization and device fit setup flow
 *  - Centralized reactive state store with LocalStorage persistence
 *  - Distraction-free Study Mode & Focus session
 *  - Interactive Personal AI Tutor with worked examples
 *  - Lesson library with audio recording consent & simulated capture
 *  - Ingestion (text, voice, camera, files) & AI generation
 *  - Resource library with Notes, Flashcards, and Practice Quizzes
 *  - Evidence-based Knowledge Map, Adaptive Practice, and Weekly Reports
 *  - Settings, Offline simulation, and live FastAPI backend connectivity
 */

const API_BASE = "/api/v1";
const HEALTH_POLL_INTERVAL_MS = 30_000;

/* --------------------------------------------------------------------------
   SVG Icons Dictionary
   -------------------------------------------------------------------------- */
const ICONS = {
  home: '<path d="m3 11 9-8 9 8"/><path d="M5 10v10h14V10M9 20v-6h6v6"/>',
  spark: '<path d="m12 3-1.4 4.1A5.3 5.3 0 0 1 7.1 10L3 11.5l4.1 1.4a5.3 5.3 0 0 1 3.5 3.5L12 21l1.4-4.6a5.3 5.3 0 0 1 3.5-3.5l4.1-1.4-4.1-1.5a5.3 5.3 0 0 1-3.5-2.9Z"/>',
  calendar: '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M8 3v4m8-4v4M3 10h18m-13 4h3m2 0h3m-8 3h3"/>',
  book: '<path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v17H7.5A3.5 3.5 0 0 0 4 22Z"/><path d="M20 5.5A3.5 3.5 0 0 0 16.5 2H13v17h3.5A3.5 3.5 0 0 1 20 22Z"/>',
  chart: '<path d="M4 20V10m6 10V4m6 16v-7m5 7H2"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1a1.7 1.7 0 0 0 1.9.3A1.7 1.7 0 0 0 10 3V2.8h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/>',
  wifi: '<path d="M5 12.6a10 10 0 0 1 14 0M2 9.2a15 15 0 0 1 20 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19" r="1"/>',
  offline: '<path d="M5 12.6a10 10 0 0 1 10.7-2M8.5 16a5 5 0 0 1 7 0M2 9.2a15 15 0 0 1 9.5-3.1M3 3l18 18"/><circle cx="12" cy="19" r="1"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 20h16"/>',
  arrow: '<path d="M5 12h14m-5-5 5 5-5 5"/>',
  play: '<path d="m9 6 9 6-9 6Z"/>',
  pause: '<path d="M9 5v14m6-14v14"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="2"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  check: '<path d="m5 12 4 4L19 6"/>',
  mic: '<rect x="9" y="3" width="6" height="12" rx="3"/><path d="M5 11a7 7 0 0 0 14 0m-7 7v3m-4 0h8"/>',
  send: '<path d="m3 4 18 8-18 8 3-8Z"/><path d="M6 12h15"/>',
  plus: '<path d="M12 5v14m-7-7h14"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  file: '<path d="M6 2h8l4 4v16H6Z"/><path d="M14 2v5h5M9 12h6m-6 4h6"/>',
  cards: '<rect x="4" y="6" width="14" height="14" rx="2"/><path d="m7 6 1-3h12v14l-2 .7"/>',
  quiz: '<circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.3 2.3 0 1 1 3.4 2c-.8.4-1.2.9-1.2 2m0 3h.01"/>',
  chevron: '<path d="m9 6 6 6-6 6"/>',
  more: '<circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/>',
  edit: '<path d="m4 20 4.5-1 10-10-3.5-3.5-10 10Z"/><path d="m13.5 7 3.5 3.5"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  headphones: '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><path d="M4 14h3v6H5a1 1 0 0 1-1-1Zm16 0h-3v6h2a1 1 0 0 0 1-1Z"/>',
  upload: '<path d="M12 16V4m-5 5 5-5 5 5"/><path d="M4 15v5h16v-5"/>',
  layers: '<path d="m12 2 9 5-9 5-9-5Z"/><path d="m3 12 9 5 9-5M3 17l9 5 9-5"/>',
  image: '<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 20"/>',
};

function renderIcon(name, size = 20, className = "") {
  const content = ICONS[name] || "";
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="${className}">${content}</svg>`;
}

function renderLumi(size = "medium") {
  return `<span class="lumi-art lumi-${size}" role="img" aria-label="Lumi, a friendly coral and teal owl learning companion"></span>`;
}

function renderBadge(text, tone = "sage") {
  return `<span class="badge badge-${tone}">${text}</span>`;
}

/* --------------------------------------------------------------------------
   Default Profile & Storage Helpers
   -------------------------------------------------------------------------- */
const defaultProfile = {
  name: "Amara Mensah",
  level: "Senior high school",
  subjects: ["Mathematics", "Biology", "History"],
  examDate: "",
  dailyMinutes: "60",
  studyTime: "After school",
  learningStyle: "Examples, then practice",
  personalization: true,
  deviceType: "Laptop",
  deviceMemory: "8 GB",
  modelPreference: "Balanced",
  learningTopic: "",
  learningSources: [],
};

function readSavedProfile() {
  try {
    const saved = localStorage.getItem("lumi-profile") || localStorage.getItem("studypath-profile");
    if (!saved) return null;
    const parsed = JSON.parse(saved);
    return {
      ...defaultProfile,
      ...parsed,
      learningTopic: typeof parsed.learningTopic === "string" ? parsed.learningTopic : "",
      learningSources: Array.isArray(parsed.learningSources) ? parsed.learningSources : [],
    };
  } catch {
    return null;
  }
}

function readSavedAttempts() {
  try {
    const saved = localStorage.getItem("lumi-attempts");
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
}

function readSavedPage() {
  const availablePages = [
    "home", "tutor", "planner", "focus", "lessons", "ingest", "generation",
    "library", "notes", "flashcards", "quiz", "completion", "knowledge",
    "recommendations", "report", "settings", "coach", "progress",
  ];
  try {
    const saved = localStorage.getItem("lumi-last-page");
    return saved && availablePages.includes(saved) ? saved : "home";
  } catch {
    return "home";
  }
}

/* --------------------------------------------------------------------------
   Application State
   -------------------------------------------------------------------------- */
const savedProfileInit = readSavedProfile();

const state = {
  page: readSavedPage(),
  online: true,
  offlineModalOpen: false,
  confirmModal: null, // { title, message, onConfirm }
  profile: savedProfileInit || defaultProfile,
  attempts: readSavedAttempts(),
  latestAttempt: readSavedAttempts().slice(-1)[0] || null,
  // Per requirement: The first screen must be the welcome-back onboarding screen
  setupOpen: true,
  returningLearner: Boolean(savedProfileInit) || true, // Defaults to Amara welcome-back
  editingProfile: false,
  onboardingStep: 0,
  backendStatus: {
    online: false,
    version: "",
    database: "checking",
    projectCount: 0,
  },
  // Onboarding sub-state
  onboarding: {
    analysisStage: 0,
    detectedCores: 16,
    topicMethod: "text",
    topicFiles: (savedProfileInit?.learningSources || []).map(name => ({
      name,
      size: "Saved source",
      type: name.split(".").pop()?.toUpperCase() || "FILE",
    })),
    isRecording: false,
    recordingSeconds: 0,
    recordingError: "",
  },
  // Planner sub-state
  planner: {
    step: 0,
    studyMode: "Learn",
    selectedMaterials: ["Notes Summary / Key Notes"],
  },
  // Focus sub-state
  focus: {
    step: 0,
    paused: false,
    flipped: false,
    answer: null,
  },
  // Ingest sub-state
  ingest: {
    topic: "",
    notes: "",
    files: [],
    inputMethod: "text",
    stage: "add",
  },
  // Generation sub-state
  generation: {
    selected: ["notes", "cards", "quiz"],
    prepared: false,
  },
  // Library sub-state
  library: {
    filter: "all",
  },
  // Flashcards sub-state
  flashcards: {
    index: 0,
    flipped: false,
    ratings: {},
  },
  // Quiz sub-state
  quiz: {
    index: 0,
    answers: {},
  },
  // Lessons sub-state
  lessons: {
    stage: "consent",
    paused: false,
    cards: false,
    searchTerm: "",
  },
  // Tutor sub-state
  tutor: {
    messages: [
      {
        role: "user",
        text: "Why does the sign change when I move a number to the other side of an equation?",
      },
      {
        role: "tutor",
        text: "Think of an equation like a balanced scale. You’re not really “moving” the number—you’re doing the opposite operation to both sides so the scale stays balanced.",
        detail: "For example: x + 3 = 8. Subtract 3 from both sides: x + 3 − 3 = 8 − 3, so x = 5.",
      },
    ],
    input: "",
    detailOpen: false,
  },
  // Coach sub-state
  coach: {
    practice: false,
  },
};

/* --------------------------------------------------------------------------
   API Client & Connectivity
   -------------------------------------------------------------------------- */
async function fetchJson(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function refreshSystemStatus() {
  try {
    const health = await fetchJson("/health");
    const isDbConnected = health.database === "connected";
    const stats = await fetchJson("/projects/stats").catch(() => ({ total: 0 }));

    state.backendStatus = {
      online: isDbConnected,
      version: health.version || "0.1.0",
      database: isDbConnected ? "Connected" : "Disconnected",
      projectCount: stats.total || 0,
    };
  } catch (error) {
    state.backendStatus = {
      online: false,
      version: "",
      database: "Offline",
      projectCount: 0,
    };
  }
  updateBackendPill();
}

function updateBackendPill() {
  const pill = document.querySelector("#backend-status-pill");
  if (pill) {
    pill.classList.toggle("is-online", state.backendStatus.online);
    pill.innerHTML = `
      <span class="dot"></span>
      <span>${state.backendStatus.online ? `API v${state.backendStatus.version} · DB Connected` : "API Offline"}</span>
    `;
  }
}

/* --------------------------------------------------------------------------
   MediaRecorder Handler (Voice Recording)
   -------------------------------------------------------------------------- */
let activeMediaStream = null;
let activeMediaRecorder = null;
let recordedAudioChunks = [];
let recordingTimerId = null;

async function startVoiceRecording() {
  state.onboarding.recordingError = "";
  if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
    state.onboarding.recordingError = "In-app recording is not supported by this browser. You can use File to upload an audio recording instead.";
    render();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    activeMediaStream = stream;
    const recorder = new MediaRecorder(stream);
    activeMediaRecorder = recorder;
    recordedAudioChunks = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size) recordedAudioChunks.push(event.data);
    };

    recorder.onstop = () => {
      const blob = new Blob(recordedAudioChunks, { type: recorder.mimeType || "audio/webm" });
      const extension = recorder.mimeType?.includes("mp4") ? "m4a" : "webm";
      const recording = {
        name: `Voice topic ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}.${extension}`,
        size: `${Math.max(1, Math.round(blob.size / 1024))} KB`,
        type: extension.toUpperCase(),
      };
      state.onboarding.topicFiles = [...state.onboarding.topicFiles, recording].slice(0, 4);
      state.profile.learningSources = state.onboarding.topicFiles.map((file) => file.name);

      if (activeMediaStream) {
        activeMediaStream.getTracks().forEach((track) => track.stop());
        activeMediaStream = null;
      }
      recordedAudioChunks = [];
      render();
    };

    recorder.start();
    state.onboarding.recordingSeconds = 0;
    state.onboarding.isRecording = true;
    render();

    if (recordingTimerId) clearInterval(recordingTimerId);
    recordingTimerId = setInterval(() => {
      state.onboarding.recordingSeconds += 1;
      const timerEl = document.querySelector(".voice-recorder .badge");
      if (timerEl) {
        timerEl.textContent = `RECORDING · ${Math.floor(state.onboarding.recordingSeconds / 60)}:${String(state.onboarding.recordingSeconds % 60).padStart(2, "0")}`;
      }
    }, 1000);
  } catch (err) {
    state.onboarding.recordingError = "Microphone access was not available. Check your browser permission and try again.";
    state.onboarding.isRecording = false;
    render();
  }
}

function stopVoiceRecording() {
  if (recordingTimerId) {
    clearInterval(recordingTimerId);
    recordingTimerId = null;
  }
  if (activeMediaRecorder?.state === "recording") {
    activeMediaRecorder.stop();
  }
  state.onboarding.isRecording = false;
}

/* --------------------------------------------------------------------------
   State Actions
   -------------------------------------------------------------------------- */
function setPage(nextPage) {
  state.page = nextPage;
  localStorage.setItem("lumi-last-page", nextPage);
  render();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function saveProfile(nextProfile) {
  state.profile = nextProfile;
  localStorage.setItem("lumi-profile", JSON.stringify(nextProfile));
  state.returningLearner = true;
  state.setupOpen = false;
  state.editingProfile = false;
  render();
}

function startNewJourneyConfirmed() {
  localStorage.removeItem("lumi-profile");
  localStorage.removeItem("studypath-profile");
  localStorage.removeItem("lumi-attempts");
  localStorage.removeItem("lumi-last-page");

  state.profile = {
    ...defaultProfile,
    name: "",
    subjects: ["Science & nature"],
    learningTopic: "",
    learningSources: [],
  };
  state.attempts = [];
  state.latestAttempt = null;
  state.page = "home";
  state.returningLearner = false;
  state.onboardingStep = 1; // Advance directly to Step 2 (About you)
  state.onboarding.topicFiles = [];
  state.onboarding.topicMethod = "text";
  state.confirmModal = null;
  render();
}

function saveAttempt(attempt) {
  const nextAttempts = [...state.attempts, attempt];
  state.attempts = nextAttempts;
  state.latestAttempt = attempt;
  localStorage.setItem("lumi-attempts", JSON.stringify(nextAttempts));
  setPage("completion");
}

function completeStudySession(score, total) {
  saveAttempt({
    score,
    total,
    completedAt: new Date().toISOString(),
    source: "study",
    concepts: [{ name: "Inverse operations", correct: score === total }],
  });
}

/* --------------------------------------------------------------------------
   Screen Rendering Functions
   -------------------------------------------------------------------------- */

// 1. Navigation items & Header
const NAV_ITEMS = [
  { id: "home", label: "Home", icon: "home" },
  { id: "library", label: "Resources", icon: "book" },
  { id: "planner", label: "Study", icon: "calendar" },
  { id: "knowledge", label: "Knowledge Map", icon: "layers" },
  { id: "report", label: "Reports", icon: "chart" },
];

function isNavActive(itemId, currentPage) {
  if (itemId === currentPage) return true;
  if (itemId === "library") {
    return ["ingest", "generation", "notes", "flashcards", "quiz", "completion", "recommendations", "lessons"].includes(currentPage);
  }
  if (itemId === "planner") return currentPage === "focus";
  if (itemId === "knowledge") return currentPage === "coach";
  return false;
}

function renderSidebar() {
  const firstName = state.profile.name.trim().split(" ")[0] || "Amara";
  const initials = state.profile.name
    .split(" ")
    .map((p) => p[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || "AM";

  return `
    <aside class="sidebar">
      <button class="brand" data-action="go-page" data-page="home" aria-label="Lumi home">
        <span class="brand-mark">${renderIcon("spark", 18)}</span>
        <span>Lumi</span>
      </button>
      <nav class="nav-list" aria-label="Primary navigation">
        ${NAV_ITEMS.map(
          (item) => `
          <button class="nav-item ${isNavActive(item.id, state.page) ? "active" : ""}" data-action="go-page" data-page="${item.id}">
            ${renderIcon(item.icon)}
            <span>${item.id === "knowledge" ? "Knowledge Analysis" : item.label}</span>
          </button>
        `
        ).join("")}
      </nav>
      <div class="sidebar-bottom">
        <button class="connection ${state.online ? "" : "is-offline"}" data-action="toggle-online" aria-label="Toggle connection">
          <span class="status-dot"></span>
          <span>
            <strong>${state.online ? "Online" : "Offline"}</strong>
            <small>${state.online ? (state.backendStatus.online ? "API & AI ready" : "AI tutor available") : "Saved materials ready"}</small>
          </span>
        </button>
        <button class="nav-item" data-action="go-page" data-page="settings">
          ${renderIcon("settings")}
          <span>Settings & offline</span>
        </button>
        <button class="nav-item compact-preferences" data-action="edit-profile">
          ${renderIcon("edit")}
          <span>Edit learning profile</span>
        </button>
        <div class="profile">
          <div class="avatar">${initials}</div>
          <span>
            <strong>${state.profile.name || "Amara"}</strong>
            <small>${state.profile.level}</small>
          </span>
          ${renderIcon("more")}
        </div>
      </div>
    </aside>
  `;
}

function renderTopbar(title) {
  return `
    <header class="topbar">
      <div>
        <p class="eyebrow">LEARNING COMPANION</p>
        <h1>${title}</h1>
      </div>
      <div class="topbar-actions">
        <div class="backend-pill ${state.backendStatus.online ? "is-online" : ""}" id="backend-status-pill">
          <span class="dot"></span>
          <span>${state.backendStatus.online ? `API v${state.backendStatus.version} · DB Connected` : "Checking Backend…"}</span>
        </div>
        <button class="top-status ${state.online ? "" : "is-offline"}" data-action="toggle-online">
          ${renderIcon(state.online ? "wifi" : "offline", 17)}
          <span>${state.online ? "Online" : "Offline"}</span>
        </button>
      </div>
    </header>
  `;
}

function renderMobileNav() {
  return `
    <nav class="mobile-nav" aria-label="Mobile navigation">
      ${NAV_ITEMS.map(
        (item) => `
        <button class="${isNavActive(item.id, state.page) ? "active" : ""}" data-action="go-page" data-page="${item.id}">
          ${renderIcon(item.icon)}
          <span>${item.id === "planner" ? "Study Mode" : item.label.replace("Study ", "")}</span>
        </button>
      `
      ).join("")}
    </nav>
  `;
}

/* --------------------------------------------------------------------------
   Screen: Onboarding & Welcome-Back Landing Page
   -------------------------------------------------------------------------- */
function renderOnboardingShell() {
  const step = state.onboardingStep;
  const firstName = state.profile.name.trim().split(" ")[0] || "Amara";

  return `
    <div class="onboarding-shell">
      <header class="onboarding-header">
        <button class="brand" data-action="go-page" data-page="home" aria-label="Lumi home">
          <span class="brand-mark">${renderIcon("spark", 18)}</span>
          <span>Lumi</span>
        </button>
        <div class="onboarding-progress" aria-label="Setup step ${step + 1} of 5">
          <span style="width: ${(step + 1) * 20}%"></span>
        </div>
        <span class="setup-count">${step + 1} of 5</span>
      </header>

      ${step === 0 ? renderWelcomeStep(firstName) : ""}
      ${step === 1 ? renderStepAboutYou() : ""}
      ${step === 2 ? renderStepDeviceAnalysis() : ""}
      ${step === 3 ? renderStepTopic() : ""}
      ${step === 4 ? renderStepPersonalization() : ""}
    </div>
  `;
}

function renderWelcomeStep(firstName) {
  const isReturning = state.returningLearner;

  return `
    <main class="welcome-step">
      <!-- Softly rounded warm cream container card matching screenshot -->
      <div class="welcome-lumi-card">
        <div class="welcome-lumi">
          <div class="welcome-glow"></div>
          ${renderLumi("large")}
        </div>
      </div>

      ${renderBadge(isReturning ? "WELCOME BACK" : "MEET LUMI", "peach")}

      <h1>${isReturning ? `Ready when you are, ${firstName}.` : "A little light for every learning moment."}</h1>

      <p>${
        isReturning
          ? "Resume where you stopped, review your learning preferences, or begin a fresh journey. Nothing changes until you choose."
          : "Tell us a little about how you study. We’ll use your choices to make recommendations more relevant—and you can change them anytime."
      }</p>

      <div class="welcome-promises">
        <span>${renderIcon("check", 16)} <strong>${isReturning ? "Progress saved" : "About 2 minutes"}</strong></span>
        <span>${renderIcon("offline", 16)} <strong>Works offline</strong></span>
        <span>${renderIcon("edit", 16)} <strong>Always editable</strong></span>
      </div>

      ${
        isReturning
          ? `
        <div class="returning-actions">
          <button class="btn btn-primary" data-action="onboarding-resume">
            ${renderIcon("play", 18)}
            <span>Resume my learning</span>
          </button>
          <button class="btn btn-secondary" data-action="onboarding-step" data-step="1">
            ${renderIcon("edit", 18)}
            <span>Review personalization</span>
          </button>
          <button class="new-journey-button" data-action="confirm-new-journey">
            ${renderIcon("plus", 20)}
            <span>
              <strong>Start a new learning journey</strong>
              <small>Clear the saved profile and learning history on this device</small>
            </span>
            ${renderIcon("chevron", 18)}
          </button>
        </div>
      `
          : `
        <button class="btn btn-primary" data-action="onboarding-step" data-step="1">
          ${renderIcon("arrow", 18)}
          <span>Set up my learning space</span>
        </button>
        <button class="setup-skip" data-action="onboarding-skip">Explore with a sample profile</button>
      `
      }
    </main>
  `;
}

function renderStepAboutYou() {
  const availableInterests = [
    "Science & nature",
    "Math & logic",
    "History & culture",
    "Languages",
    "Technology",
    "Arts & creativity",
  ];
  const isValid = state.profile.name.trim().length > 0 && state.profile.subjects.length > 0;

  return `
    <main class="setup-card">
      <div class="setup-heading">
        ${renderBadge("ABOUT YOU", "blue")}
        <h1>Let’s make this space yours.</h1>
        <p>We only need enough detail to organize subjects and suggest useful next steps.</p>
      </div>

      <div class="setup-form">
        <label class="setup-field">
          <span>What should Lumi call you?</span>
          <input type="text" id="input-profile-name" value="${escapeHtml(state.profile.name)}" placeholder="Your name" />
        </label>

        <label class="setup-field">
          <span>Age range</span>
          <select id="select-profile-level">
            ${["Under 13", "13–17", "18–24", "25–34", "35–49", "50 or older", "Prefer not to say"]
              .map((level) => `<option value="${level}" ${state.profile.level === level ? "selected" : ""}>${level}</option>`)
              .join("")}
          </select>
        </label>

        <div class="setup-field">
          <span>Your interests <small>Choose up to four</small></span>
          <div class="choice-grid">
            ${availableInterests
              .map((interest) => {
                const selected = state.profile.subjects.includes(interest);
                return `
                <button type="button" class="${selected ? "selected" : ""}" data-action="toggle-subject" data-subject="${interest}">
                  <span>${interest.slice(0, 2)}</span>
                  ${interest}
                  ${selected ? renderIcon("check", 15) : ""}
                </button>
              `;
              })
              .join("")}
          </div>
          <input
            id="input-custom-interest"
            placeholder="Add another interest and press Enter…"
            ${state.profile.subjects.length >= 4 ? "disabled" : ""}
          />
        </div>
      </div>

      <div class="setup-actions">
        ${state.editingProfile ? `<button class="btn btn-ghost" data-action="cancel-setup">Cancel</button>` : ""}
        <button class="btn btn-secondary" data-action="onboarding-step" data-step="0">Back</button>
        <button class="btn btn-primary" data-action="onboarding-step" data-step="2" ${isValid ? "" : "disabled"}>
          <span>Analyze my device</span>
          ${renderIcon("arrow", 18)}
        </button>
      </div>
    </main>
  `;
}

function renderStepDeviceAnalysis() {
  const stage = state.onboarding.analysisStage;
  const models = [
    ["Llama 3.2 3B Instruct · Q4", "Recommended · Fast and responsive for tutoring, summaries, and flashcards.", "spark"],
    ["Phi-3.5 Mini · Q4", "Balanced · Strong reasoning in a compact model with comfortable memory headroom.", "layers"],
    ["Qwen2.5 7B Instruct · Q4", "Best quality · Uses more of the 6 GB VRAM and may respond more slowly.", "book"],
  ];
  const isComplete = stage >= 4;

  return `
    <main class="setup-card">
      <div class="setup-heading">
        ${renderBadge(isComplete ? "CHOOSE YOUR MODEL" : "ANALYZING DEVICE", "blue")}
        <h1>${isComplete ? "Select the local model you prefer." : "Finding the smoothest fit for your device."}</h1>
        <p>This prototype uses the device specifications you provided to compare models. No model is downloaded or installed during setup.</p>
      </div>

      <div class="panel automatic-analysis" aria-live="polite">
        ${
          !isComplete
            ? `
          <div class="analysis-orb">
            ${renderIcon("spark", 27)}
            <i></i>
          </div>
          <div class="analysis-copy">
            <p class="eyebrow">AUTOMATIC CHECK</p>
            <h3>Reading safe browser signals…</h3>
            <p>This takes only a moment.</p>
          </div>
          <div class="animated-analysis">
            ${[
              "Reading system and memory",
              "Checking GPU and VRAM",
              "Reviewing storage and CPU",
              "Matching compatible models",
            ]
              .map(
                (message, index) => `
              <div class="${stage > index ? "complete" : stage === index ? "active" : ""}">
                <span>${stage > index ? renderIcon("check", 14) : "<i></i>"}</span>
                <p>
                  <strong>${message}</strong>
                  <small>${stage > index ? "Complete" : stage === index ? "Analyzing…" : "Waiting"}</small>
                </p>
              </div>
            `
              )
              .join("")}
          </div>
        `
            : `
          <div>
            <div class="device-analysis-head">
              <span>${renderIcon("check", 20)}</span>
              <div>
                <p class="eyebrow">ANALYSIS COMPLETE</p>
                <h3>Your device can run compact and 7B quantized models.</h3>
              </div>
            </div>
            <div class="summary-stats">
              <span><strong>15.9 GB</strong><small>RAM</small></span>
              <span><strong>6 GB</strong><small>GTX 1660 SUPER VRAM</small></span>
              <span><strong>16</strong><small>CPU cores</small></span>
              <span><strong>52.1 GB</strong><small>Free storage</small></span>
              <span><strong>Windows 11</strong><small>Operating system</small></span>
              <span><strong>NVIDIA</strong><small>GPU acceleration</small></span>
            </div>
            <div class="section-heading">
              <div>
                <p class="eyebrow">COMPATIBLE MODELS</p>
                <h3>Choose one model</h3>
              </div>
              ${renderBadge(state.profile.modelPreference || "Not selected", "neutral")}
            </div>
            <div class="learning-styles">
              ${models
                .map(([name, copy, icon]) => {
                  const selected = state.profile.modelPreference === name;
                  return `
                  <button type="button" class="${selected ? "selected" : ""}" data-action="select-model" data-model="${name}">
                    <span>${renderIcon(icon, 20)}</span>
                    <div>
                      <strong>${name}</strong>
                      <p>${copy}</p>
                    </div>
                    <i>${selected ? renderIcon("check", 15) : ""}</i>
                  </button>
                `;
                })
                .join("")}
            </div>
          </div>
        `
        }
      </div>

      <div class="hardware-note">
        ${renderIcon("settings", 18)}
        <p><strong>Provided device profile</strong><br/>15.9 GB RAM · NVIDIA GeForce GTX 1660 SUPER · 6 GB VRAM · 16 CPU cores · 52.1 GB free · Windows 11.</p>
      </div>

      <div class="setup-actions">
        <button class="btn btn-secondary" data-action="onboarding-step" data-step="1">Back</button>
        <button class="btn btn-primary" data-action="onboarding-step" data-step="3" ${isComplete && state.profile.modelPreference ? "" : "disabled"}>
          <span>Use selected model</span>
          ${renderIcon("arrow", 18)}
        </button>
      </div>
    </main>
  `;
}

function renderStepTopic() {
  const method = state.onboarding.topicMethod;
  const isRec = state.onboarding.isRecording;
  const recSec = state.onboarding.recordingSeconds;
  const hasContent = state.profile.learningTopic.trim().length >= 2 || state.onboarding.topicFiles.length > 0;

  return `
    <main class="setup-card">
      <div class="completion-lumi topic-welcome-lumi">
        ${renderLumi("large")}
      </div>
      <div class="setup-heading">
        ${renderBadge("LUMI IS READY TO HELP", "peach")}
        <h1>Hi! What would you like to learn?</h1>
        <p>I’m happy you’re here. Type a topic, tell me by voice, show me a photo, or choose a file—we’ll take it one step at a time.</p>
      </div>

      <section class="setup-form">
        <div class="source-tabs" role="tablist" aria-label="Choose how to add a topic">
          <button type="button" class="${method === "text" ? "active" : ""}" data-action="set-topic-method" data-method="text">${renderIcon("edit", 16)} Text</button>
          <button type="button" class="${method === "voice" ? "active" : ""}" data-action="set-topic-method" data-method="voice">${renderIcon("mic", 16)} Voice</button>
          <button type="button" class="${method === "camera" ? "active" : ""}" data-action="set-topic-method" data-method="camera">${renderIcon("image", 16)} Camera</button>
          <button type="button" class="${method === "files" ? "active" : ""}" data-action="set-topic-method" data-method="files">${renderIcon("upload", 16)} File</button>
        </div>

        ${
          method === "text"
            ? `
          <label class="setup-field">
            <span>Topic you want to learn</span>
            <input type="text" id="input-learning-topic" value="${escapeHtml(state.profile.learningTopic)}" placeholder="For example: How solar panels work" />
          </label>
        `
            : ""
        }

        ${
          method === "voice"
            ? `
          <div class="drop-zone compact-drop-zone voice-recorder ${isRec ? "is-recording" : ""}">
            ${renderBadge(isRec ? `RECORDING · ${Math.floor(recSec / 60)}:${String(recSec % 60).padStart(2, "0")}` : "VOICE INPUT", isRec ? "peach" : "neutral")}
            <span class="drop-icon voice-mic">${renderIcon("mic", 24)}<i></i></span>
            <strong>${isRec ? "I’m listening…" : "Record your topic"}</strong>
            <p>${isRec ? "Describe what you want to learn. Speak naturally and stop when you’re finished." : "Use your microphone to tell Lumi what you want to learn."}</p>
            <div class="voice-waveform ${isRec ? "active" : ""}" aria-hidden="true">
              ${Array.from({ length: 24 }).map(() => "<i></i>").join("")}
            </div>
            ${
              isRec
                ? `<button type="button" class="btn btn-secondary" data-action="stop-recording">${renderIcon("stop", 16)} Stop recording</button>`
                : `<button type="button" class="btn btn-primary" data-action="start-recording">${renderIcon("mic", 16)} Start recording</button>`
            }
            ${state.onboarding.recordingError ? `<small class="recording-error" role="alert">${state.onboarding.recordingError}</small>` : `<small>Your browser will ask for microphone permission.</small>`}
          </div>
        `
            : ""
        }

        ${
          method === "camera"
            ? `
          <label class="drop-zone compact-drop-zone">
            <input type="file" accept="image/*" capture="environment" id="file-input-camera" />
            <span class="drop-icon">${renderIcon("image", 24)}</span>
            <strong>Open your camera</strong>
            <p>Take a photo of a page, object, diagram, or whiteboard.</p>
            <small>Uses your device camera when supported</small>
          </label>
        `
            : ""
        }

        ${
          method === "files"
            ? `
          <label class="drop-zone compact-drop-zone">
            <input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,image/*,audio/*" id="file-input-files" />
            <span class="drop-icon">${renderIcon("upload", 24)}</span>
            <strong>Choose a learning file</strong>
            <p>Documents, text, images, or audio</p>
            <small>Up to 4 files during onboarding</small>
          </label>
        `
            : ""
        }

        ${
          state.onboarding.topicFiles.length > 0
            ? `
          <div class="file-queue">
            ${state.onboarding.topicFiles
              .map(
                (file, index) => `
              <div>
                <span class="file-type">${file.type.slice(0, 4)}</span>
                <p>
                  <strong>${escapeHtml(file.name)}</strong>
                  <small>${file.size} · Topic source added</small>
                </p>
                <button type="button" data-action="remove-topic-file" data-index="${index}" aria-label="Remove ${escapeHtml(file.name)}">
                  ${renderIcon("close", 17)}
                </button>
              </div>
            `
              )
              .join("")}
          </div>
        `
            : ""
        }

        <div class="format-note">
          ${renderIcon("spark", 18)}
          <p><strong>Prototype capture</strong><br/>Voice, photos, and files are saved as source names only. Their contents are not analyzed or uploaded to an AI service.</p>
        </div>
      </section>

      <div class="setup-actions">
        <button class="btn btn-secondary" data-action="onboarding-step" data-step="2">Back</button>
        <button class="btn btn-primary" data-action="onboarding-step" data-step="4" ${hasContent ? "" : "disabled"}>
          <span>Choose learning style</span>
          ${renderIcon("arrow", 18)}
        </button>
      </div>
    </main>
  `;
}

function renderStepPersonalization() {
  const styles = [
    ["Learn", "Build understanding with key notes, explanations, and guided examples.", "book"],
    ["Practice", "Answer targeted questions and get immediate feedback on each concept.", "quiz"],
    ["Review", "Refresh earlier material with summaries, recall cards, and quick checks.", "cards"],
  ];

  return `
    <main class="setup-card">
      <div class="setup-heading">
        ${renderBadge("PERSONALIZATION", "peach")}
        <h1>How do you like to learn?</h1>
        <p>Choose a starting preference. Lumi can still explain something differently whenever you ask.</p>
      </div>

      <div class="learning-styles">
        ${styles
          .map(([title, copy, icon]) => {
            const selected =
              state.profile.learningStyle === title ||
              (title === "Learn" && state.profile.learningStyle === "Examples, then practice");
            return `
            <button type="button" class="${selected ? "selected" : ""}" data-action="select-learning-style" data-style="${title}">
              <span>${renderIcon(icon, 20)}</span>
              <div>
                <strong>${title}</strong>
                <p>${copy}</p>
              </div>
              <i>${selected ? renderIcon("check", 15) : ""}</i>
            </button>
          `;
          })
          .join("")}
      </div>

      <label class="personalization-toggle">
        <span>
          ${renderIcon("spark", 20)}
          <p>
            <strong>Personalized recommendations</strong>
            <small>Use saved quiz attempts, completed activities, and your preferences to suggest what to study next.</small>
          </p>
        </span>
        <input type="checkbox" id="check-personalization" ${state.profile.personalization ? "checked" : ""} />
        <i></i>
      </label>

      <div class="local-ai-note">
        ${renderIcon("offline", 18)}
        <p><strong>Local AI is not configured on this device.</strong><br/>Saved lessons, plans, flashcards, and supported quizzes still work offline. Live AI features require a connection.</p>
      </div>

      <div class="setup-actions">
        <button class="btn btn-secondary" data-action="onboarding-step" data-step="3">Back</button>
        <button class="btn btn-primary" data-action="finish-setup">
          ${renderIcon("check", 18)}
          <span>${state.editingProfile ? "Save preferences" : "Finish setup"}</span>
        </button>
      </div>
    </main>
  `;
}

// 2. Main Page Screens
function renderHomePage() {
  const firstName = state.profile.name.trim().split(" ")[0] || "Learner";
  const focusSubject = state.profile.subjects[0] || "Mathematics";

  return `
    <div class="page home-page">
      <section class="hero">
        <div class="hero-copy">
          ${renderBadge("WELCOME BACK", "peach")}
          <h2>Ready to learn, ${firstName}?</h2>
          <p>Start with ${focusSubject.toLowerCase()}, create new resources, or review your learning report.</p>
          <div class="hero-actions">
            <button class="btn btn-primary" data-action="go-page" data-page="planner">
              ${renderIcon("play", 18)}
              <span>Begin learning</span>
            </button>
            <span>Choose your study mode</span>
          </div>
        </div>
        <div class="hero-visual" aria-hidden="true">
          <div class="orbit orbit-one"></div>
          <div class="orbit orbit-two"></div>
          ${renderLumi("large")}
          <div class="float-card">
            ${renderIcon("spark", 16)}
            <span><strong>Lumi’s here.</strong> One step at a time.</span>
          </div>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <p class="eyebrow">START HERE</p>
            <h3>Choose your next step</h3>
          </div>
        </div>
        <div class="quick-grid">
          <button class="quick-card coral" data-action="go-page" data-page="ingest">
            <span class="quick-icon">${renderIcon("plus", 20)}</span>
            <span>
              <strong>Create Learning Resources</strong>
              <small>Turn text, voice, photos, or files into a learning set.</small>
            </span>
            ${renderIcon("arrow", 18)}
          </button>
          <button class="quick-card sage" data-action="go-page" data-page="planner">
            <span class="quick-icon">${renderIcon("play", 20)}</span>
            <span>
              <strong>Study Mode</strong>
              <small>Choose Learn, Practice, or Review and begin a focused session.</small>
            </span>
            ${renderIcon("arrow", 18)}
          </button>
          <button class="quick-card blue" data-action="go-page" data-page="report">
            <span class="quick-icon">${renderIcon("chart", 20)}</span>
            <span>
              <strong>Report Learning</strong>
              <small>See weekly progress, strengths, and topics that need more practice.</small>
            </span>
            ${renderIcon("arrow", 18)}
          </button>
        </div>
      </section>

      <div class="section-block">
        <section class="panel today-panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">SUGGESTED NEXT</p>
              <h3>Your study plan</h3>
            </div>
            <button class="text-button" data-action="go-page" data-page="planner">
              Open Study Mode ${renderIcon("chevron", 15)}
            </button>
          </div>
          <div class="timeline">
            <div class="timeline-item">
              <span class="timeline-dot">1</span>
              <div>
                <strong>Review cell structure</strong>
                <small>12 flashcards · suggested</small>
              </div>
              <span>20 min</span>
            </div>
            <div class="timeline-item current">
              <span class="timeline-dot">2</span>
              <div>
                <strong>Quadratic equations</strong>
                <small>Worked examples · up next</small>
                <div class="mini-progress"><span></span></div>
              </div>
              <span>25 min</span>
            </div>
            <div class="timeline-item">
              <span class="timeline-dot">3</span>
              <div>
                <strong>French Revolution</strong>
                <small>Summary + quick quiz</small>
              </div>
              <span>30 min</span>
            </div>
          </div>
        </section>
      </div>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <p class="eyebrow">SAVED FOR YOU</p>
            <h3>Pick up where you left off</h3>
          </div>
          <button class="text-button" data-action="go-page" data-page="lessons">
            View all ${renderIcon("arrow", 15)}
          </button>
        </div>
        <div class="resource-row">
          <button class="resource-card" data-action="go-page" data-page="notes">
            <span class="subject-art biology">${renderIcon("book", 30)}</span>
            <span>
              ${renderBadge("Biology")}
              <strong>Cell division & mitosis</strong>
              <small>${renderIcon("clock", 14)} Key notes · demo source</small>
            </span>
          </button>
          <button class="resource-card" data-action="go-page" data-page="flashcards">
            <span class="subject-art maths">${renderIcon("cards", 30)}</span>
            <span>
              ${renderBadge("Biology", "peach")}
              <strong>Mitosis recall cards</strong>
              <small>${renderIcon("cards", 14)} 3 flashcards · offline</small>
            </span>
          </button>
          <button class="resource-card" data-action="go-page" data-page="quiz">
            <span class="subject-art history">${renderIcon("quiz", 30)}</span>
            <span>
              ${renderBadge("Biology", "blue")}
              <strong>Cell division reviewer</strong>
              <small>${renderIcon("quiz", 14)} Practice quiz · 3 questions</small>
            </span>
          </button>
        </div>
      </section>
    </div>
  `;
}

function renderTutorPage() {
  const messages = state.tutor.messages;

  return `
    <div class="tutor-layout">
      <section class="chat-area">
        <div class="chat-intro">
          ${renderLumi("medium")}
          <div>
            ${renderBadge(state.online ? "LUMI · AI TUTOR ONLINE" : "LUMI · LIVE HELP UNAVAILABLE", state.online ? "sage" : "neutral")}
            <h2>Let’s figure this out together.</h2>
            <p>Ask Lumi a question, or choose a quick way to continue.</p>
          </div>
        </div>

        <div class="messages">
          ${messages
            .map(
              (m, i) => `
            <div class="message-row ${m.role}">
              ${m.role === "tutor" ? renderLumi("small") : ""}
              <div class="message-bubble">
                <p>${escapeHtml(m.text)}</p>
                ${
                  m.detail
                    ? `
                  <div class="worked-example">
                    <strong>Worked example</strong>
                    <p>${escapeHtml(m.detail)}</p>
                  </div>
                `
                    : ""
                }
                ${
                  m.role === "tutor" && i === 1
                    ? `
                  <button class="disclosure" data-action="toggle-tutor-detail">
                    ${state.tutor.detailOpen ? "Hide" : "Show"} why this works ${renderIcon("chevron", 14)}
                  </button>
                  ${
                    state.tutor.detailOpen
                      ? `<p class="detail-copy">Adding and subtracting the same amount preserves equality. Both sides change equally, so the relationship stays true.</p>`
                      : ""
                  }
                `
                    : ""
                }
              </div>
            </div>
          `
            )
            .join("")}
        </div>

        <div class="suggestion-row">
          <button data-action="send-suggestion" data-text="Explain it simply">Explain it simply</button>
          <button data-action="send-suggestion" data-text="Show me another example">Show me another example</button>
          <button data-action="send-suggestion" data-text="Test my understanding">Test my understanding</button>
        </div>

        <form class="composer" id="tutor-form">
          <button type="button" class="composer-icon" data-action="go-page" data-page="ingest" aria-label="Add learning material">
            ${renderIcon("plus", 18)}
          </button>
          <input
            id="tutor-input"
            value="${escapeHtml(state.tutor.input)}"
            placeholder="Ask a follow-up question…"
            aria-label="Tutor question"
          />
          <button
            type="button"
            class="composer-icon"
            aria-label="Use voice input"
            title="${state.online ? "Voice input prototype" : "Voice unavailable offline"}"
            data-action="voice-prototype"
          >
            ${renderIcon("mic", 18)}
          </button>
          <button type="submit" class="send-button" aria-label="Send question">
            ${renderIcon("send", 18)}
          </button>
        </form>

        <p class="prototype-note">Demo tutor responses are pre-written for this prototype; no live AI model is connected.</p>
      </section>

      <aside class="context-panel">
        <p class="eyebrow">CURRENT CONTEXT</p>
        <h3>Quadratic equations</h3>
        <div class="context-meta">
          <span>${renderIcon("book", 16)} Mathematics</span>
          <span>${renderIcon("clock", 16)} Studying 14 min</span>
        </div>
        <hr />
        <p class="eyebrow">SAVE THIS EXPLANATION AS</p>
        <button class="context-action" data-action="go-page" data-page="flashcards">
          ${renderIcon("cards", 18)}
          <span>
            <strong>Flashcards</strong>
            <small>3 suggested cards</small>
          </span>
          ${renderIcon("plus", 18)}
        </button>
        <button class="context-action" data-action="go-page" data-page="quiz">
          ${renderIcon("quiz", 18)}
          <span>
            <strong>Quick practice</strong>
            <small>4 understanding checks</small>
          </span>
          ${renderIcon("plus", 18)}
        </button>
        <div class="support-note">
          ${renderIcon("download", 18)}
          <p><strong>Available offline</strong><br/>Saved cards and quizzes work without a connection.</p>
        </div>
      </aside>
    </div>
  `;
}

function renderPlannerPage() {
  const pStep = state.planner.step;
  const studyMode = state.planner.studyMode;
  const selected = state.planner.selectedMaterials;

  const modeDetails = [
    { name: "Learn", icon: "book", copy: "Build understanding with key notes, explanations, and guided examples." },
    { name: "Practice", icon: "quiz", copy: "Answer targeted questions and get immediate feedback on each concept." },
    { name: "Review", icon: "cards", copy: "Refresh earlier material with summaries, recall cards, and quick checks." },
  ];

  const materialOptions = [
    { name: "Notes Summary / Key Notes", icon: "book", copy: "Load concise summaries, definitions, and important takeaways.", time: 10, tone: "sage" },
    { name: "Flashcards", icon: "cards", copy: "Load question-and-answer cards for active recall.", time: 10, tone: "coral" },
    { name: "Quizzes / Exam / Reviewer", icon: "quiz", copy: "Load practice questions, reviewer items, and answer checks.", time: 15, tone: "blue" },
  ];

  const loaded = materialOptions.filter((m) => selected.includes(m.name));
  const totalMinutes = loaded.reduce((sum, m) => sum + m.time, 0);
  const stepTitles = ["Choose your study mode", "Choose learning materials", "Review your session"];

  return `
    <div class="page planner-page">
      <section class="planner-head">
        <div>
          ${renderBadge("STUDY MODE", "peach")}
          <h2>${stepTitles[pStep]}</h2>
          <p>Complete one simple step at a time.</p>
        </div>
        ${
          pStep === 2
            ? `
          <div class="duration-card">
            ${renderIcon("clock", 20)}
            <span>
              <small>ESTIMATED TIME</small>
              <strong>${totalMinutes} min</strong>
            </span>
          </div>
        `
            : ""
        }
      </section>

      <section class="panel topic-panel">
        <div class="section-heading">
          <div>
            <p class="eyebrow">STEP ${pStep + 1} OF 3</p>
            <h3>${stepTitles[pStep]}</h3>
          </div>
          ${renderBadge(`${Math.round(((pStep + 1) / 3) * 100)}%`, "neutral")}
        </div>
        <div class="onboarding-progress" aria-label="Study setup step ${pStep + 1} of 3">
          <span style="width: ${((pStep + 1) / 3) * 100}%"></span>
        </div>
      </section>

      ${
        pStep === 0
          ? `
        <section class="panel topic-panel section-block">
          <div class="section-heading">
            <div>
              <p class="eyebrow">CHOOSE ONE</p>
              <h3>How do you want to study?</h3>
            </div>
            ${renderBadge(studyMode, "neutral")}
          </div>
          <div class="learning-styles">
            ${modeDetails
              .map(
                (mode) => `
              <button class="${studyMode === mode.name ? "selected" : ""}" data-action="set-study-mode" data-mode="${mode.name}">
                <span>${renderIcon(mode.icon, 20)}</span>
                <div>
                  <strong>${mode.name}</strong>
                  <p>${mode.copy}</p>
                </div>
                <i>${studyMode === mode.name ? renderIcon("check", 15) : ""}</i>
              </button>
            `
              )
              .join("")}
          </div>
          <div class="setup-actions">
            <button class="btn btn-primary" data-action="planner-step" data-step="1">
              <span>Choose topics</span>
              ${renderIcon("arrow", 18)}
            </button>
          </div>
        </section>
      `
          : ""
      }

      ${
        pStep === 1
          ? `
        <section class="panel topic-panel section-block">
          <div class="section-heading">
            <div>
              <p class="eyebrow">LOAD FOR STUDY</p>
              <h3>Which materials do you want?</h3>
            </div>
            ${renderBadge(`${selected.length} selected`, "neutral")}
          </div>
          <p class="muted">Choose one or more saved resources to use in this session.</p>
          <div class="learning-styles">
            ${materialOptions
              .map((mat) => {
                const isSel = selected.includes(mat.name);
                return `
                <button class="${isSel ? "selected" : ""}" data-action="toggle-material" data-material="${mat.name}">
                  <span>${renderIcon(mat.icon, 20)}</span>
                  <div>
                    <strong>${mat.name}</strong>
                    <p>${mat.copy}</p>
                  </div>
                  <i>${isSel ? renderIcon("check", 15) : ""}</i>
                </button>
              `;
              })
              .join("")}
          </div>
          <div class="setup-actions">
            <button class="btn btn-secondary" data-action="planner-step" data-step="0">Back</button>
            <button class="btn btn-primary" data-action="planner-step" data-step="2" ${selected.length > 0 ? "" : "disabled"}>
              <span>Review plan</span>
              ${renderIcon("arrow", 18)}
            </button>
          </div>
        </section>
      `
          : ""
      }

      ${
        pStep === 2
          ? `
        <section class="panel schedule-panel section-block">
          <div class="section-heading">
            <div>
              <p class="eyebrow">${studyMode.toUpperCase()} SESSION</p>
              <h3>Materials ready to load</h3>
            </div>
            <span class="time-total">${renderIcon("clock", 16)} ${totalMinutes} min</span>
          </div>
          <div class="schedule-list">
            ${loaded
              .map(
                (mat) => `
              <div class="schedule-item">
                <span class="schedule-index ${mat.tone}">${renderIcon(mat.icon, 15)}</span>
                <span>
                  <strong>${mat.name}</strong>
                  <small>${mat.copy}</small>
                </span>
                <div class="schedule-time">
                  <strong>${mat.time}</strong>
                  <small>min</small>
                </div>
                ${renderIcon("check", 17)}
              </div>
            `
              )
              .join("")}
          </div>
          <div class="planner-reason">
            ${renderIcon("spark", 18)}
            <p><strong>${studyMode} mode selected.</strong> Study Mode will load only the ${selected.length === 1 ? "resource" : "resources"} you selected.</p>
          </div>
          <div class="setup-actions">
            <button class="btn btn-secondary" data-action="planner-step" data-step="1">Back</button>
            <button class="btn btn-primary" data-action="go-page" data-page="focus">
              ${renderIcon("play", 18)}
              <span>Start ${studyMode.toLowerCase()} session</span>
            </button>
          </div>
        </section>
      `
          : ""
      }
    </div>
  `;
}

function renderFocusPage() {
  const step = state.focus.step;
  const paused = state.focus.paused;
  const flipped = state.focus.flipped;
  const answer = state.focus.answer;

  return `
    <div class="focus-shell">
      <header class="focus-header">
        <button class="brand" data-action="go-page" data-page="library">
          <span class="brand-mark">${renderIcon("spark", 18)}</span>
          <span>Lumi</span>
        </button>
        <div class="focus-progress">
          <span>
            <strong>Quadratic equations</strong>
            <small>Activity ${step + 1} of 3 · ${25 - step * 8} min remaining</small>
          </span>
          <div>
            <i style="width: ${(step + 1) * 33}%"></i>
          </div>
        </div>
        <button class="btn btn-secondary" data-action="toggle-focus-pause">
          ${renderIcon(paused ? "play" : "pause", 18)}
          <span>${paused ? "Resume" : "Pause"}</span>
        </button>
      </header>

      <main class="focus-main">
        ${
          paused
            ? `
          <div class="pause-state">
            <div class="complete-mark">${renderIcon("pause", 28)}</div>
            <h2>Session paused.</h2>
            <p>Take the time you need. Your place is saved on this device.</p>
            <button class="btn btn-primary" data-action="toggle-focus-pause">
              ${renderIcon("play", 18)}
              <span>Resume when ready</span>
            </button>
          </div>
        `
            : `
          <div class="focus-kicker">
            <span>ACTIVITY ${step + 1}</span>
            ${renderBadge(step === 0 ? "CONCEPT" : step === 1 ? "FLASHCARD" : "QUICK CHECK", "blue")}
          </div>

          ${
            step === 0
              ? `
            <article class="learning-card">
              <p class="eyebrow">THE KEY IDEA</p>
              <h2>Undo each operation in reverse order.</h2>
              <p>To isolate <b>x</b>, treat the equation like a wrapped gift. Remove the outermost “layer” first, and do the same thing to both sides.</p>
              <div class="equation">
                <span>2x + 6 = 18</span>
                ${renderIcon("arrow", 18)}
                <span>2x = 12</span>
                ${renderIcon("arrow", 18)}
                <span>x = 6</span>
              </div>
              <div class="callout">
                ${renderIcon("spark", 18)}
                <p><strong>Notice the order:</strong> subtract 6 first, then divide by 2. This reverses the original operations.</p>
              </div>
            </article>
          `
              : ""
          }

          ${
            step === 1
              ? `
            <button class="flashcard ${flipped ? "flipped" : ""}" data-action="flip-focus-card">
              <span class="eyebrow">${flipped ? "ANSWER" : "TAP TO REVEAL"}</span>
              <strong>${flipped ? "Apply the inverse operation to both sides." : "How do you keep an equation balanced?"}</strong>
              <small>${flipped ? "Whatever you do to one side, do to the other." : "Think about the balance-scale analogy."}</small>
            </button>
          `
              : ""
          }

          ${
            step === 2
              ? `
            <article class="learning-card quiz-card">
              <p class="eyebrow">TRY THIS</p>
              <h2>What is the first step to solve 3x − 4 = 11?</h2>
              ${["Divide both sides by 3", "Add 4 to both sides", "Subtract 11 from both sides"]
                .map(
                  (opt, i) => `
                <button class="answer-option ${answer === i ? "selected" : ""}" data-action="select-focus-answer" data-index="${i}">
                  <span>${String.fromCharCode(65 + i)}</span>
                  ${opt}
                </button>
              `
                )
                .join("")}
            </article>
          `
              : ""
          }

          <div class="focus-footer">
            <p>${step === 0 ? "Read at your own pace." : step === 1 ? "Retrieval practice strengthens memory." : "Choose the best first step."}</p>
            <button
              class="btn btn-primary"
              data-action="focus-next"
              ${step === 2 && answer === null ? "disabled" : ""}
            >
              <span>${step === 2 ? "Finish session" : "Next"}</span>
              ${renderIcon("arrow", 18)}
            </button>
          </div>
        `
        }
      </main>
    </div>
  `;
}

function renderLessonsPage() {
  const stage = state.lessons.stage;
  const paused = state.lessons.paused;
  const cardsReady = state.lessons.cards;

  return `
    <div class="page lessons-page">
      <div class="lesson-layout">
        <aside class="lesson-library panel">
          <div class="section-heading">
            <div>
              <p class="eyebrow">MY LESSONS</p>
              <h3>Saved lessons</h3>
            </div>
            <button class="square-button" data-action="go-page" data-page="ingest" aria-label="Add study material">
              ${renderIcon("plus", 18)}
            </button>
          </div>
          <button class="btn btn-soft full-button lesson-add" data-action="go-page" data-page="ingest">
            ${renderIcon("upload", 18)}
            <span>Add study material</span>
          </button>
          <div class="search-box">
            ${renderIcon("search", 17)}
            <input placeholder="Search lessons…" aria-label="Search lessons" id="lesson-search-input" />
          </div>
          <button class="lesson-list-item active">
            <span class="subject-dot biology"></span>
            <span>
              <strong>Cell division & mitosis</strong>
              <small>Biology · Today</small>
            </span>
            ${renderBadge("Saved")}
          </button>
          <button class="lesson-list-item">
            <span class="subject-dot maths"></span>
            <span>
              <strong>Quadratic functions</strong>
              <small>Maths · Monday</small>
            </span>
          </button>
          <button class="lesson-list-item">
            <span class="subject-dot history"></span>
            <span>
              <strong>Industrial Revolution</strong>
              <small>History · May 16</small>
            </span>
          </button>
        </aside>

        <section class="lesson-main">
          ${
            stage === "consent"
              ? `
            <div class="consent-card panel">
              <div class="record-illustration">
                ${renderIcon("mic", 30)}
                <i></i>
              </div>
              ${renderBadge("BEFORE YOU RECORD", "peach")}
              <h2>Make sure everyone is comfortable.</h2>
              <p>Only record after your teacher and anyone speaking have clearly agreed. Recording rules may differ at your school or location.</p>
              <label class="consent-check">
                <input type="checkbox" id="lesson-consent-check" />
                <span>${renderIcon("check", 15)}</span>
                <strong>I have permission from everyone being recorded.</strong>
              </label>
              <div class="consent-actions">
                <button class="btn btn-primary" data-action="lesson-start-recording">
                  ${renderIcon("mic", 18)}
                  <span>Start recording</span>
                </button>
                <button class="btn btn-secondary" data-action="go-page" data-page="ingest">
                  ${renderIcon("upload", 18)}
                  <span>Add notes or files</span>
                </button>
              </div>
              <p class="prototype-note">Prototype only: microphone capture and transcription are not connected.</p>
            </div>
          `
              : ""
          }

          ${
            stage === "recording"
              ? `
            <div class="recording-card panel">
              ${renderBadge(`<span class="record-dot"></span> ${paused ? "PAUSED" : "RECORDING"}`, "peach")}
              <div class="timer">08:42</div>
              <p>Biology · Cell division</p>
              <div class="waveform ${paused ? "paused" : ""}">
                ${Array.from({ length: 42 })
                  .map((_, i) => `<i style="height: ${16 + ((i * 17) % 52)}%"></i>`)
                  .join("")}
              </div>
              <div class="record-controls">
                <button type="button" data-action="lesson-toggle-pause">
                  ${renderIcon(paused ? "play" : "pause", 24)}
                  <span>${paused ? "Resume" : "Pause"}</span>
                </button>
                <button type="button" class="stop-control" data-action="lesson-stop-recording">
                  ${renderIcon("stop", 24)}
                  <span>Stop & save</span>
                </button>
              </div>
              <p class="prototype-note">Visual recording demo only. No audio is being captured.</p>
            </div>
          `
              : ""
          }

          ${
            stage === "notes"
              ? `
            <div class="notes-view">
              <div class="notes-head">
                <div>
                  ${renderBadge("Biology · Saved on device")}
                  <h2>Cell division & mitosis</h2>
                  <p>Today, 10:20 AM · 32 min lesson</p>
                </div>
                <button class="btn btn-secondary">
                  ${renderIcon("download", 16)}
                  <span>Available offline</span>
                </button>
              </div>
              <div class="notes-grid">
                <article class="panel generated-notes">
                  <p class="eyebrow">DEMO GENERATED NOTES</p>
                  <h3>Lesson summary</h3>
                  <p>Cell division allows organisms to grow, repair tissue, and reproduce. Mitosis creates two genetically identical daughter cells through a sequence of distinct phases.</p>
                  <h3>Key concepts</h3>
                  <ul>
                    <li><strong>Interphase:</strong> The cell grows and copies its DNA before division.</li>
                    <li><strong>Mitosis:</strong> Prophase, metaphase, anaphase, and telophase.</li>
                    <li><strong>Cytokinesis:</strong> The cytoplasm divides to form two cells.</li>
                  </ul>
                  <div class="transcript-preview">
                    <span>12:18</span>
                    <p>“During metaphase, the chromosomes line up at the cell’s equator…”</p>
                  </div>
                </article>
                <aside class="stack">
                  <div class="panel create-materials">
                    <p class="eyebrow">STUDY MATERIALS</p>
                    <button data-action="lesson-generate-cards">
                      ${renderIcon("cards", 20)}
                      <span>
                        <strong>Generate flashcards</strong>
                        <small>8 key concepts found</small>
                      </span>
                      ${renderIcon("arrow", 18)}
                    </button>
                    <button data-action="go-page" data-page="quiz">
                      ${renderIcon("quiz", 20)}
                      <span>
                        <strong>Create a practice quiz</strong>
                        <small>6 suggested questions</small>
                      </span>
                      ${renderIcon("arrow", 18)}
                    </button>
                  </div>
                  ${
                    cardsReady
                      ? `
                    <div class="panel success-card">
                      <span>${renderIcon("check", 16)}</span>
                      <div>
                        <strong>8 demo flashcards ready</strong>
                        <p>Saved with this lesson for offline study.</p>
                      </div>
                    </div>
                  `
                      : ""
                  }
                  <div class="panel availability">
                    ${renderIcon(state.online ? "wifi" : "offline", 20)}
                    <p>
                      <strong>${state.online ? "Online processing available" : "Offline limitation"}</strong><br/>
                      ${state.online ? "In a connected product, transcription could process now." : "New transcription requires a connection. Saved notes remain available."}
                    </p>
                  </div>
                </aside>
              </div>
            </div>
          `
              : ""
          }
        </section>
      </div>
    </div>
  `;
}

function renderIngestionPage() {
  const stage = state.ingest.stage;
  const topic = state.ingest.topic;
  const notes = state.ingest.notes;
  const files = state.ingest.files;
  const method = state.ingest.inputMethod;

  const wordCount = notes.trim() ? notes.trim().split(/\s+/).length : 0;
  const chunkCount = Math.max(1, Math.ceil(wordCount / 350) + files.length);
  const hasContent = topic.trim().length >= 2 && (notes.trim().length >= 20 || files.length > 0);

  if (stage === "ready") {
    return `
      <div class="page ingestion-page">
        <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
        <section class="ingest-success panel">
          <div class="complete-mark">${renderIcon("check", 30)}</div>
          ${renderBadge("CONTENT READY")}
          <h2>Your topic is ready.</h2>
          <p>Your captured material is linked to “${escapeHtml(topic)}” and ready for the next prototype step. Audio, images, and documents were not parsed, and no AI resources were generated.</p>
          <div class="ingest-results">
            <span><strong>1</strong><small>Topic added</small></span>
            <span><strong>${files.length + (notes.trim() ? 1 : 0)}</strong><small>Sources added</small></span>
            <span><strong>${chunkCount}</strong><small>Planned sections</small></span>
          </div>
          <div class="pipeline-summary">
            <div>
              <span>${renderIcon("check", 15)}</span>
              <p><strong>Material captured</strong><small>${files.length} file${files.length === 1 ? "" : "s"} · ${wordCount} written words</small></p>
            </div>
            <i></i>
            <div>
              <span>${renderIcon("check", 15)}</span>
              <p><strong>Topic linked</strong><small>${escapeHtml(topic)}</small></p>
            </div>
            <i></i>
            <div>
              <span>${renderIcon(state.online ? "wifi" : "offline", 15)}</span>
              <p>
                <strong>Generation is optional</strong>
                <small>${state.online ? "A connected model would be needed next" : "Wait for a connection or configured local AI"}</small>
              </p>
            </div>
          </div>
          <div class="success-actions">
            <button class="btn btn-primary" data-action="go-page" data-page="generation">
              ${renderIcon("spark", 18)}
              <span>Choose learning resources</span>
            </button>
            <button class="btn btn-secondary" data-action="go-page" data-page="library">
              ${renderIcon("book", 18)}
              <span>Save without generating</span>
            </button>
            <button class="btn btn-ghost" data-action="reset-ingestion">
              ${renderIcon("plus", 18)}
              <span>Add another</span>
            </button>
          </div>
        </section>
      </div>
    `;
  }

  return `
    <div class="page ingestion-page">
      <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
      <section class="ingest-head">
        <div>
          ${renderBadge("NEW LEARNING SET", "blue")}
          <h2>What would you like to learn?</h2>
          <p>Name the topic, then add free text, record your voice, use your camera, or upload a file.</p>
        </div>
        <div class="ingest-steps" aria-label="Ingestion progress">
          <span class="active"><i>1</i>Topic & material</span>
          <span><i>2</i>Ready</span>
        </div>
      </section>

      <div class="ingestion-grid">
        <section class="panel ingest-source">
          <label class="setup-field">
            <span>Topic</span>
            <input type="text" id="ingest-topic-input" value="${escapeHtml(topic)}" placeholder="For example: Cell division, budgeting, or Spanish basics" />
          </label>
          <div class="source-tabs" role="tablist">
            <button type="button" class="${method === "text" ? "active" : ""}" data-action="set-ingest-method" data-method="text">${renderIcon("edit", 16)} Text</button>
            <button type="button" class="${method === "voice" ? "active" : ""}" data-action="set-ingest-method" data-method="voice">${renderIcon("mic", 16)} Voice</button>
            <button type="button" class="${method === "camera" ? "active" : ""}" data-action="set-ingest-method" data-method="camera">${renderIcon("image", 16)} Camera</button>
            <button type="button" class="${method === "files" ? "active" : ""}" data-action="set-ingest-method" data-method="files">${renderIcon("upload", 16)} Files</button>
          </div>

          ${
            method === "text"
              ? `
            <div class="notes-input">
              <label for="material-notes">Free text</label>
              <textarea id="material-notes" placeholder="Paste notes, write an explanation, or add the information you want to study…\n\nTip: include enough detail for useful notes, flashcards, and questions.">${escapeHtml(notes)}</textarea>
              <span>${wordCount} words</span>
            </div>
          `
              : ""
          }

          ${
            method === "voice"
              ? `
            <label class="drop-zone compact-drop-zone">
              <input type="file" accept="audio/*" capture="user" id="ingest-voice-file" />
              <span class="drop-icon">${renderIcon("mic", 24)}</span>
              <strong>Record a voice command</strong>
              <p>Tell Lumi what you want to learn or explain what you already know.</p>
              <small>Uses your device’s recorder when supported · microphone permission may be requested</small>
            </label>
          `
              : ""
          }

          ${
            method === "camera"
              ? `
            <label class="drop-zone compact-drop-zone">
              <input type="file" accept="image/*" capture="environment" id="ingest-camera-file" />
              <span class="drop-icon">${renderIcon("image", 24)}</span>
              <strong>Open your camera</strong>
              <p>Take a photo of a page, diagram, object, or whiteboard.</p>
              <small>Uses your device’s camera when supported · camera permission may be requested</small>
            </label>
          `
              : ""
          }

          ${
            method === "files"
              ? `
            <label class="drop-zone compact-drop-zone">
              <input type="file" multiple accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,image/*,audio/*" id="ingest-multi-files" />
              <span class="drop-icon">${renderIcon("upload", 24)}</span>
              <strong>Browse files</strong>
              <p>PDF, DOCX, PPTX, TXT, Markdown, images, or audio</p>
              <small>Up to 6 files · selected files can be removed before continuing</small>
            </label>
          `
              : ""
          }

          ${
            files.length > 0
              ? `
            <div class="file-queue">
              ${files
                .map(
                  (file, idx) => `
                <div>
                  <span class="file-type">${file.type.slice(0, 4)}</span>
                  <p>
                    <strong>${escapeHtml(file.name)}</strong>
                    <small>${file.size} · Ready to add</small>
                  </p>
                  <button type="button" data-action="remove-ingest-file" data-index="${idx}" aria-label="Remove ${escapeHtml(file.name)}">
                    ${renderIcon("close", 17)}
                  </button>
                </div>
              `
                )
                .join("")}
            </div>
          `
              : ""
          }

          <div class="format-note">
            ${renderIcon("file", 18)}
            <p><strong>Prototype capture</strong><br/>Text is kept in this session. Audio, photos, and files can be selected and reviewed, but are not transcribed, analyzed, or uploaded to an AI service.</p>
          </div>
        </section>

        <aside class="panel ingest-help">
          <div class="icon-tile">${renderIcon("spark", 20)}</div>
          <p class="eyebrow">CHOOSE YOUR WAY</p>
          <h3>Show or tell Lumi.</h3>
          <div class="help-step">
            <span>1</span>
            <p><strong>Name the topic</strong><small>Use any subject, skill, or idea you want to learn.</small></p>
          </div>
          <div class="help-step">
            <span>2</span>
            <p><strong>Add learning material</strong><small>Type, speak, take a photo with your camera, or choose a saved file.</small></p>
          </div>
          <div class="availability">
            ${renderIcon(state.online ? "wifi" : "offline", 20)}
            <p>
              <strong>${state.online ? "Online" : "Working offline"}</strong><br/>
              ${state.online ? "Selected material can enter the prototype workflow." : "You can capture material now. New AI processing is unavailable."}
            </p>
          </div>
        </aside>

        <div class="ingest-footer">
          <p>${hasContent ? "Your topic and learning material are ready." : "Add a topic, then type, record, capture, or upload learning material."}</p>
          <button class="btn btn-primary" data-action="prepare-material" ${hasContent ? "" : "disabled"}>
            ${renderIcon("check", 18)}
            <span>Prepare material</span>
          </button>
        </div>
      </div>
    </div>
  `;
}

function renderGenerationPage() {
  const selected = state.generation.selected;
  const prepared = state.generation.prepared;

  const resources = [
    { id: "notes", icon: "book", title: "Key notes", copy: "Important concepts, definitions, and takeaways" },
    { id: "cards", icon: "cards", title: "Flashcards", copy: "Short question-and-answer recall cards" },
    { id: "quiz", icon: "quiz", title: "Quiz & reviewer", copy: "Practice questions with explanations" },
  ];

  return `
    <div class="page workflow-page">
      <button class="back-link" data-action="go-page" data-page="ingest">← Back to imported material</button>
      <section class="workflow-hero">
        <div>
          ${renderBadge("PROTOTYPE GENERATION", "peach")}
          <h2>What should Lumi prepare?</h2>
          <p>Select the resources you want. This prototype uses clearly labeled sample content; no local or cloud AI model is connected.</p>
        </div>
        ${renderLumi("medium")}
      </section>

      <div class="generation-layout">
        <section class="panel generation-card">
          <div class="section-heading">
            <div>
              <p class="eyebrow">LEARNING RESOURCES</p>
              <h3>Choose one or more</h3>
            </div>
            ${renderBadge(`${selected.length} selected`, "neutral")}
          </div>

          <div class="resource-select-list">
            ${resources
              .map((res) => {
                const isSel = selected.includes(res.id);
                return `
                <button class="${isSel ? "selected" : ""}" data-action="toggle-generation-res" data-id="${res.id}">
                  <span>${renderIcon(res.icon, 20)}</span>
                  <span>
                    <strong>${res.title}</strong>
                    <small>${res.copy}</small>
                  </span>
                  <i>${isSel ? renderIcon("check", 15) : ""}</i>
                </button>
              `;
              })
              .join("")}
          </div>

          ${
            !state.online
              ? `
            <div class="status-callout warning">
              ${renderIcon("offline", 18)}
              <p><strong>New generation is unavailable offline.</strong><br/>Reconnect or configure a genuine local model. Saved resources remain available.</p>
            </div>
          `
              : ""
          }

          ${
            prepared
              ? `
            <div class="generation-progress" aria-live="polite">
              ${resources
                .filter((r) => selected.includes(r.id))
                .map(
                  (r) => `
                <div>
                  <span>${renderIcon("check", 15)}</span>
                  <p>
                    <strong>${r.title}</strong>
                    <small>Sample resource prepared from the Cell division demo source</small>
                  </p>
                  ${renderBadge("Ready")}
                </div>
              `
                )
                .join("")}
            </div>
          `
              : ""
          }

          <div class="generation-actions">
            ${
              !prepared
                ? `
              <button class="btn btn-primary" data-action="prepare-sample-resources" ${state.online && selected.length > 0 ? "" : "disabled"}>
                ${renderIcon("spark", 18)}
                <span>Prepare sample resources</span>
              </button>
            `
                : `
              <button class="btn btn-primary" data-action="go-page" data-page="library">
                <span>Open learning set</span>
                ${renderIcon("arrow", 18)}
              </button>
            `
            }
          </div>
        </section>

        <aside class="panel source-proof">
          <p class="eyebrow">SOURCE BOUNDARY</p>
          <h3>Grounded in your material</h3>
          <p>The demo resources are tied to the built-in Cell division lesson and are labeled as samples. Uploaded files are not parsed in this prototype.</p>
          <div>
            ${renderIcon("file", 20)}
            <span>
              <strong>Biology lesson notes</strong>
              <small>Cell division & mitosis · demo source</small>
            </span>
          </div>
          <div>
            ${renderIcon("offline", 20)}
            <span>
              <strong>Offline after saving</strong>
              <small>Prepared samples stay available in this browser session</small>
            </span>
          </div>
        </aside>
      </div>
    </div>
  `;
}

function renderResourceLibraryPage() {
  const filter = state.library.filter;
  const actions = [
    { id: "notes", label: "Key notes", icon: "book", page: "notes", meta: "4 sections" },
    { id: "cards", label: "Flashcards", icon: "cards", page: "flashcards", meta: "6 cards" },
    { id: "quiz", label: "Quiz & reviewer", icon: "quiz", page: "quiz", meta: "3 questions" },
  ];

  return `
    <div class="page library-page">
      <section class="workflow-hero">
        <div>
          ${renderBadge("LEARNING RESOURCES", "blue")}
          <h2>Everything you need, in one learning set.</h2>
          <p>Open saved material, continue studying, or create a new set from your own notes and files.</p>
        </div>
        <button class="btn btn-primary" data-action="go-page" data-page="ingest">
          ${renderIcon("plus", 18)}
          <span>Create learning set</span>
        </button>
      </section>

      <div class="library-tabs" role="tablist">
        ${[
          ["all", "All resources"],
          ["notes", "Notes"],
          ["cards", "Flashcards"],
          ["quiz", "Quizzes"],
        ]
          .map(
            ([id, label]) => `
          <button class="${filter === id ? "active" : ""}" data-action="set-library-filter" data-filter="${id}">${label}</button>
        `
          )
          .join("")}
      </div>

      <section class="panel learning-set">
        <div class="learning-set-head">
          <div class="set-art">${renderIcon("book", 28)}</div>
          <div>
            <span>
              ${renderBadge("Biology")}
              ${renderBadge("Available offline", "neutral")}
            </span>
            <h3>Cell division & mitosis</h3>
            <p>Source: Biology lesson notes · Updated today · Version 1</p>
          </div>
          <button class="btn btn-primary" data-action="go-page" data-page="focus">
            ${renderIcon("play", 18)}
            <span>Start studying</span>
          </button>
        </div>

        <div class="set-progress">
          <span>
            <strong>Learning progress</strong>
            <small>${state.attempts.length > 0 ? "Completed recent assessment" : "No completed quiz yet"}</small>
          </span>
          <div>
            <i style="width: ${state.attempts.length > 0 ? "100%" : "0%"}"></i>
          </div>
          <button data-action="go-page" data-page="knowledge">
            View knowledge map ${renderIcon("arrow", 15)}
          </button>
        </div>

        <div class="resource-action-grid">
          ${actions
            .filter((item) => filter === "all" || filter === item.id)
            .map(
              (item) => `
            <button data-action="go-page" data-page="${item.page}">
              <span>${renderIcon(item.icon, 20)}</span>
              <span>
                <strong>${item.label}</strong>
                <small>${item.meta} · demo source</small>
              </span>
              ${renderIcon("chevron", 18)}
            </button>
          `
            )
            .join("")}
        </div>

        <div class="version-row">
          <span>
            ${renderIcon("layers", 18)}
            <strong>Version 1</strong>
            <small>Original sample set · no adaptive updates yet</small>
          </span>
          <button data-action="go-page" data-page="recommendations">Check recommendations</button>
        </div>
      </section>

      <section class="library-empty panel">
        <div>${renderIcon("plus", 20)}</div>
        <span>
          <strong>Create another learning set</strong>
          <small>Import notes, PDFs, text files, or paste text manually.</small>
        </span>
        <button class="btn btn-secondary" data-action="go-page" data-page="ingest">
          ${renderIcon("upload", 18)}
          <span>Add material</span>
        </button>
      </section>
    </div>
  `;
}

function renderNotesPage() {
  return `
    <div class="page viewer-page">
      <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
      <div class="viewer-layout">
        <article class="panel note-document">
          <div class="document-head">
            <div>
              ${renderBadge("DEMO KEY NOTES · VERSION 1")}
              <h2>Cell division & mitosis</h2>
              <p>Referenced source: Biology lesson notes</p>
            </div>
            ${renderBadge("Available offline", "neutral")}
          </div>

          <div class="key-takeaway">
            ${renderIcon("spark", 20)}
            <p><strong>Key takeaway</strong><br/>Cell division supports growth, repair, and reproduction. Mitosis produces two genetically identical daughter cells.</p>
          </div>

          <h3>Before division</h3>
          <p>During interphase, a cell grows, performs its normal functions, and copies its DNA so each new cell can receive a complete set.</p>

          <h3>The four phases of mitosis</h3>
          <ol>
            <li><strong>Prophase:</strong> Chromosomes condense and become visible.</li>
            <li><strong>Metaphase:</strong> Chromosomes line up at the cell equator.</li>
            <li><strong>Anaphase:</strong> Sister chromatids move to opposite poles.</li>
            <li><strong>Telophase:</strong> New nuclei form around each chromosome set.</li>
          </ol>

          <h3>Cytokinesis</h3>
          <p>The cytoplasm divides, completing the formation of two daughter cells.</p>
        </article>

        <aside class="stack">
          <section class="panel viewer-side">
            <p class="eyebrow">CONTINUE LEARNING</p>
            <h3>Ready to recall this?</h3>
            <p>Use the same source material in a focused study session.</p>
            <button class="btn btn-primary full-button" data-action="go-page" data-page="focus">
              ${renderIcon("play", 18)}
              <span>Start study mode</span>
            </button>
          </section>
          <section class="panel source-proof compact">
            <p class="eyebrow">SOURCE</p>
            <div>
              ${renderIcon("file", 18)}
              <span>
                <strong>Biology lesson notes</strong>
                <small>Built-in demo content</small>
              </span>
            </div>
          </section>
        </aside>
      </div>
    </div>
  `;
}

const DEMO_FLASHCARDS = [
  ["What happens during interphase?", "The cell grows and copies its DNA before division."],
  ["Where do chromosomes line up during metaphase?", "At the cell’s equator."],
  ["What does mitosis produce?", "Two genetically identical daughter cells."],
];

function renderFlashcardsPage() {
  const index = state.flashcards.index;
  const flipped = state.flashcards.flipped;
  const ratings = state.flashcards.ratings;
  const currentCard = DEMO_FLASHCARDS[index];

  return `
    <div class="page cards-page">
      <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
      <div class="cards-header">
        <div>
          ${renderBadge("DEMO FLASHCARDS", "blue")}
          <h2>Cell division & mitosis</h2>
          <p>Card ${index + 1} of ${DEMO_FLASHCARDS.length} · saved offline</p>
        </div>
        <div class="card-count">
          ${Object.keys(ratings).length}/${DEMO_FLASHCARDS.length}
          <small>reviewed</small>
        </div>
      </div>

      <button class="study-flashcard ${flipped ? "flipped" : ""}" data-action="flip-study-card">
        <span class="eyebrow">${flipped ? "ANSWER" : "QUESTION"}</span>
        <strong>${currentCard[flipped ? 1 : 0]}</strong>
        <small>${flipped ? "Tap to see the question" : "Tap to reveal the answer"}</small>
      </button>

      <div class="rating-row">
        <button class="${ratings[index] === "practice" ? "selected" : ""}" data-action="rate-flashcard" data-rating="practice">
          Needs more practice
        </button>
        <button class="${ratings[index] === "understood" ? "selected" : ""}" data-action="rate-flashcard" data-rating="understood">
          I understand this
        </button>
      </div>

      <div class="deck-nav">
        <button class="btn btn-secondary" data-action="flashcard-prev" ${index === 0 ? "disabled" : ""}>
          Previous
        </button>
        ${
          index < DEMO_FLASHCARDS.length - 1
            ? `
          <button class="btn btn-primary" data-action="flashcard-next">
            <span>Next card</span>
            ${renderIcon("arrow", 18)}
          </button>
        `
            : `
          <button class="btn btn-primary" data-action="go-page" data-page="quiz">
            ${renderIcon("quiz", 18)}
            <span>Take the quiz</span>
          </button>
        `
        }
      </div>
    </div>
  `;
}

const QUIZ_QUESTIONS = [
  {
    question: "What is the main result of mitosis?",
    options: ["Four different cells", "Two genetically identical cells", "One larger cell"],
    answer: 1,
    concept: "Purpose of mitosis",
    explanation: "Mitosis produces two daughter cells with the same genetic information.",
  },
  {
    question: "During which phase do chromosomes line up at the cell equator?",
    options: ["Prophase", "Metaphase", "Telophase"],
    answer: 1,
    concept: "Mitosis phases",
    explanation: "Meta means middle: chromosomes align across the middle during metaphase.",
  },
  {
    question: "What happens before mitosis during interphase?",
    options: ["DNA is copied", "The cytoplasm splits", "Chromatids move apart"],
    answer: 0,
    concept: "Interphase",
    explanation: "The cell grows and duplicates its DNA during interphase.",
  },
];

function renderQuizPage() {
  const index = state.quiz.index;
  const current = QUIZ_QUESTIONS[index];
  const selected = state.quiz.answers[index];

  return `
    <div class="page quiz-page">
      <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
      <section class="quiz-shell panel">
        <div class="quiz-progress">
          <span>
            <strong>Cell division quiz</strong>
            <small>Question ${index + 1} of ${QUIZ_QUESTIONS.length}</small>
          </span>
          <div>
            <i style="width: ${((index + 1) / QUIZ_QUESTIONS.length) * 100}%"></i>
          </div>
        </div>

        ${renderBadge("DEMO QUIZ · SAVES LOCALLY", "peach")}
        <h2>${current.question}</h2>

        <div class="quiz-options">
          ${current.options
            .map(
              (opt, optIdx) => `
            <button class="${selected === optIdx ? "selected" : ""}" data-action="select-quiz-opt" data-index="${optIdx}">
              <span>${String.fromCharCode(65 + optIdx)}</span>
              ${opt}
            </button>
          `
            )
            .join("")}
        </div>

        ${
          selected !== undefined
            ? `
          <div class="answer-feedback ${selected === current.answer ? "correct" : "incorrect"}" aria-live="polite">
            ${renderIcon(selected === current.answer ? "check" : "spark", 20)}
            <p>
              <strong>${selected === current.answer ? "That’s right." : "No worries—this is useful evidence."}</strong><br/>
              ${current.explanation}
            </p>
          </div>
        `
            : ""
        }

        <div class="quiz-footer">
          <button class="btn btn-secondary" data-action="quiz-prev" ${index === 0 ? "disabled" : ""}>
            Previous
          </button>
          ${
            index < QUIZ_QUESTIONS.length - 1
              ? `
            <button class="btn btn-primary" data-action="quiz-next" ${selected !== undefined ? "" : "disabled"}>
              <span>Next question</span>
              ${renderIcon("arrow", 18)}
            </button>
          `
              : `
            <button class="btn btn-primary" data-action="submit-quiz" ${selected !== undefined ? "" : "disabled"}>
              ${renderIcon("check", 18)}
              <span>Submit quiz</span>
            </button>
          `
          }
        </div>
      </section>
    </div>
  `;
}

function renderCompletionPage() {
  const attempt = state.latestAttempt || {
    score: 3,
    total: 3,
    completedAt: new Date().toISOString(),
    source: "quiz",
    concepts: [],
  };
  const percentage = Math.round((attempt.score / attempt.total) * 100);

  return `
    <div class="page completion-page">
      <section class="completion-card panel">
        <div class="completion-lumi">
          ${renderLumi("medium")}
        </div>
        ${renderBadge("SESSION COMPLETED")}
        <h2>${percentage === 100 ? "Wonderful focus—you understood every check." : "Nice progress. Every answer gives us a clearer next step."}</h2>
        <p>Lumi saved this result locally and used only your submitted answers to update the knowledge map.</p>

        <div class="summary-stats">
          <span><strong>${attempt.score}/${attempt.total}</strong><small>Correct answers</small></span>
          <span><strong>${attempt.concepts.filter((c) => !c.correct).length}</strong><small>Topics to revisit</small></span>
          <span><strong>Saved</strong><small>On this device</small></span>
        </div>

        <div class="recalc-state">
          <span>${renderIcon("check", 18)}</span>
          <p>
            <strong>Knowledge map updated</strong>
            <small>Recommendations now reflect this session’s evidence.</small>
          </p>
        </div>

        <div class="completion-actions">
          <button class="btn btn-primary" data-action="go-page" data-page="knowledge">
            ${renderIcon("layers", 18)}
            <span>View knowledge map</span>
          </button>
          <button class="btn btn-secondary" data-action="go-page" data-page="recommendations">
            ${renderIcon("spark", 18)}
            <span>See next steps</span>
          </button>
        </div>
      </section>
    </div>
  `;
}

function renderKnowledgeMapPage() {
  const attempt = state.latestAttempt;
  const topics = Array.from(
    new Set([...(attempt?.concepts.map((item) => item.name) || []), "Purpose of mitosis", "Mitosis phases", "Interphase", "Cytokinesis"])
  );

  return `
    <div class="page knowledge-page">
      <section class="workflow-hero">
        <div>
          ${renderBadge("KNOWLEDGE MAP", "blue")}
          <h2>See what the evidence supports.</h2>
          <p>Topic states come from completed answers—not guesses about your ability.</p>
        </div>
        ${
          attempt
            ? `
          <button class="btn btn-primary" data-action="go-page" data-page="recommendations">
            ${renderIcon("spark", 18)}
            <span>Knowledge Analysis</span>
          </button>
        `
            : ""
        }
      </section>

      ${
        !attempt
          ? `
        <section class="empty-evidence panel">
          <div>${renderIcon("layers", 28)}</div>
          <h3>No assessed topics yet</h3>
          <p>Complete a quiz or focused study session to begin your knowledge map. Lumi won’t invent mastery scores without evidence.</p>
          <button class="btn btn-primary" data-action="go-page" data-page="quiz">
            ${renderIcon("quiz", 18)}
            <span>Take a practice quiz</span>
          </button>
        </section>
      `
          : `
        <div class="knowledge-layout">
          <section class="panel map-card">
            <div class="map-legend">
              <span><i class="strong"></i>Strong understanding</span>
              <span><i class="developing"></i>Developing</span>
              <span><i class="practice"></i>Needs practice</span>
              <span><i class="unassessed"></i>Not assessed</span>
            </div>
            <div class="topic-map">
              ${topics
                .map((topic) => {
                  const result = attempt.concepts.find((item) => item.name === topic);
                  const status = result ? (result.correct ? "strong" : "practice") : "unassessed";
                  return `
                  <div class="topic-state ${status}">
                    <span>${renderIcon(result?.correct ? "check" : result ? "spark" : "more", 18)}</span>
                    <p>
                      <strong>${topic}</strong>
                      <small>${status === "strong" ? "Correct in your latest quiz" : status === "practice" ? "Incorrect in your latest quiz" : "No submitted answer yet"}</small>
                    </p>
                    ${renderBadge(status === "strong" ? "Strong" : status === "practice" ? "Needs practice" : "Not assessed", status === "strong" ? "sage" : status === "practice" ? "peach" : "neutral")}
                  </div>
                `;
                })
                .join("")}
            </div>
          </section>

          <aside class="panel evidence-panel">
            <p class="eyebrow">LATEST EVIDENCE</p>
            <h3>${attempt.score} of ${attempt.total} correct</h3>
            <p>${new Date(attempt.completedAt).toLocaleDateString()} · ${attempt.source === "quiz" ? "Quiz" : "Study session"}</p>
            <hr />
            <strong>How this works</strong>
            <p>Correct answers support “strong” for this attempt. Incorrect answers flag practice. More sessions are needed before claiming lasting mastery.</p>
          </aside>
        </div>
      `
      }
    </div>
  `;
}

function renderRecommendationsPage() {
  const attempt = state.latestAttempt;
  const gaps = attempt?.concepts.filter((item) => !item.correct) || [];

  return `
    <div class="page recommendation-page">
      <button class="back-link" data-action="go-page" data-page="library">← Learning Resources</button>
      <section class="workflow-hero">
        <div>
          ${renderBadge("ADAPTIVE PRACTICE", "peach")}
          <h2>${gaps.length ? "Let’s strengthen the parts that need another look." : "Your next step will appear here."}</h2>
          <p>Recommendations use your latest submitted answers and preserve the original resource version.</p>
        </div>
        ${renderLumi("medium")}
      </section>

      ${
        !attempt
          ? `
        <section class="empty-evidence panel">
          <div>${renderIcon("spark", 28)}</div>
          <h3>Complete one activity first</h3>
          <p>Once Lumi has real answer evidence, targeted notes, cards, and practice will appear here.</p>
          <button class="btn btn-primary" data-action="go-page" data-page="focus">
            ${renderIcon("play", 18)}
            <span>Start study mode</span>
          </button>
        </section>
      `
          : `
        <div class="recommendation-grid">
          ${
            gaps.length
              ? gaps
                  .map(
                    (gap, index) => `
                <section class="panel recommendation-card">
                  <span class="recommendation-icon">${renderIcon(index % 2 ? "cards" : "quiz", 22)}</span>
                  ${renderBadge("BASED ON LATEST QUIZ", "peach")}
                  <h3>Review ${escapeHtml(gap.name.toLowerCase())}</h3>
                  <p>You missed the question connected to this concept. Try a short explanation, then answer a similar check.</p>
                  <div class="version-note">
                    ${renderIcon("layers", 18)}
                    <span>
                      <strong>Suggested update · Version 2</strong>
                      <small>Version 1 remains available</small>
                    </span>
                  </div>
                  <button class="btn btn-primary full-button" data-action="go-page" data-page="focus">
                    ${renderIcon("play", 18)}
                    <span>Start targeted practice</span>
                  </button>
                </section>
              `
                  )
                  .join("")
              : `
                <section class="panel recommendation-card">
                  <span class="recommendation-icon">${renderIcon("check", 22)}</span>
                  ${renderBadge("NO GAPS IN LATEST QUIZ")}
                  <h3>Revisit later for spaced practice</h3>
                  <p>Your latest answers were correct. Lumi will not invent a weakness; review again later to strengthen retention.</p>
                  <button class="btn btn-secondary" data-action="go-page" data-page="library">Back to resources</button>
                </section>
              `
          }
        </div>
      `
      }
    </div>
  `;
}

function renderReportPage() {
  const attempts = state.attempts;

  if (!attempts.length) {
    return `
      <div class="page report-page">
        <section class="workflow-hero">
          <div>
            ${renderBadge("REPORT LEARNING", "blue")}
            <h2>Your learning insights will appear here.</h2>
            <p>Complete a study session or quiz to begin a report based on your actual answers.</p>
          </div>
        </section>
        <section class="empty-evidence panel">
          <div>${renderIcon("chart", 28)}</div>
          <h3>No learning evidence yet</h3>
          <p>Lumi won’t invent strengths, gaps, or weekly trends. Your first completed activity will start this report.</p>
          <button class="btn btn-primary" data-action="go-page" data-page="quiz">
            ${renderIcon("quiz", 18)}
            <span>Take a quiz</span>
          </button>
        </section>
      </div>
    `;
  }

  const conceptEvidence = new Map();
  attempts.forEach((att) =>
    att.concepts.forEach((concept) => {
      const prev = conceptEvidence.get(concept.name) || { correct: 0, total: 0 };
      conceptEvidence.set(concept.name, {
        correct: prev.correct + (concept.correct ? 1 : 0),
        total: prev.total + 1,
      });
    })
  );

  const concepts = Array.from(conceptEvidence, ([name, ev]) => ({
    name,
    ...ev,
    accuracy: Math.round((ev.correct / ev.total) * 100),
  }));

  const strengths = concepts.filter((c) => c.correct > c.total - c.correct).sort((a, b) => b.accuracy - a.accuracy);
  const needsPractice = concepts.filter((c) => c.correct <= c.total - c.correct).sort((a, b) => a.accuracy - b.accuracy);
  const overallScore = Math.round(
    (attempts.reduce((s, a) => s + a.score, 0) / attempts.reduce((s, a) => s + a.total, 0)) * 100
  );

  const currentWeek = new Date();
  currentWeek.setHours(0, 0, 0, 0);
  currentWeek.setDate(currentWeek.getDate() - ((currentWeek.getDay() + 6) % 7));

  const weeks = Array.from({ length: 6 }, (_, idx) => {
    const start = new Date(currentWeek);
    start.setDate(start.getDate() - (5 - idx) * 7);
    const end = new Date(start);
    end.setDate(end.getDate() + 7);
    const weekAttempts = attempts.filter((a) => {
      const d = new Date(a.completedAt);
      return d >= start && d < end;
    });
    const ans = weekAttempts.reduce((s, a) => s + a.total, 0);
    const cor = weekAttempts.reduce((s, a) => s + a.score, 0);
    return {
      label: start.toLocaleDateString(undefined, { month: "short", day: "numeric" }),
      sessions: weekAttempts.length,
      average: ans ? Math.round((cor / ans) * 100) : 0,
    };
  });

  return `
    <div class="page report-page">
      <section class="workflow-hero">
        <div>
          ${renderBadge("REPORT LEARNING", "blue")}
          <h2>What’s working—and what to practice next.</h2>
          <p>Insights and weekly analysis use only your saved quiz and study-session answers.</p>
        </div>
        <button class="btn btn-secondary" data-action="go-page" data-page="quiz">
          ${renderIcon("quiz", 18)}
          <span>Add quiz evidence</span>
        </button>
      </section>

      <div class="report-grid">
        <section class="panel weekly-report">
          <div class="section-heading">
            <div>
              <p class="eyebrow">WEEKLY ANALYSIS</p>
              <h3>Performance across six weeks</h3>
            </div>
            ${renderBadge("Actual activity", "neutral")}
          </div>
          <div class="weekly-chart" aria-label="Average answer performance by week">
            ${weeks
              .map(
                (week) => `
              <div class="weekly-column">
                <div class="weekly-value">${week.sessions ? `${week.average}%` : "—"}</div>
                <div class="weekly-track">
                  <i class="${week.sessions ? "has-data" : ""}" style="height: ${week.sessions ? Math.max(12, week.average) : 4}%"></i>
                </div>
                <strong>${week.label}</strong>
                <small>${week.sessions} session${week.sessions === 1 ? "" : "s"}</small>
              </div>
            `
              )
              .join("")}
          </div>
          <p class="report-caveat">Weekly bars show average correct answers only when activity exists. A score change alone does not prove long-term learning.</p>
        </section>

        <section class="panel report-summary">
          <p class="eyebrow">AT A GLANCE</p>
          <div>
            <strong>${attempts.length}</strong>
            <small>Sessions completed</small>
          </div>
          <div>
            <strong>${overallScore}%</strong>
            <small>Correct across saved answers</small>
          </div>
          <div>
            <strong>${concepts.length}</strong>
            <small>Concepts assessed</small>
          </div>
        </section>
      </div>

      <div class="report-details">
        <section class="panel">
          <div class="insight-title">
            <span>${renderIcon("check", 20)}</span>
            <div>
              <p class="eyebrow">YOU EXCEL AT</p>
              <h3>Evidence-backed strengths</h3>
            </div>
          </div>
          ${
            strengths.length
              ? strengths
                  .map(
                    (c) => `
                <p>
                  ${renderIcon("check", 16)}
                  <span>
                    <strong>${c.name}</strong>
                    <small>${c.correct} of ${c.total} checks correct · ${c.accuracy}%</small>
                  </span>
                </p>
              `
                  )
                  .join("")
              : `<p class="muted">Complete more questions correctly to establish a strength.</p>`
          }
        </section>

        <section class="panel">
          <div class="insight-title practice">
            <span>${renderIcon("spark", 20)}</span>
            <div>
              <p class="eyebrow">PRACTICE NEXT</p>
              <h3>Concepts needing attention</h3>
            </div>
          </div>
          ${
            needsPractice.length
              ? needsPractice
                  .map(
                    (c) => `
                <p>
                  ${renderIcon("spark", 16)}
                  <span>
                    <strong>${c.name}</strong>
                    <small>${c.correct} of ${c.total} checks correct · review, then retry</small>
                  </span>
                </p>
              `
                  )
                  .join("")
              : `<p class="muted">No practice gap is supported by your saved answers right now.</p>`
          }
        </section>
      </div>
    </div>
  `;
}

function renderProgressPage() {
  return `
    <div class="page progress-page">
      <section class="progress-hero">
        <div>
          ${renderBadge("PRACTICE & PROGRESS", "blue")}
          <h2>You’re building a stronger foundation.</h2>
          <p>Here’s what your saved practice data suggests—and what to focus on next.</p>
        </div>
        <button class="btn btn-primary" data-action="go-page" data-page="coach">
          ${renderIcon("play", 18)}
          <span>Start recommended practice</span>
        </button>
      </section>

      <div class="progress-grid">
        <section class="panel narrative-card">
          <p class="eyebrow">THIS WEEK’S STORY</p>
          <div class="story-lead">
            <div class="progress-ring" style="--progress: 250deg;">
              <div>
                <strong>72%</strong>
                <small>3 topics</small>
              </div>
            </div>
            <div>
              <h3>Your algebra steps are becoming more consistent.</h3>
              <p>You correctly used inverse operations in 6 of 8 recent questions. Sign changes still need one more focused round.</p>
            </div>
          </div>
          <div class="evidence-row">
            <span>
              ${renderIcon("check", 18)}
              <p><strong>Strength</strong> Solving one-step equations</p>
            </span>
            <span>
              ${renderIcon("spark", 18)}
              <p><strong>Focus next</strong> Negative coefficients</p>
            </span>
          </div>
        </section>

        <section class="panel next-card">
          <p class="eyebrow">RECOMMENDED NEXT</p>
          ${renderBadge("12 MINUTES", "peach")}
          <h3>Practice sign changes</h3>
          <p>Based on two incorrect answers from your May 21 algebra quiz.</p>
          <button class="btn btn-soft" data-action="go-page" data-page="coach">
            <span>Review mistakes</span>
            ${renderIcon("arrow", 18)}
          </button>
        </section>
      </div>

      <section class="panel attempts">
        <div class="section-heading">
          <div>
            <p class="eyebrow">RECENT ATTEMPTS</p>
            <h3>Learning history</h3>
          </div>
          <span class="demo-label">SAMPLE DATA</span>
        </div>
        ${[
          ["Algebra practice", "6 of 8 correct", "May 21", "Improved from last attempt", "quiz", "peach"],
          ["Cell biology quick quiz", "7 of 10 correct", "May 19", "Review mitosis phases", "book", "blue"],
          ["French Revolution recall", "8 of 9 correct", "May 17", "Strong understanding", "file", "sage"],
        ]
          .map(
            ([name, score, date, badge, icon, tone], i) => `
          <button class="attempt-row" data-action="go-page" data-page="coach">
            <span class="attempt-icon a${i}">${renderIcon(icon, 18)}</span>
            <span>
              <strong>${name}</strong>
              <small>${date} · ${score}</small>
            </span>
            ${renderBadge(badge, tone)}
            ${renderIcon("chevron", 18)}
          </button>
        `
          )
          .join("")}
      </section>
    </div>
  `;
}

function renderCoachPage() {
  if (state.coach.practice) {
    return `
      <div class="page coach-page">
        <button class="back-link" data-action="coach-exit-practice">← Back to analysis</button>
        <div class="practice-question panel">
          ${renderBadge("TARGETED PRACTICE · 1 OF 4", "peach")}
          <h2>Solve: −2x + 6 = 14</h2>
          <p>What should you do first?</p>
          ${["Subtract 6 from both sides", "Divide both sides by −2", "Add 2 to both sides"]
            .map(
              (opt, i) => `
            <button data-action="coach-answer" data-index="${i}">
              <span>${String.fromCharCode(65 + i)}</span>
              ${opt}
            </button>
          `
            )
            .join("")}
        </div>
      </div>
    `;
  }

  return `
    <div class="page coach-page">
      <button class="back-link" data-action="go-page" data-page="progress">← Practice & Progress</button>
      <section class="coach-head">
        <div>
          ${renderBadge("ADAPTIVE LEARNING COACH", "peach")}
          <h2>You’re getting closer.</h2>
          <p>Let’s look at the evidence, then practice this concept one more time.</p>
        </div>
        <div class="score-card">
          <strong>6<span>/8</span></strong>
          <small>Algebra quiz · May 21</small>
        </div>
      </section>

      <div class="coach-grid">
        <section class="panel mistakes">
          <p class="eyebrow">WHAT NEEDS ATTENTION</p>
          <h3>Two answers share the same pattern.</h3>
          <p>In both questions, the negative sign was lost while isolating <b>x</b>. That suggests the inverse-operation step needs review. One quiz is not enough to label this a lasting misconception.</p>

          <div class="mistake-item">
            <div>
              <span>QUESTION 4</span>
              <strong>Solve: −3x = 12</strong>
            </div>
            <div class="answer-compare">
              <span class="wrong">Your answer: x = 4</span>
              <span class="right">Correct: x = −4</span>
            </div>
            <button data-action="coach-start-practice">See explanation ${renderIcon("chevron", 15)}</button>
          </div>

          <div class="mistake-item">
            <div>
              <span>QUESTION 7</span>
              <strong>Solve: 5 − 2x = 11</strong>
            </div>
            <div class="answer-compare">
              <span class="wrong">Your answer: x = 3</span>
              <span class="right">Correct: x = −3</span>
            </div>
            <button data-action="coach-start-practice">See explanation ${renderIcon("chevron", 15)}</button>
          </div>
        </section>

        <aside class="stack">
          <section class="panel practice-plan">
            <p class="eyebrow">YOUR PRACTICE PLAN</p>
            <h3>12 focused minutes</h3>
            <div>
              <span>1</span>
              <p><strong>Review the rule</strong><small>2 min · inverse operations</small></p>
            </div>
            <div>
              <span>2</span>
              <p><strong>Try four questions</strong><small>8 min · negative coefficients</small></p>
            </div>
            <div>
              <span>3</span>
              <p><strong>Explain one answer</strong><small>2 min · check understanding</small></p>
            </div>
            <button class="btn btn-primary full-button" data-action="coach-start-practice">
              ${renderIcon("play", 18)}
              <span>Start practice</span>
            </button>
          </section>

          <section class="panel strength-note">
            ${renderIcon("check", 20)}
            <p><strong>What’s already working</strong><br/>You set up both equations correctly and handled addition consistently.</p>
          </section>
        </aside>
      </div>
    </div>
  `;
}

function renderSettingsPage() {
  return `
    <div class="page settings-page">
      <section class="workflow-hero">
        <div>
          ${renderBadge("SETTINGS & OFFLINE STATUS", "neutral")}
          <h2>Clear controls, honest capability states.</h2>
          <p>Manage your learning profile, review local device specs, and test connectivity simulations.</p>
        </div>
      </section>

      <div class="settings-grid">
        <section class="panel setting-card">
          <span class="setting-icon ${state.online ? "" : "muted"}">
            ${renderIcon(state.online ? "wifi" : "offline", 22)}
          </span>
          <div>
            <h3>${state.online ? "You’re online" : "You’re offline"}</h3>
            <p>${state.online ? "Connected prototype features are available. Backend service is active." : "Saved notes, cards, quizzes, and results remain available. New generation is unavailable."}</p>
          </div>
          <button class="btn ${state.online ? "btn-secondary" : "btn-primary"}" data-action="toggle-online">
            ${renderIcon(state.online ? "offline" : "wifi", 18)}
            <span>${state.online ? "Simulate offline" : "Reconnect"}</span>
          </button>
        </section>

        <section class="panel setting-card">
          <span class="setting-icon">${renderIcon("download", 22)}</span>
          <div>
            <h3>Offline library</h3>
            <p>Cell division notes, flashcards, quiz, and saved results are available in this browser session.</p>
          </div>
          ${renderBadge("Ready")}
        </section>

        <section class="panel setting-card">
          <span class="setting-icon">${renderIcon("spark", 22)}</span>
          <div>
            <h3>Local AI device profile</h3>
            <p>${state.profile.deviceType} · ${state.profile.deviceMemory} RAM · ${state.profile.modelPreference || "Balanced"} preference. No model is installed or tested by this prototype.</p>
          </div>
          ${renderBadge("Recommendation saved", "neutral")}
        </section>

        <section class="panel setting-card">
          <span class="setting-icon">${renderIcon("edit", 22)}</span>
          <div>
            <h3>Learning profile</h3>
            <p>Update learner name, age range, subjects, study routine, device fit, and personalization preferences.</p>
          </div>
          <button class="btn btn-secondary" data-action="edit-profile">Edit profile</button>
        </section>

        <section class="panel setting-card">
          <span class="setting-icon">${renderIcon("settings", 22)}</span>
          <div>
            <h3>Backend API & Database (InnoVisionPH)</h3>
            <p>
              Status: <strong>${state.backendStatus.database}</strong> ·
              Version: <strong>${state.backendStatus.version || "0.1.0"}</strong> ·
              Seeded sample projects: <strong>${state.backendStatus.projectCount}</strong>
            </p>
          </div>
          <a href="/docs" target="_blank" rel="noopener" class="btn btn-secondary">
            API Docs
          </a>
        </section>
      </div>
    </div>
  `;
}

function renderOfflineModal() {
  return `
    <div class="modal-backdrop" data-action="close-offline-modal">
      <section class="offline-modal" data-stop-propagation="true">
        <button class="modal-close" data-action="close-offline-modal" aria-label="Close modal">
          ${renderIcon("close", 18)}
        </button>
        <div class="modal-icon">${renderIcon("download", 26)}</div>
        ${renderBadge(state.online ? "ONLINE NOW" : "OFFLINE MODE", state.online ? "sage" : "neutral")}
        <h2>${state.online ? "Keep learning without a connection." : "Your saved learning is ready."}</h2>
        <p>${state.online ? "Save today’s essentials to this device before you go offline." : "You can use downloaded notes, flashcards, quizzes, and your current study plan."}</p>

        <div class="download-list">
          <span>
            ${renderIcon("calendar", 18)}
            <p><strong>Today’s study plan</strong><small>6 activities · 120 min</small></p>
            ${renderIcon("check", 18)}
          </span>
          <span>
            ${renderIcon("book", 18)}
            <p><strong>3 saved lessons</strong><small>Notes and transcripts</small></p>
            ${renderIcon("check", 18)}
          </span>
          <span>
            ${renderIcon("cards", 18)}
            <p><strong>34 flashcards</strong><small>Across 4 topics</small></p>
            ${renderIcon("check", 18)}
          </span>
        </div>

        ${
          state.online
            ? `<button class="btn btn-primary full-button" data-action="save-offline-ready">Saved to this device</button>`
            : `<button class="btn btn-secondary full-button" data-action="toggle-online">${renderIcon("wifi", 18)} Simulate reconnection</button>`
        }
        <p class="prototype-note">Local AI is not configured. Live tutoring and new content generation require internet.</p>
      </section>
    </div>
  `;
}

function renderConfirmModal() {
  if (!state.confirmModal) return "";
  const { title, message } = state.confirmModal;

  return `
    <div class="confirm-modal-overlay" data-action="close-confirm-modal">
      <div class="confirm-card" data-stop-propagation="true">
        <div class="confirm-icon">${renderIcon("spark", 26)}</div>
        <h3>${escapeHtml(title)}</h3>
        <p>${escapeHtml(message)}</p>
        <div class="confirm-actions">
          <button class="btn btn-secondary" data-action="close-confirm-modal">Cancel</button>
          <button class="btn btn-primary" data-action="confirm-action-proceed">Clear & start fresh</button>
        </div>
      </div>
    </div>
  `;
}

/* --------------------------------------------------------------------------
   Master Render Loop
   -------------------------------------------------------------------------- */
const TITLES = {
  home: "Home",
  tutor: "AI Tutor",
  planner: "Study Mode",
  focus: "Focus",
  lessons: "Lessons",
  ingest: "Import Materials",
  generation: "AI Processing",
  library: "Learning Resources",
  notes: "Key Notes",
  flashcards: "Flashcards",
  quiz: "Quiz & Reviewer",
  completion: "Session Complete",
  knowledge: "Knowledge Map",
  recommendations: "Adaptive Practice",
  report: "Learning Report",
  settings: "Settings",
  coach: "Learning Coach",
  progress: "Practice & Progress",
};

function render() {
  const appEl = document.querySelector("#app");
  if (!appEl) return;

  // 1. If in onboarding / welcome-back mode, render onboarding shell
  if (state.setupOpen) {
    appEl.innerHTML = `
      ${renderOnboardingShell()}
      ${renderConfirmModal()}
    `;
    attachActiveListeners();
    return;
  }

  // 2. If in full focus mode, render focus shell directly
  if (state.page === "focus") {
    appEl.innerHTML = renderFocusPage();
    attachActiveListeners();
    return;
  }

  // 3. Otherwise render standard app shell with Sidebar, Topbar, Main page, and Mobile nav
  let pageContent = "";
  switch (state.page) {
    case "home":
      pageContent = renderHomePage();
      break;
    case "tutor":
      pageContent = renderTutorPage();
      break;
    case "planner":
      pageContent = renderPlannerPage();
      break;
    case "lessons":
      pageContent = renderLessonsPage();
      break;
    case "ingest":
      pageContent = renderIngestionPage();
      break;
    case "generation":
      pageContent = renderGenerationPage();
      break;
    case "library":
      pageContent = renderResourceLibraryPage();
      break;
    case "notes":
      pageContent = renderNotesPage();
      break;
    case "flashcards":
      pageContent = renderFlashcardsPage();
      break;
    case "quiz":
      pageContent = renderQuizPage();
      break;
    case "completion":
      pageContent = renderCompletionPage();
      break;
    case "knowledge":
      pageContent = renderKnowledgeMapPage();
      break;
    case "recommendations":
      pageContent = renderRecommendationsPage();
      break;
    case "report":
      pageContent = renderReportPage();
      break;
    case "settings":
      pageContent = renderSettingsPage();
      break;
    case "progress":
      pageContent = renderProgressPage();
      break;
    case "coach":
      pageContent = renderCoachPage();
      break;
    default:
      pageContent = renderHomePage();
  }

  appEl.innerHTML = `
    <div class="app-shell">
      ${renderSidebar()}
      <main class="main-shell">
        ${renderTopbar(TITLES[state.page] || "Lumi")}
        ${pageContent}
      </main>
      ${renderMobileNav()}
      ${state.offlineModalOpen ? renderOfflineModal() : ""}
      ${renderConfirmModal()}
    </div>
  `;

  attachActiveListeners();
}

/* --------------------------------------------------------------------------
   Event Listeners & Event Delegation
   -------------------------------------------------------------------------- */
function attachActiveListeners() {
  // Input listeners that update state without re-rendering the whole page
  const profileNameInput = document.querySelector("#input-profile-name");
  if (profileNameInput) {
    profileNameInput.addEventListener("input", (e) => {
      state.profile.name = e.target.value;
      const nextBtn = document.querySelector('[data-action="onboarding-step"][data-step="2"]');
      if (nextBtn) {
        nextBtn.disabled = !state.profile.name.trim() || state.profile.subjects.length === 0;
      }
    });
  }

  const profileLevelSelect = document.querySelector("#select-profile-level");
  if (profileLevelSelect) {
    profileLevelSelect.addEventListener("change", (e) => {
      state.profile.level = e.target.value;
    });
  }

  const customInterestInput = document.querySelector("#input-custom-interest");
  if (customInterestInput) {
    customInterestInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const val = e.currentTarget.value.trim();
        if (val && !state.profile.subjects.includes(val) && state.profile.subjects.length < 4) {
          state.profile.subjects.push(val);
          render();
        }
      }
    });
  }

  const learningTopicInput = document.querySelector("#input-learning-topic");
  if (learningTopicInput) {
    learningTopicInput.addEventListener("input", (e) => {
      state.profile.learningTopic = e.target.value;
      const nextBtn = document.querySelector('[data-action="onboarding-step"][data-step="4"]');
      if (nextBtn) {
        nextBtn.disabled = state.profile.learningTopic.trim().length < 2 && state.onboarding.topicFiles.length === 0;
      }
    });
  }

  const personalizationCheck = document.querySelector("#check-personalization");
  if (personalizationCheck) {
    personalizationCheck.addEventListener("change", (e) => {
      state.profile.personalization = e.target.checked;
    });
  }

  // Camera and file inputs for onboarding step 3
  const fileCamera = document.querySelector("#file-input-camera");
  if (fileCamera) {
    fileCamera.addEventListener("change", (e) => {
      handleFilesAdded(e.target.files, "onboarding");
      e.target.value = "";
    });
  }

  const fileFiles = document.querySelector("#file-input-files");
  if (fileFiles) {
    fileFiles.addEventListener("change", (e) => {
      handleFilesAdded(e.target.files, "onboarding");
      e.target.value = "";
    });
  }

  // Ingestion inputs
  const ingestTopic = document.querySelector("#ingest-topic-input");
  if (ingestTopic) {
    ingestTopic.addEventListener("input", (e) => {
      state.ingest.topic = e.target.value;
      updateIngestButton();
    });
  }

  const ingestNotes = document.querySelector("#material-notes");
  if (ingestNotes) {
    ingestNotes.addEventListener("input", (e) => {
      state.ingest.notes = e.target.value;
      updateIngestButton();
    });
  }

  const ingestVoiceFile = document.querySelector("#ingest-voice-file");
  if (ingestVoiceFile) {
    ingestVoiceFile.addEventListener("change", (e) => {
      handleFilesAdded(e.target.files, "ingest");
      e.target.value = "";
    });
  }

  const ingestCameraFile = document.querySelector("#ingest-camera-file");
  if (ingestCameraFile) {
    ingestCameraFile.addEventListener("change", (e) => {
      handleFilesAdded(e.target.files, "ingest");
      e.target.value = "";
    });
  }

  const ingestMultiFiles = document.querySelector("#ingest-multi-files");
  if (ingestMultiFiles) {
    ingestMultiFiles.addEventListener("change", (e) => {
      handleFilesAdded(e.target.files, "ingest");
      e.target.value = "";
    });
  }

  // Tutor chat form
  const tutorForm = document.querySelector("#tutor-form");
  if (tutorForm) {
    tutorForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.querySelector("#tutor-input");
      const text = input ? input.value.trim() : state.tutor.input.trim();
      if (!text) return;
      submitTutorMessage(text);
    });
  }
}

function handleFilesAdded(fileList, target) {
  if (!fileList || !fileList.length) return;
  const newItems = Array.from(fileList).map((f) => ({
    name: f.name,
    size: f.size > 1048576 ? `${(f.size / 1048576).toFixed(1)} MB` : `${Math.max(1, Math.round(f.size / 1024))} KB`,
    type: f.name.split(".").pop()?.toUpperCase() || "FILE",
  }));

  if (target === "onboarding") {
    state.onboarding.topicFiles = [...state.onboarding.topicFiles, ...newItems].slice(0, 4);
    state.profile.learningSources = state.onboarding.topicFiles.map((file) => file.name);
  } else if (target === "ingest") {
    state.ingest.files = [...state.ingest.files, ...newItems].slice(0, 6);
  }
  render();
}

function updateIngestButton() {
  const hasContent = state.ingest.topic.trim().length >= 2 && (state.ingest.notes.trim().length >= 20 || state.ingest.files.length > 0);
  const btn = document.querySelector('[data-action="prepare-material"]');
  if (btn) btn.disabled = !hasContent;
}

function submitTutorMessage(text) {
  state.tutor.messages.push({ role: "user", text });
  state.tutor.input = "";

  setTimeout(() => {
    state.tutor.messages.push({
      role: "tutor",
      text: state.online
        ? "Let’s take it one small step at a time. I’ll use the balance idea and show you what changes on each side."
        : "Live AI help needs an internet connection. Your saved explanation and practice cards are still available offline.",
      detail: state.online
        ? "Start by identifying the operation attached to the number. Then apply its inverse to both sides."
        : undefined,
    });
    render();
    const chatContainer = document.querySelector(".chat-area");
    if (chatContainer) chatContainer.scrollTop = chatContainer.scrollHeight;
  }, 350);

  render();
}

// Master event delegation on #app
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-stop-propagation]")) {
    e.stopPropagation();
    return;
  }

  const trigger = e.target.closest("[data-action]");
  if (!trigger) return;

  const action = trigger.dataset.action;

  switch (action) {
    case "go-page":
      setPage(trigger.dataset.page);
      break;

    case "onboarding-resume":
      state.setupOpen = false;
      state.editingProfile = false;
      render();
      break;

    case "onboarding-step":
      const nextStep = Number.parseInt(trigger.dataset.step, 10);
      state.onboardingStep = nextStep;

      // When transitioning to step 2 (Device analysis), trigger animation sequence
      if (nextStep === 2) {
        state.onboarding.analysisStage = 0;
        state.onboarding.detectedCores = 16;
        setTimeout(() => { state.onboarding.analysisStage = 1; render(); }, 350);
        setTimeout(() => { state.onboarding.analysisStage = 2; render(); }, 950);
        setTimeout(() => {
          state.profile.deviceType = "Windows 11 desktop";
          state.profile.deviceMemory = "15.9 GB";
          state.profile.modelPreference = "Llama 3.2 3B Instruct · Q4";
          state.onboarding.analysisStage = 3;
          render();
        }, 1550);
        setTimeout(() => { state.onboarding.analysisStage = 4; render(); }, 2250);
      }
      render();
      break;

    case "onboarding-skip":
      saveProfile(defaultProfile);
      break;

    case "confirm-new-journey":
      // Requirement: Only clear saved profile and learning history after user explicitly confirms
      state.confirmModal = {
        title: "Start a new learning journey?",
        message: "This will clear your saved profile and learning history on this device and guide you through a fresh setup.",
        onConfirm: startNewJourneyConfirmed,
      };
      render();
      break;

    case "close-confirm-modal":
      state.confirmModal = null;
      render();
      break;

    case "confirm-action-proceed":
      if (state.confirmModal?.onConfirm) {
        state.confirmModal.onConfirm();
      }
      break;

    case "toggle-subject":
      const subject = trigger.dataset.subject;
      if (state.profile.subjects.includes(subject)) {
        state.profile.subjects = state.profile.subjects.filter((s) => s !== subject);
      } else {
        state.profile.subjects = [...state.profile.subjects, subject].slice(0, 4);
      }
      render();
      break;

    case "select-model":
      state.profile.modelPreference = trigger.dataset.model;
      render();
      break;

    case "set-topic-method":
      state.onboarding.topicMethod = trigger.dataset.method;
      render();
      break;

    case "start-recording":
      startVoiceRecording();
      break;

    case "stop-recording":
      stopVoiceRecording();
      break;

    case "remove-topic-file":
      const fileIdx = Number.parseInt(trigger.dataset.index, 10);
      state.onboarding.topicFiles = state.onboarding.topicFiles.filter((_, i) => i !== fileIdx);
      state.profile.learningSources = state.onboarding.topicFiles.map((file) => file.name);
      render();
      break;

    case "select-learning-style":
      state.profile.learningStyle = trigger.dataset.style;
      render();
      break;

    case "finish-setup":
      saveProfile(state.profile);
      break;

    case "cancel-setup":
      state.setupOpen = false;
      state.editingProfile = false;
      render();
      break;

    case "edit-profile":
      state.editingProfile = true;
      state.setupOpen = true;
      state.onboardingStep = 1;
      render();
      break;

    case "toggle-online":
      state.online = !state.online;
      render();
      break;

    case "close-offline-modal":
      state.offlineModalOpen = false;
      render();
      break;

    case "save-offline-ready":
      state.offlineModalOpen = false;
      render();
      break;

    // Planner actions
    case "planner-step":
      state.planner.step = Number.parseInt(trigger.dataset.step, 10);
      render();
      break;

    case "set-study-mode":
      state.planner.studyMode = trigger.dataset.mode;
      render();
      break;

    case "toggle-material":
      const mat = trigger.dataset.material;
      if (state.planner.selectedMaterials.includes(mat)) {
        state.planner.selectedMaterials = state.planner.selectedMaterials.filter((m) => m !== mat);
      } else {
        state.planner.selectedMaterials.push(mat);
      }
      render();
      break;

    // Focus mode actions
    case "toggle-focus-pause":
      state.focus.paused = !state.focus.paused;
      render();
      break;

    case "flip-focus-card":
      state.focus.flipped = !state.focus.flipped;
      render();
      break;

    case "select-focus-answer":
      state.focus.answer = Number.parseInt(trigger.dataset.index, 10);
      render();
      break;

    case "focus-next":
      if (state.focus.step === 2) {
        const isCorrect = state.focus.answer === 1; // Option B: Add 4 to both sides
        completeStudySession(isCorrect ? 1 : 0, 1);
        state.focus.step = 0;
        state.focus.answer = null;
        state.focus.flipped = false;
      } else {
        state.focus.step += 1;
        render();
      }
      break;

    // Lessons actions
    case "lesson-start-recording":
      state.lessons.stage = "recording";
      render();
      break;

    case "lesson-toggle-pause":
      state.lessons.paused = !state.lessons.paused;
      render();
      break;

    case "lesson-stop-recording":
      state.lessons.stage = "notes";
      render();
      break;

    case "lesson-generate-cards":
      state.lessons.cards = true;
      render();
      break;

    // Ingestion actions
    case "set-ingest-method":
      state.ingest.inputMethod = trigger.dataset.method;
      render();
      break;

    case "remove-ingest-file":
      const idx = Number.parseInt(trigger.dataset.index, 10);
      state.ingest.files = state.ingest.files.filter((_, i) => i !== idx);
      render();
      break;

    case "prepare-material":
      state.ingest.stage = "ready";
      render();
      break;

    case "reset-ingestion":
      state.ingest.stage = "add";
      state.ingest.topic = "";
      state.ingest.notes = "";
      state.ingest.files = [];
      render();
      break;

    // Generation actions
    case "toggle-generation-res":
      const rId = trigger.dataset.id;
      if (state.generation.selected.includes(rId)) {
        state.generation.selected = state.generation.selected.filter((item) => item !== rId);
      } else {
        state.generation.selected.push(rId);
      }
      render();
      break;

    case "prepare-sample-resources":
      state.generation.prepared = true;
      render();
      break;

    // Library actions
    case "set-library-filter":
      state.library.filter = trigger.dataset.filter;
      render();
      break;

    // Flashcards actions
    case "flip-study-card":
      state.flashcards.flipped = !state.flashcards.flipped;
      render();
      break;

    case "rate-flashcard":
      state.flashcards.ratings[state.flashcards.index] = trigger.dataset.rating;
      render();
      break;

    case "flashcard-prev":
      if (state.flashcards.index > 0) {
        state.flashcards.index -= 1;
        state.flashcards.flipped = false;
        render();
      }
      break;

    case "flashcard-next":
      if (state.flashcards.index < DEMO_FLASHCARDS.length - 1) {
        state.flashcards.index += 1;
        state.flashcards.flipped = false;
        render();
      }
      break;

    // Quiz actions
    case "select-quiz-opt":
      state.quiz.answers[state.quiz.index] = Number.parseInt(trigger.dataset.index, 10);
      render();
      break;

    case "quiz-prev":
      if (state.quiz.index > 0) {
        state.quiz.index -= 1;
        render();
      }
      break;

    case "quiz-next":
      if (state.quiz.index < QUIZ_QUESTIONS.length - 1) {
        state.quiz.index += 1;
        render();
      }
      break;

    case "submit-quiz":
      const concepts = QUIZ_QUESTIONS.map((q, qIdx) => ({
        name: q.concept,
        correct: state.quiz.answers[qIdx] === q.answer,
      }));
      const score = concepts.filter((c) => c.correct).length;
      saveAttempt({
        score,
        total: QUIZ_QUESTIONS.length,
        completedAt: new Date().toISOString(),
        source: "quiz",
        concepts,
      });
      state.quiz.index = 0;
      state.quiz.answers = {};
      break;

    // Tutor actions
    case "send-suggestion":
      submitTutorMessage(trigger.dataset.text);
      break;

    case "toggle-tutor-detail":
      state.tutor.detailOpen = !state.tutor.detailOpen;
      render();
      break;

    case "voice-prototype":
      alert("Voice input prototype: Microphone input is simulated in this environment.");
      break;

    // Coach actions
    case "coach-start-practice":
      state.coach.practice = true;
      render();
      break;

    case "coach-exit-practice":
      state.coach.practice = false;
      render();
      break;

    case "coach-answer":
      alert("Great job! Applying inverse operations isolates x accurately.");
      state.coach.practice = false;
      render();
      break;
  }
});

function escapeHtml(str) {
  if (typeof str !== "string") return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/* --------------------------------------------------------------------------
   Initialization
   -------------------------------------------------------------------------- */
function init() {
  render();
  refreshSystemStatus();
  setInterval(refreshSystemStatus, HEALTH_POLL_INTERVAL_MS);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
