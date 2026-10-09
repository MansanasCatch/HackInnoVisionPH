"""Integration with local Ollama API service for model inspection and auto-pulling."""

import threading
import urllib.request
import json
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

OLLAMA_BASE_URL = "http://localhost:11434"


def is_ollama_reachable(base_url: str = OLLAMA_BASE_URL) -> bool:
    """Check if local Ollama service is listening."""
    try:
        req = urllib.request.Request(f"{base_url}/", headers={"User-Agent": "FastAPI-App"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
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


def trigger_ollama_pull_background(model_name: str, base_url: str = OLLAMA_BASE_URL) -> None:
    """Asynchronously pull the requested model from Ollama in a background thread."""
    def _pull_worker():
        if not is_ollama_reachable(base_url):
            logger.info("Ollama service unreachable at %s. Skipping auto-pull for '%s'.", base_url, model_name)
            return

        logger.info("Initiating background Ollama pull for model '%s'...", model_name)
        try:
            url = f"{base_url}/api/pull"
            payload = json.dumps({"name": model_name, "stream": False}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=300.0) as resp:
                result = resp.read().decode("utf-8")
                logger.info("Ollama pull for model '%s' completed successfully.", model_name)
        except Exception as err:
            logger.error("Error pulling model '%s' from Ollama: %s", model_name, err)

    thread = threading.Thread(target=_pull_worker, daemon=True, name=f"ollama-pull-{model_name}")
    thread.start()
