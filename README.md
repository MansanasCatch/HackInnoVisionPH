# 🚀 Offline AI Learning Coach — InnoVisionPH

An **Offline AI Learning Coach** starter & API built with **Python + FastAPI**, SQLAlchemy 2.0, Alembic database migrations, and a pure HTML / CSS / JavaScript interface.

---

## 💡 Project Flow & System Architecture

### Flow

#### A. Setup
- **Onboarding / Account Setup**: Create a local profile (username, list of interests, age, study level, subjects, exam dates, daily study time).
- **Device Specs Setup**: Detect RAM, GPU, and storage, then pick the right local AI model (or a non-AI fallback).

#### B. Create
- **Ingest**: Lessons, notes, and files are extracted, chunked, and tagged to topics.
- **Process Flow**: Job queue, prompt templates, output validation, and progress tracking.
- **Local AI**: Runs on-device (in-browser or local server) and generates study material.
- **Generate**: Produces Notes Summary / Key Notes, Flashcards, and Quizzes / Exam / Reviewer.
- **Learning Resources**: The central hub that stores everything with version history.
- **Report: Learning Comparison**: Compares progress across versions.

#### C. Study
- **Study Mode**: The student picks topics and available time.
- **Load Learning Resources**: Builds the session queue by priority.
- **Recalculating**: Updates priorities using the latest 3 versions.
- **Start**: Begins the session.
- **Scene**: Where the student answers quizzes, exams, and flashcards.
- **Completed**: Shows score and summary.
- **Update Knowledge Map**: Updates mastery, analyzes mistakes, and writes back to Learning Resources.

```text
The Loop:
Ingest ──► Local AI ──► Generate ──► Learning Resources
                                           │
Study Mode ──► Load ──► Recalculating ──► Start ──► Scene ──► Completed
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

#### 🧩 Gaps to Add
- Study planner step (“5 topics in 2 hours”)
- Mistake analyzer and adaptive practice
- Fallback when AI isn’t available
- Retry path for bad AI output
- Recording consent step
- Tutor chat
- Settings, export, and backup

---

## 📋 Table of Contents

1. [Prerequisites (what to install)](#-prerequisites-what-to-install)
2. [Quick Start](#-quick-start)
3. [How to Run the App](#-how-to-run-the-app)
4. [Project Structure](#-project-structure)
5. [Architecture](#-architecture)
6. [API Endpoints](#-api-endpoints)
7. [Database Migrations](#-database-migrations)
8. [Testing & Code Quality](#-testing--code-quality)
9. [Icons (Font Awesome)](#-icons-font-awesome)
10. [Troubleshooting](#-troubleshooting)

---

## 🧰 Prerequisites (what to install)

| Tool | Version | Download |
| --- | --- | --- |
| **Python** | **3.12 or newer** (tested on Python 3.12/3.14) | https://www.python.org/downloads/ |
| **Git** | Latest | https://git-scm.com/downloads |
| **VS Code** *(recommended)* | Latest | https://code.visualstudio.com/ |

> ⚠️ **Windows:** during Python installation, tick **“Add python.exe to PATH”**.

Verify your installation:

```bash
python --version   # Python 3.12+ expected
pip --version
```

Recommended VS Code extensions (prompted automatically via `.vscode/extensions.json`):
Python, Python Debugger, Ruff, EditorConfig.

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

# 4. Install dependencies
pip install -r requirements.txt

# 5. (Optional) create your local environment file
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux

# 6. Run the app 🎉
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
3. 🗄️ **Applies database migrations** (`alembic upgrade head`) — the SQLite database and tables are initialized automatically.
4. 🔁 Starts Uvicorn with **hot-reload** enabled during development.

| Command | Description |
| --- | --- |
| `python run.py` | Default run (kill busy port → run migrations → start server) |
| `python run.py --port 9000` | Use a custom port |
| `python run.py --host 0.0.0.0` | Bind to all interfaces (for local network testing) |
| `python run.py --no-reload` | Disable hot-reload |
| `python run.py --skip-migrations` | Launch server without executing migrations |

| URL | Description |
| --- | --- |
| http://127.0.0.1:8000 | Welcome Page (countdown to Oct 9, 2026 & live DB status) |
| http://127.0.0.1:8000/docs | Interactive OpenAPI documentation (Swagger UI) |
| http://127.0.0.1:8000/redoc | ReDoc API documentation |
| http://127.0.0.1:8000/api/v1/health | System & Database Health Endpoint |

---

## 🗂️ Project Structure

```text
InnoVisionPH/
├── app/                          # Backend application (Clean Code Architecture)
│   ├── main.py                   # FastAPI app factory, middleware, routes & static mounts
│   ├── api/                      # 🌐 Presentation layer (HTTP controllers)
│   │   ├── deps.py               #    Dependency injection wiring
│   │   └── v1/
│   │       ├── router.py         #    Aggregated API v1 router
│   │       └── endpoints/        #    health.py, onboarding.py
│   ├── services/                 # 🧠 Business logic / domain use cases
│   │   ├── onboarding_service.py #    User onboarding use cases
│   │   └── health_service.py     #    Health check logic
│   ├── repositories/             # 🗃️ Data access (Abstract port + SQLAlchemy adapter)
│   │   └── onboarding_repository.py
│   ├── models/                   # 🧱 SQLAlchemy 2.0 ORM models (Database tables)
│   │   └── onboarding.py         #    OnboardingProfile model
│   ├── schemas/                  # 📦 Pydantic schemas (Request / response contracts)
│   │   ├── onboarding.py         #    OnboardingCreate, OnboardingRead, OnboardingUpdate
│   │   └── health.py
│   ├── db/                       # ⚙️ Database engine, session maker, declarative base & SQLite DB (`innovision.db`)
│   └── core/                     # 🔧 Configuration (.env), logging & custom exceptions
├── frontend/                     # Pure HTML / CSS / JS (No external JS frameworks)
│   ├── index.html                # Welcome page (message, countdown, DB indicator)
│   ├── css/styles.css            # Custom CSS with design tokens & glassmorphism
│   ├── js/app.js                 # Pure vanilla ES module (countdown & health poll)
│   └── assets/favicon.svg        # Clean SVG favicon
├── migrations/                   # Alembic database migrations
│   ├── env.py                    # Migration environment connected to app metadata
│   └── versions/                 # 20261010_0002_create_onboardings.py
├── tests/
│   ├── conftest.py               # Shared fixtures (in-memory SQLite, TestClient)
│   ├── unit/                     # ✅ Unit tests (isolated, fast, no HTTP/DB required)
│   └── integration/              # 🔗 Repository & API integration tests
├── alembic.ini                   # Alembic configuration
├── pyproject.toml                # Pytest, coverage & Ruff linting configuration
├── requirements.txt              # Pinned Python dependencies
├── run.py                        # Launcher (auto-kill port, migrate & start)
├── .env.example                  # Environment variables template
└── .gitignore                    # Standard Python, DB, and cache ignores
```

---

## 🏛️ Architecture

```text
 Browser (frontend/)  ──fetch──►  API (routers)  ──►  Services  ──►  Repositories  ──►  Database
                                   validate DTOs       business        data access       SQLAlchemy
                                   (Pydantic)          rules           (abstract port)   + Alembic
