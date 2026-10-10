# ⚛️ Calibrat8 Frontend

> **React 19 + TypeScript + Vite + TailwindCSS v4 Single-Page Application**  
> Offline-first adaptive AI study companion that runs on your local machine.

---

## 🚀 Overview

The **Calibrat8 Frontend** is an offline-capable, responsive web interface built for learners, students, and exam reviewees. It integrates directly with the local FastAPI backend (`http://127.0.0.1:8000`) and the local Ollama AI model runner, ensuring that studying, flashcards, quizzes, and notes generation remain accessible even without an internet connection.

---

## ✨ Features & User Interface

### 1. 👤 Multi-Profile & Account Management
- **Local & Database Synchronization**: Automatically syncs profiles with the backend via `/api/v1/onboarding`.
- **Fast Profile Switcher**: Switch between learners instantly from the sidebar dropdown widget.
- **Account Actions**: "Add another user", "Review profile preferences", and "Log out & Switch profile".
- **Cascading Profile Deletion**: Accessible modal confirmation dialog that permanently purges the profile and all associated study attempts and hardware specs from the database via `DELETE /api/v1/onboarding/{id}`.

### 2. 💻 Device Specs Auto-Detection & Local AI Setup
- **Cross-Platform Detection**: Supports both **Windows** (WMI, DirectX, dedicated NVIDIA/AMD VRAM) and **macOS** (Apple Silicon M-series unified memory, Metal acceleration) via `/api/v1/device/detect`.
- **Intelligent Model Suggestions**: Suggests the optimal local model (`llama3.2:1b`, `llama3.2:3b`, `phi3.5:mini`, `qwen2.5:7b`) based on available RAM, VRAM, and storage via `/api/v1/device/suggestions`.
- **Ollama Status & Background Pulls**: Tracks installed models and real-time streaming download progress.
- **Hardware Fallback Mode**: Gracefully handles lightweight devices with a non-AI offline study mode.

### 3. 🎯 Focus Mode & Study Scene
- **3-Activity Step Progress**: Interactive visual indicator tracking `CONCEPT`, `FLASHCARD`, and `QUICK CHECK`.
- **Interactive 3D Flashcard**: Flip cards with accessible ARIA states, smooth transitions, and keyboard/touch support.
- **Equation Hover Highlights**: Step-by-step mathematical breakdowns with contextual color highlights.
- **Instant Quiz Feedback**: Real-time answer validation callouts ("That’s it." / "Good try...") before session completion.

### 4. 📥 4-Column Material Ingestion Hub
- **Multiple Input Modalities**:
  - 📝 **Type it**: Paste or write notes, concepts, and definitions.
  - 🎙️ **Say it**: In-browser voice recording with dynamic waveform animation.
  - 📷 **Snap it**: Camera capture for whiteboards, textbooks, or notes.
  - 📁 **Add a file**: Multi-format document upload (PDF, DOCX, PPTX, TXT, Markdown, Images, Audio).
- **Prototype Safety**: Ingestion queue with remove buttons, size checks, and clear status feedback.

### 5. 🏠 Home & Dashboard Experience
- **Learning Shortcuts (`quick-grid`)**: Micro-animated action cards ("Make Something", "Jump Back In", "See Your Growth").
- **Flight Visuals**: Calibrat8 floating laptop illustration (`/calibrat8-flying-laptop.png`) with flight physics animations.
- **Ambient Lighting**: CSS keyframe gradient drift (`onboarding-light-drift`) during onboarding.

### 6. ⚙️ Settings & Local AI Controls
- **Runtime Model Switcher**: Change the active Ollama model without restarting the server.
- **Device Profile Summary**: Live overview of detected RAM, GPU, CPU, and storage.
- **Danger Zone**: Remove learning profile with confirmation safeguard.

---

## 🗂️ Project Structure

```text
frontend/
├── public/                     # Static assets
│   ├── calibrat8-flying-laptop.png
│   ├── calibrat8-onboarding-icon.png
│   ├── calibrat8.png
│   └── favicon.svg
├── src/
│   ├── api/                    # 🌐 Typed backend API client & schemas
│   │   ├── client.ts           #    API fetch client & error handling
│   │   ├── mappers.ts          #    Age & profile mapper helpers
│   │   ├── mappers.test.ts     #    Unit tests for mappers
│   │   └── types.ts            #    TypeScript interfaces matching backend DTOs
│   ├── App.tsx                 # ⚛️ Core application shell, state & routing
│   ├── index.css               # 🎨 Design tokens, animations & TailwindCSS v4 imports
│   └── main.tsx                # 🚀 React 19 entrypoint
├── index.html                  # HTML template
├── package.json                # Dependencies and npm scripts
├── tsconfig.json               # TypeScript configuration
└── vite.config.ts              # Vite 5 config with backend proxy (/api -> http://127.0.0.1:8000)
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
| --- | --- |
| **React 19** | Component architecture and state management |
| **TypeScript 5.7** | Strict type safety for data models and API contracts |
| **Vite 5 / 8** | Ultra-fast development server and production bundler |
| **TailwindCSS v4** | Utility-first styling with `@tailwindcss/vite` |
| **Manrope & DM Sans** | Premium typography and readable study layouts |

---

## 💻 Development & Build Scripts

Make sure you are in the `frontend/` directory:

```bash
cd frontend
```

### Install Dependencies
```bash
npm install
```

### Start Vite Development Server
```bash
npm run dev
```
*Runs on `http://localhost:8080` (or next free port) with reverse proxy forwarding `/api` calls to FastAPI at `http://127.0.0.1:8000`.*

### Typecheck TypeScript
```bash
npx tsc --noEmit
```

### Production Build
```bash
npm run build
```
*Compiles optimized HTML, CSS, and JS bundle into `frontend/dist/`. FastAPI serves this bundle directly at `http://127.0.0.1:8000`.*

### Preview Production Build
```bash
npm run preview
```

---

## 🔌 API Client Integration

The frontend connects to the backend through `src/api/client.ts`. Key integrated endpoints include:

- `GET /api/v1/health`: Server & database connectivity
- `POST /api/v1/onboarding`: Create learner profile
- `GET /api/v1/onboarding`: List all saved database profiles
- `GET /api/v1/onboarding/{id}`: Fetch learner profile by ID
- `PUT /api/v1/onboarding/{id}`: Update profile preferences
- `DELETE /api/v1/onboarding/{id}`: Cascade delete profile & child records
- `POST /api/v1/device/detect`: Cross-platform hardware spec auto-detection
- `GET /api/v1/device/suggestions`: Hardware-informed local model options
- `POST /api/v1/device`: Save device hardware record linked to profile
- `POST /api/v1/device/select-model`: Switch active Ollama model at runtime
- `GET /api/v1/device/active-model`: Live status of active model and download progress
- `GET /api/v1/device/ollama/models`: Installed models in local Ollama instance
