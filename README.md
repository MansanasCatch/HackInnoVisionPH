# 🚀 InnoVisionPH Hackathon Starter

A **Clean Code Architecture** starter kit built with **Python + FastAPI**, SQLAlchemy 2.0, Alembic database migrations,
and a **pure HTML / CSS / JavaScript** welcome page featuring a live hackathon countdown and backend connectivity status.

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
10. [Adding a New Feature](#-adding-a-new-feature-checklist)
11. [Troubleshooting](#-troubleshooting)

---

## 🧰 Prerequisites (what to install)

| Tool | Version | Download |
| --- | --- | --- |
| **Python** | **3.12 or newer** (tested on Python 3.14) | https://www.python.org/downloads/ |
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
3. 🗄️ **Applies database migrations** (`alembic upgrade head`) — the SQLite database and sample records are initialized automatically.
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
│   │       └── endpoints/        #    health.py, projects.py
│   ├── services/                 # 🧠 Business logic / domain use cases
│   │   ├── project_service.py    #    Project use cases
│   │   └── health_service.py     #    Health check logic
│   ├── repositories/             # 🗃️ Data access (Abstract port + SQLAlchemy adapter)
│   │   └── project_repository.py
│   ├── models/                   # 🧱 SQLAlchemy 2.0 ORM models (Database tables)
│   │   └── project.py            #    Sample Project model
│   ├── schemas/                  # 📦 Pydantic schemas (Request / response contracts)
│   │   ├── project.py
│   │   └── health.py
│   ├── db/                       # ⚙️ Database engine, session maker & declarative base
│   └── core/                     # 🔧 Configuration (.env), logging & custom exceptions
├── frontend/                     # Pure HTML / CSS / JS (No external JS frameworks)
│   ├── index.html                # Welcome page (message, countdown, DB indicator)
│   ├── css/styles.css            # Custom CSS with design tokens & glassmorphism
│   ├── js/app.js                 # Pure vanilla ES module (countdown & health poll)
│   └── assets/favicon.svg        # Clean SVG favicon
├── migrations/                   # Alembic database migrations
│   ├── env.py                    # Migration environment connected to app metadata
│   └── versions/                 # 20261004_0001_create_projects.py (seed data included)
├── tests/
│   ├── conftest.py               # Shared fixtures (in-memory SQLite, TestClient)
│   ├── unit/                     # ✅ Unit tests (isolated, fast, no HTTP/DB required)
│   └── integration/              # 🔗 Repository & API integration tests
├── .vscode/                      # Editor settings, launch configs & recommended plugins
├── alembic.ini                   # Alembic configuration
├── pyproject.toml                # Pytest, coverage & Ruff linting configuration
├── requirements.txt              # Pinned Python dependencies
├── run.py                        # Launcher (auto-kill port, migrate & start)
├── .env.example                  # Environment variables template
├── .editorconfig                 # Consistent whitespace & formatting rules
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
- **Repository Pattern**: Services depend on the `AbstractProjectRepository` interface, making them straightforward to unit-test with mock repositories.
- **Centralized Error Handling**: Services raise domain exceptions (`NotFoundError`, `ConflictError`), which FastAPI translates into standardized JSON error responses.

---

## 🔌 API Endpoints

Base path: `/api/v1`

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | API liveness and database connectivity status |
| `GET` | `/projects/stats` | Aggregated project statistics by status (used by Welcome page) |
| `GET` | `/projects` | List projects (with optional status filter, limit, offset) |
| `GET` | `/projects/{id}` | Retrieve a single project by ID |
| `POST` | `/projects` | Register a new project |

---

## 🗄️ Database Migrations

SQLite is enabled by default (`innovision.db` in project root). Migrations are powered by **Alembic**.

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

> **Note**: When creating a new model, import it in `app/models/__init__.py` so Alembic's autogenerate can detect it.

**Switching to PostgreSQL**:

```bash
pip install "psycopg[binary]"
# In .env:
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/innovision
```

---

## 🧪 Testing & Code Quality

```bash
# Run the test suite (warnings are treated as errors)
pytest

# Run tests with test coverage summary
pytest --cov

# Check linting with Ruff
ruff check .

# Format code with Ruff
ruff format .
```

Standards enforced:

- **Strict Warning Free**: `filterwarnings = ["error"]` in `pyproject.toml`.
- **Ruff**: Modern Python 3.12+ rules, PEP 8 compliance, and import sorting.
- **Type Annotations**: Comprehensive type hinting across models, schemas, and services.

---

## 🎨 Icons (Font Awesome)

The UI uses **Font Awesome 6 (Free)** included via CDN in `frontend/index.html`:

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">
```

| Resource | Link |
| --- | --- |
| 🔍 Search free icons | https://fontawesome.com/search?o=r&m=free |
| 📖 Usage guide | https://docs.fontawesome.com/web/add-icons/how-to |
| 🌐 CDN source (cdnjs) | https://cdnjs.com/libraries/font-awesome |

Examples:

```html
<i class="fa-solid fa-rocket"></i>       <!-- Solid icon -->
<i class="fa-regular fa-clock"></i>      <!-- Regular icon -->
<i class="fa-solid fa-database"></i>     <!-- Database icon -->
```

---

## ✅ Adding a New Feature (Checklist)

Example: adding a `Team` resource.

1. **Model** &rarr; `app/models/team.py` and register it in `app/models/__init__.py`.
2. **Migration** &rarr; `alembic revision --autogenerate -m "create teams table"` &rarr; `alembic upgrade head`.
3. **Schemas** &rarr; `app/schemas/team.py` (`TeamCreate`, `TeamRead`).
4. **Repository** &rarr; `app/repositories/team_repository.py` (abstract interface + SQLAlchemy implementation).
5. **Service** &rarr; `app/services/team_service.py` (domain rules, raise custom errors).
6. **Dependency Injection** &rarr; wire `get_team_service` in `app/api/deps.py`.
7. **Router** &rarr; `app/api/v1/endpoints/teams.py` and include in `app/api/v1/router.py`.
8. **Tests** &rarr; `tests/unit/test_team_service.py` & `tests/integration/test_teams_api.py`.
9. Verify with `ruff check .` and `pytest`.

---

## 🛠️ Troubleshooting

| Issue | Resolution |
| --- | --- |
| `python` not recognized | Reinstall Python with **Add python.exe to PATH** checked, or run with `py` on Windows |
| Cannot activate venv in PowerShell | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Port 8000 occupied | `python run.py` automatically terminates existing listeners; or specify a custom port: `python run.py --port 9000` |
| Reset database | Delete `innovision.db` and start `python run.py` (migrations re-create tables and seeds automatically) |
| `Unable to copy ...venvlauncher.exe` | The `.venv` is in use by a running process. Stop any running server (`Ctrl+C`) before recreating the virtual environment |

---

Happy hacking! 🇵🇭💡
