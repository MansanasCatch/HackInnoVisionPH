"""Integration with local Ollama API service for model inspection and streaming auto-pulling."""

import json
import shutil
import subprocess
import threading
import time
import urllib.request
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"

# Global reference to prevent ResourceWarning on subprocess garbage collection
_OLLAMA_PROC: subprocess.Popen[bytes] | None = None

# Global memory map to track streaming model download progress
PULL_PROGRESS: dict[str, dict[str, Any]] = {}


def is_ollama_reachable(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Check if local Ollama service is listening."""
    try:
        req = urllib.request.Request(f"{base_url}/", headers={"User-Agent": "FastAPI-App"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_ollama_started(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Check if Ollama is listening; if not, automatically launch 'ollama serve' in background."""
    global _OLLAMA_PROC
    if is_ollama_reachable(base_url):
        logger.info("Ollama local service is running at %s", base_url)
        return True

    ollama_path = shutil.which("ollama")
    if not ollama_path:
        logger.warning(
            "Ollama executable not found in system PATH. "
            "Install Ollama (https://ollama.com) to enable local AI auto-start."
        )
        return False

    logger.info("Auto-starting local Ollama service (`ollama serve`)...")
    try:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        _OLLAMA_PROC = subprocess.Popen(
            [ollama_path, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )

        for _ in range(10):
            time.sleep(0.5)
            if is_ollama_reachable(base_url):
                logger.info("Ollama local service successfully auto-started!")
                return True

    except Exception as err:
        logger.warning("Failed to auto-start Ollama server: %s", err)

    return False


def get_installed_ollama_models(base_url: str = OLLAMA_BASE_URL) -> list[str]:
    """Fetch currently pulled model tags from local Ollama tags endpoint."""
    if not is_ollama_reachable(base_url):
        return []
    try:
        url = f"{base_url}/api/tags"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = data.get("models", [])
            return [m.get("name") for m in models if "name" in m]
    except Exception as err:
        logger.warning("Failed to list Ollama tags: %s", err)
        return []


def get_model_pull_progress(model_name: str, base_url: str = OLLAMA_BASE_URL) -> dict[str, Any]:
    """Get live pull progress percentage and status message for a given model."""
    installed = get_installed_ollama_models(base_url)

    if model_name in installed or f"{model_name}:latest" in installed:
        return {
            "status": "completed",
            "pull_percentage": 100.0,
            "status_message": "installed",
        }

    if model_name in PULL_PROGRESS:
        return PULL_PROGRESS[model_name]

    return {
        "status": "not_pulled",
        "pull_percentage": 0.0,
        "status_message": "not pulled",
    }


def trigger_ollama_pull_background(model_name: str, base_url: str = OLLAMA_BASE_URL) -> None:
    """Asynchronously pull the requested model from Ollama in background and stream progress %."""

    def _pull_worker() -> None:
        if not is_ollama_reachable(base_url):
            ensure_ollama_started(base_url)

        if not is_ollama_reachable(base_url):
            logger.info("Ollama unreachable at %s. Skipping pull for '%s'.", base_url, model_name)
            PULL_PROGRESS[model_name] = {
                "status": "offline",
                "pull_percentage": 0.0,
                "status_message": "Ollama service offline",
            }
            return

        logger.info("Initiating streaming Ollama pull for model '%s'...", model_name)
        PULL_PROGRESS[model_name] = {
            "status": "pulling",
            "pull_percentage": 0.0,
            "completed_bytes": 0,
            "total_bytes": 0,
            "status_message": "starting pull",
        }

        try:
            url = f"{base_url}/api/pull"
            payload = json.dumps({"name": model_name, "stream": True}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=1800.0) as resp:
                for line in resp:
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        status_str = chunk.get("status", "")
                        completed = chunk.get("completed", 0)
                        total = chunk.get("total", 0)

                        pct = 0.0
                        if total > 0 and completed > 0:
                            pct = round((completed / total) * 100.0, 1)

                        if status_str == "success" or pct >= 100.0:
                            pct = 100.0

                        PULL_PROGRESS[model_name] = {
                            "status": "completed" if status_str == "success" else "pulling",
                            "pull_percentage": pct,
                            "completed_bytes": completed,
                            "total_bytes": total,
                            "status_message": status_str,
                        }
                    except Exception:
                        continue

            PULL_PROGRESS[model_name] = {
                "status": "completed",
                "pull_percentage": 100.0,
                "status_message": "success",
            }
            logger.info("Ollama pull for model '%s' completed successfully (100%%).", model_name)

        except Exception as err:
            logger.error("Error pulling model '%s' from Ollama: %s", model_name, err)
            PULL_PROGRESS[model_name] = {
                "status": "failed",
                "pull_percentage": 0.0,
                "status_message": f"Error: {err}",
            }

    thread = threading.Thread(target=_pull_worker, daemon=True, name=f"ollama-pull-{model_name}")
    thread.start()
