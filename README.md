# ⚡ Calibrat8: Learn. Score. Calibrate.

> **Offline AI that turns your lessons into study material, then levels it to your scores.**

---

## 🎯 The Challenge

What if all cloud AI agents suddenly went down? Millions of students and exam reviewees who rely on cloud chatbots for notes, quizzes, and tutoring would lose their study help overnight, right before exam day. **Calibrat8** is our answer: a fully local AI app that keeps working when the cloud does not.

---

## 🔴 The Problem

Students and professionals preparing for exams struggle to manage multiple subjects, find their knowledge gaps, and review effectively in limited time. Civil service, licensure, board, and certification exams cover large amounts of material, and many reviewees study after work or school with only a few hours a week.

Today’s AI study tools depend on cloud servers and a constant internet connection. If the service goes down, the connection drops, or the learner lives in a rural or low-connectivity area, the tool stops working. Cloud tools also send personal study data to third-party servers, and reviewers, quizzes, flashcards, and study plans end up scattered across different apps. Most tools generate content but never learn from the learner’s mistakes.

---

## 💡 Our Solution

**Calibrat8** is an offline AI learning coach that runs entirely on the user’s own device using locally hosted models (Ollama). There is no cloud agent, no API key, and no internet dependency. If every cloud AI went offline tomorrow, Calibrat8 would keep working exactly the same.

- 📖 **Learn**: The user uploads lessons, notes, review materials, or files. Local AI generates notes summaries, key notes, flashcards, and quizzes/exam reviewers on the device.
- 🎯 **Score**: The user answers quizzes and mock exams in Study Mode. Calibrat8 records each answer, whether it was correct, time taken, confidence, and hints used, all tied to a specific concept.
- ⚙️ **Calibrate**: After each session, the Knowledge Map updates. Mastery per concept is recalculated using the latest three versions of results, mistakes are analyzed, and the next questions level up or down to match the user’s scores: harder where they are strong, more practice where they are weak.

---

## 🔒 Why Local AI

- 🛡️ **Resilient**: Works during cloud outages, network failures, or no connectivity at all.
- 🔐 **Private**: Lessons, review materials, and scores never leave the device.
- 💰 **Affordable**: No per-query cloud cost, so it can be free or very low cost for students, reviewees, and schools.
- 🌐 **Inclusive**: Built for rural and low-connectivity communities.
- 💻 **Cross-Platform Device-Aware**: Automatically detects RAM, GPU, VRAM, CPU, and storage across **both Windows and macOS** (including Apple Silicon M-series unified memory & Metal acceleration), then recommends the right local model with a non-AI fallback for lightweight devices.

---

## ✨ Key Features

- ⚙️ **Cross-Platform Hardware Detection**: Seamless auto-detection on Windows (WMI/DirectX) and macOS (`sysctl`/`system_profiler`), detecting Apple Silicon unified memory or dedicated NVIDIA/AMD VRAM.
- 🧠 **Hardware-Informed Model Recommendations**: Tiered model suggestions (`llama3.2:1b`, `llama3.2:3b`, `phi3.5:mini`, `qwen2.5:7b`) with memory headroom calculations and reasons.
- 👥 **Multi-Profile Management & Cascading Cleanup**: Switch accounts instantly from the sidebar widget, sync profiles to SQLite database, and delete profiles with cascading deletion of child device specs, learning resources, and study attempts.
- 🤖 **Offline AI Generation**: Notes summaries, key notes, flashcards, and quizzes/exams/reviewers generated on-device via Ollama.
- 🗃️ **Central Learning Resources Hub**: All materials stored with version history (3-version retention window + archived analytics).
- 📈 **Adaptive Difficulty**: Questions calibrate to previous scores through the Knowledge Map.
- ⏱️ **Interactive Focus Mode**: 3-activity step progress indicator (`CONCEPT` → `FLASHCARD` → `QUICK CHECK`), interactive 3D flashcard flip, equation hover highlights, and real-time quiz feedback callouts.
- 📥 **4-Column Multi-Modal Ingestion**: Capture materials via typing (`Type it`), microphone voice recording (`Say it`), camera capture (`Snap it`), or document file upload (`Add a file`).
- 🔍 **Mistake Analysis**: Identifies weak topics and misconceptions from wrong answers.
- 📊 **Learning Comparison Report**: Shows progress across versions, useful for tracking exam readiness.