```

**Key Architectural Principles**:

- **Thin Controllers**: Routers in `app/api/` only validate payloads and delegate to services.
- **Pure Business Logic**: Services in `app/services/` contain domain logic and never import framework-specific HTTP components.
- **Repository Pattern**: Services depend on abstract repository interfaces (`AbstractOnboardingRepository`), making them straightforward to unit-test with mock repositories.
- **Centralized Error Handling**: Services raise domain exceptions (`NotFoundError`, `ConflictError`), which FastAPI translates into standardized JSON error responses.

---

## 🔌 API Endpoints

Base path: `/api/v1`

### 👤 Onboarding
| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API liveness and database connectivity status |
| `POST` | `/onboarding` | Save onboarding account setup (Username, List of interests, Age) |
| `GET` | `/onboarding` | List onboarding profiles (with optional pagination limit & offset) |
| `GET` | `/onboarding/{id}` | Get onboarding profile by ID |
| `GET` | `/onboarding/user/{username}` | Get onboarding profile by Username |
| `PUT` | `/onboarding/{id}` | Update onboarding profile |

### 💻 Device Specs Setup & Local AI Models
| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/device/detect` | Auto-detect host machine hardware specs (RAM, GPU, VRAM, CPU, storage, OS) |
| `GET` | `/device/suggestions` | Get local AI model options with specific hardware applicability reasons |
| `POST` | `/device` | Save hardware specs setup linked to an onboarding account (`onboarding_id`) |
| `GET` | `/device/account/{onboarding_id}` | Fetch device specs & selected model for an account |
| `POST` | `/device/select-model` | Switch active local AI model at runtime & trigger Ollama background auto-pull |
| `GET` | `/device/active-model` | Fetch active local AI model configured for AI generation tasks |
| `GET` | `/device/ollama/models` | List installed Ollama models and check local Ollama server connection |

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

```bash
# Run the test suite
.\.venv\Scripts\pytest.exe
```

---

## 🛠️ Troubleshooting

| Issue | Resolution |
| --- | --- |
| `python` not recognized | Reinstall Python with **Add python.exe to PATH** checked, or run with `py` on Windows |
| Cannot activate venv in PowerShell | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 occupied | `python run.py` automatically terminates existing listeners; or specify a custom port: `python run.py --port 9000` |
| Reset database | Delete `app/db/innovision.db` and start `python run.py` (migrations re-create tables automatically) |

---

Happy hacking! 🇵🇭💡