---

## 👥 Who It Is For

- 🎓 High school and college students
- 📋 Professional exam reviewees: civil service, licensure, board, bar, and certification exams
- 💼 Working professionals reviewing in limited time
- 👩‍🏫 Teachers, tutors, and review centers creating personalized materials
- 🏞️ Learners in rural or low-connectivity areas
- 🏫 Schools and institutions seeking privacy-focused AI learning tools

---

## 💡 Project Flow & System Architecture

### Flow

#### A. Setup
- **Onboarding / Account Setup**: Create a local profile (username, list of interests, age, study level, subjects, exam dates, daily study time). Profiles support switching, editing, and database-backed deletion.
- **Device Specs Setup**: Auto-detect RAM, GPU, VRAM, and storage (Windows & macOS), then pick the right local AI model (or non-AI fallback). Ollama auto-pulls selected models in the background.

#### B. Create
- **Ingest**: Lessons, notes, and files (PDF, Word, Excel, Images, CSV, Text) are extracted, chunked, and tagged to topics.
- **Process Flow**: Job queue, prompt templates, output validation, and progress tracking.
- **Local AI**: Runs on-device (local server via Ollama) and generates study material.
- **Generate**: Produces Notes Summary / Key Notes, Flashcards, and Quizzes / Exam / Reviewer.
- **Learning Resources**: The central hub that stores everything with version history.
- **Report: Learning Comparison**: Compares progress across versions.

#### C. Study
- **Study Mode**: The student picks topics and available time.
- **Load Learning Resources**: Builds the session queue by priority.
- **Recalculating**: Updates priorities using the latest 3 versions.
- **Start**: Begins the session.
- **Scene / Focus**: Where the student answers quizzes, exams, and flashcards with instant feedback.
- **Completed**: Shows score and summary.
- **Update Knowledge Map**: Updates mastery, analyzes mistakes, and writes back to Learning Resources.

```text
The Loop:
Ingest ──► Local AI ──► Generate ──► Learning Resources
                                           │
Study Mode ──► Load ──► Recalculating ──► Start ──► Focus Scene ──► Completed
                                                                       │
                                             Update Knowledge Map ─────┘
```

#### 📊 Scene Records Per Answer
- Question and concept ID
- Student's answer
- Correct or not
- Time taken
- Confidence score
- Hints used

---

## 📋 Table of Contents

1. [Prerequisites](#-prerequisites-what-to-install)
2. [Quick Start](#-quick-start)
3. [How to Run the App](#-how-to-run-the-app)
4. [Project Structure](#-project-structure)
5. [Architecture](#-architecture)
6. [API Endpoints](#-api-endpoints)
7. [Database Migrations](#-database-migrations)
8. [Testing & Code Quality](#-testing--code-quality)
9. [Troubleshooting](#-troubleshooting)

---

## 🛠️ Technology Stack

| Layer | Technologies & Tools |
| --- | --- |
| **Backend API** | **FastAPI**, **Python 3.12+**, Uvicorn (ASGI), Pydantic v2 |
| **Database & ORM** | **SQLite 3**, **SQLAlchemy 2.0** ORM, **Alembic** migrations |
| **Local AI Engine** | **Ollama** (`llama3.2:1b`, `llama3.2:3b`, `phi3.5:mini`, `qwen2.5:7b`), Psutil |
| **Hardware Detection** | Cross-platform engine (Windows WMI/DirectX + macOS sysctl/system_profiler Metal) |
| **Frontend UI** | **React 19**, **TypeScript 5.7**, **Vite 5**, **TailwindCSS v4**, Single-Page Application (SPA) |
| **Document Extraction** | PyPDF, python-docx, openpyxl, Pillow, CSV, Plain Text |
| **Testing & Quality** | Pytest, Pytest-Asyncio, Pytest-Cov, Ruff, Vitest |

---

## 🧰 Prerequisites (what to install)

| Tool | Version | Download |
| --- | --- | --- |
| **Python** | **3.12 or newer** (tested on Python 3.12/3.14) | https://www.python.org/downloads/ |
| **Node.js & npm** | **v20 or newer** (for React/Vite frontend development & build) | https://nodejs.org |
| **Ollama** | **Latest** (for Local AI model execution) | https://ollama.com |
| **Git** | Latest | https://git-scm.com/downloads |
| **VS Code** *(recommended)* | Latest | https://code.visualstudio.com/ |

> ⚠️ **Windows:** during Python installation, tick **“Add python.exe to PATH”**.

Verify your installation:

```bash
python --version   # Python 3.12+ expected
node -v            # Node.js v20+ expected
npm -v
ollama --version   # (Optional, app can auto-launch Ollama background server)
```

---

## ⚡ Quick Start

```bash
# 1. Clone and enter the project
git clone <your-repo-url> InnoVisionPH
cd InnoVisionPH

# 2. Create a virtual environment (skip if .venv already exists)
python -m venv .venv

# 3. Activate it
#    Windows (PowerShell)
.venv\Scripts\Activate.ps1
#    Windows (cmd)
.venv\Scripts\activate.bat
#    macOS / Linux
source .venv/bin/activate

# 4. Install backend dependencies
pip install -r requirements.txt

# 5. Build the React frontend (compiled output saved to frontend/dist)
cd frontend
npm install
npm run build
cd ..

# 6. (Optional) create your local environment file
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux

# 7. Run the app 🎉
python run.py
```

Open **http://127.0.0.1:8000** in your browser.

> 💡 If PowerShell blocks script execution on Windows, run once:  
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## ▶️ How to Run the App

```bash
python run.py
```

`run.py` automatically performs:

1. 🔪 **Auto-kills** any process already listening on the port (default `8000`) to prevent "address already in use" errors.
2. ⏳ Waits until the port is completely free.
3. 🤖 **Auto-starts Ollama** background engine if installed locally.
4. 🗄️ **Applies database migrations** (`alembic upgrade head`) — the SQLite database and tables are initialized automatically.
5. 🔁 Starts Uvicorn with **hot-reload** enabled during development.

| Command | Description |
| --- | --- |
| `python run.py` | Default run (kill busy port → start Ollama → run migrations → start server) |
| `python run.py --port 9000` | Use a custom port |
| `python run.py --host 0.0.0.0` | Bind to all interfaces (for local network testing) |
| `python run.py --no-reload` | Disable hot-reload |
| `python run.py --skip-migrations` | Launch server without executing migrations |

| URL | Description |
| --- | --- |
| http://127.0.0.1:8000 | Calibrat8 React SPA Frontend |
| http://127.0.0.1:8000/docs | Interactive OpenAPI documentation (Swagger UI) |
| http://127.0.0.1:8000/redoc | ReDoc API documentation |
| http://127.0.0.1:8000/api/v1/health | System & Database Health Endpoint |

---

## 🗂️ Project Structure

```text
InnoVisionPH/
├── app/                              # Backend application (Clean Architecture & FastAPI)
│   ├── main.py                       # FastAPI app factory, middleware, routes & React SPA mounts
│   ├── api/                          # 🌐 Presentation layer (HTTP controllers)
│   │   ├── deps.py                   #    Dependency injection wiring
│   │   └── v1/
│   │       ├── router.py             #    Aggregated API v1 router
│   │       └── endpoints/            #    health, onboarding, device, ai, learning_resources, study_sessions, knowledge_map
│   ├── services/                     # 🧠 Business logic & domain use cases
│   │   ├── onboarding_service.py     #    User onboarding & cascade deletion use cases
│   │   ├── device_service.py         #    Device specs coordination & model selection
│   │   ├── device_detection.py       #    Cross-platform hardware detector (Windows & macOS)
│   │   ├── model_recommendation.py   #    Hardware-aware model recommender
│   │   ├── local_ai_service.py       #    Local AI model inference & context grounding
│   │   ├── file_parser.py            #    Multi-format document extractor (PDF, Word, Excel, Images, CSV, Text)
│   │   ├── ollama_service.py         #    Ollama daemon auto-start & background pull percentage tracker
│   │   └── health_service.py         #    Health check logic
│   ├── repositories/                 # 🗃️ Data access (Abstract ports + SQLAlchemy adapters)
│   │   ├── onboarding_repository.py  #    Onboarding DB access with cascading deletion
│   │   ├── device_repository.py      #    Device specs DB access
│   │   ├── learning_resource_repository.py
│   │   └── study_session_repository.py
│   ├── models/                       # 🧱 SQLAlchemy 2.0 ORM models (Database tables)
│   │   ├── onboarding.py             #    OnboardingProfile model
│   │   ├── device.py                 #    DeviceSpecs model
│   │   ├── learning_resource.py      #    LearningResource & versions
│   │   └── study_session.py          #    StudySession & answer logs
│   ├── schemas/                      # 📦 Pydantic schemas (Request / response contracts)
│   │   ├── onboarding.py
│   │   ├── device.py
│   │   ├── ai.py
│   │   ├── learning_resource.py
│   │   ├── study_session.py
│   │   └── health.py
│   ├── db/                           # ⚙️ Database engine, session maker & SQLite DB (`innovision.db`)
│   └── core/                         # 🔧 Configuration (.env), logging & custom exceptions
├── frontend/                         # ⚛️ React 19 + TypeScript + TailwindCSS v4 SPA
│   ├── README.md                     #    Dedicated frontend architecture & UI guide
│   ├── src/
│   │   ├── api/                      #    Typed API client, mappers, and TypeScript schemas
│   │   ├── App.tsx                   #    App shell, multi-profile state, study scenes, navigation
│   │   ├── index.css                 #    Design tokens, ambient lighting, keyframe animations
│   │   └── main.tsx                  #    React 19 entrypoint
│   ├── public/                       #    Static assets (Calibrat8 illustrations, icons)
│   ├── dist/                         #    Production bundle output (compiled via `npm run build`)
│   ├── index.html                    #    Single Page Application entry point
│   ├── package.json                  #    Dependencies & scripts
│   ├── tsconfig.json                 #    TypeScript configuration
│   └── vite.config.ts                #    Vite build & dev proxy configuration
├── migrations/                       # Alembic database migrations
│   ├── env.py                        # Migration environment connected to app metadata
│   └── versions/                     # DB schema migration scripts
├── tests/
│   ├── conftest.py                   # Shared fixtures (in-memory SQLite, TestClient)
│   ├── unit/                         # ✅ Unit tests for services & parsers
│   └── integration/                  # 🔗 API & repository integration tests
├── alembic.ini                       # Alembic configuration
├── pyproject.toml                    # Pytest, coverage & Ruff linting configuration
├── requirements.txt                  # Pinned Python dependencies
├── run.py                            # Server launcher script
└── README.md                         # Project documentation
```

---

## 🏛️ Architecture

```text
 Browser / Client  ──fetch──►  API (routers)  ──►  Services  ──►  Repositories  ──►  Database / Ollama
 (React 19 SPA)                validate DTOs       business        data access       SQLAlchemy SQLite
                               (Pydantic v2)       rules           (abstract port)   + Local Ollama Engine
```

---

## 🔌 API Endpoints

Base path: `/api/v1`

### 👤 Onboarding & Profile Management
| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API liveness and database connectivity status |
| `POST` | `/onboarding` | Save onboarding account setup (username, interests, age) |
| `GET` | `/onboarding` | List onboarding profiles (with optional pagination limit & offset) |
| `GET` | `/onboarding/{id}` | Get onboarding profile by ID |
| `GET` | `/onboarding/user/{username}` | Get onboarding profile by Username |
| `PUT` | `/onboarding/{id}` | Update onboarding profile preferences |
| `DELETE` | `/onboarding/{id}` | Permanently delete profile and cascade delete all child device specs, resources, and study sessions |

### 💻 Device Specs Setup & Local AI Models
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/device/detect` | Cross-platform auto-detect of host machine hardware (Windows & macOS RAM, GPU/Metal, VRAM, CPU, storage, OS) |
| `GET` | `/device/suggestions` | Get local AI model options with specific hardware applicability reasons |
| `POST` | `/device` | Save hardware specs setup linked to an onboarding account (`onboarding_id`) |
| `GET` | `/device/account/{onboarding_id}` | Fetch device specs & selected model for an account |
| `POST` | `/device/select-model` | Switch active local AI model at runtime & trigger Ollama background auto-pull |
| `GET` | `/device/active-model` | Fetch active local AI model with streaming pull percentage |
| `GET` | `/device/ollama/models` | List installed Ollama models and check local Ollama server connection |

### 🤖 Local AI & File Ingestion
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/ai/generate` | Generate text using active local model for the account |
| `POST` | `/ai/generate-with-files` | Generate Local AI response grounded by attached file contents (PDF, Word, Excel, Images, CSV, Text) |

### 📚 Learning Resources (Hub, Generation & Versioning)
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/learning-resources/generate` | End-to-end multi-format ingestion & Local AI generation (creates resource + version with summary, key notes, flashcards, quizzes) |
| `POST` | `/learning-resources` | Create a learner-owned resource container manually |
| `GET` | `/learning-resources` | List learning resources for an account with latest version metadata |
| `GET` | `/learning-resources/{id}` | Get specific learning resource details |
| `POST` | `/learning-resources/{resource_id}/versions` | Add a version and retain the latest three full versions |
| `GET` | `/learning-resources/{resource_id}/versions` | List selectable versions for a resource |
| `GET` | `/learning-resources/{resource_id}/versions/{version_id}` | Retrieve a specific generated resource version |
| `GET` | `/learning-resources/{resource_id}/versions/{version_id}/progress` | Check first-time status and progress for one version |
| `GET` | `/learning-resources/{resource_id}/analytics/archived` | Read compact metrics for archived versions |

### ⏱️ Study Sessions & Answers
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/study-sessions` | Start an attempt against an exact version |
| `GET` | `/study-sessions` | List completed study sessions for an account |
| `GET` | `/study-sessions/{id}` | Get study session status, score, and summary |
| `POST` | `/study-sessions/{session_id}/answers` | Record an answer and concept evidence (tracks correct, hints, confidence, time) |
| `POST` | `/study-sessions/{session_id}/complete` | Score the attempt and advance only the current version |

### 🗺️ Knowledge Map & Mastery
| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/knowledge-map` | Fetch concept mastery levels (Mastered, Practicing, Needs Review) computed from recent session answers |

---

## 🗄️ Database Migrations

SQLite is enabled by default (`app/db/innovision.db`). Migrations are powered by **Alembic**.

```bash
# Apply pending migrations (executed automatically by run.py)
alembic upgrade head

# Generate a new migration after editing models in app/models/
alembic revision --autogenerate -m "create new table"

# Roll back the latest migration
alembic downgrade -1

# Check current revision status
alembic current
```

---

## 🧪 Testing & Code Quality

### Backend Tests
```bash
# Run unit & integration test suites
.venv\Scripts\python -m pytest tests/unit/test_device_service.py tests/unit/test_onboarding_service.py tests/integration/test_device_api.py tests/integration/test_onboarding_api.py

# Backend code formatting & lint checks
.venv\Scripts\ruff check .
```

### Frontend Tests & Type Checking
```bash
# Navigate to frontend
cd frontend

# TypeScript typecheck
npx tsc --noEmit

# Production bundle build
npm run build
```

---

## 🛠️ Troubleshooting

| Issue | Resolution |
| --- | --- |
| `python` not recognized | Reinstall Python with **Add python.exe to PATH** checked, or run with `py` on Windows |
| Cannot activate venv in PowerShell | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 occupied | `python run.py` automatically terminates existing listeners; or specify a custom port: `python run.py --port 9000` |
| Ollama model missing | Selecting a model triggers automatic background downloading (`ollama pull`). Track status via `GET /api/v1/device/active-model` |
| Reset database | Delete `app/db/innovision.db` and start `python run.py` (migrations re-create tables automatically) |

---

Happy learning! 🇵🇭💡 **Calibrat8: Learn. Score. Calibrate.**
