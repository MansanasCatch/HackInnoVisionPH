"""Application launcher.

Steps performed on every run:
    1. Auto-kill any process currently listening on the configured port.
    2. Wait until the port is free.
    3. Apply pending Alembic database migrations (``alembic upgrade head``).
    4. Start Uvicorn (with hot-reload when ``DEBUG=true``).

Usage:
    python run.py                 # uses HOST / PORT from .env (default 127.0.0.1:8000)
    python run.py --port 9000     # override port
    python run.py --no-reload     # disable hot reload
    python run.py --skip-migrations
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import time
from pathlib import Path

import psutil
import uvicorn
from alembic import command
from alembic.config import Config

from app.core.config import BASE_DIR, get_settings
from app.core.logging import configure_logging, get_logger

logger = get_logger("launcher")

PORT_RELEASE_TIMEOUT_SECONDS = 10.0
PROCESS_TERMINATE_TIMEOUT_SECONDS = 5.0


def _find_listening_pids(port: int) -> set[int]:
    """Return the PIDs of every process listening on ``port``."""
    pids: set[int] = set()
    try:
        connections = psutil.net_connections(kind="inet")
    except psutil.AccessDenied:
        # Some platforms (e.g. macOS) require elevated rights for a global scan;
        # fall back to inspecting each process we are allowed to see.
        connections = []
        for proc in psutil.process_iter(["pid"]):
            try:
                connections.extend(proc.net_connections(kind="inet"))
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue

    for conn in connections:
        is_listener = conn.status == psutil.CONN_LISTEN and conn.laddr
        if is_listener and conn.laddr.port == port and conn.pid:
            pids.add(conn.pid)
    return pids


def _protected_pids() -> set[int]:
    """PIDs that must never be killed: this process and its ancestors."""
    current = psutil.Process(os.getpid())
    return {current.pid, *(parent.pid for parent in current.parents())}


def kill_port(port: int) -> None:
    """Terminate every process (and its children) listening on ``port``."""
    pids = _find_listening_pids(port) - _protected_pids()
    if not pids:
        logger.info("Port %s is free.", port)
        return

    targets: list[psutil.Process] = []
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            targets.extend([proc, *proc.children(recursive=True)])
            logger.warning("Port %s is busy -> stopping PID %s (%s)", port, pid, proc.name())
        except psutil.NoSuchProcess:
            continue

    for proc in targets:
        try:
            proc.terminate()
        except psutil.NoSuchProcess:
            continue

    _, alive = psutil.wait_procs(targets, timeout=PROCESS_TERMINATE_TIMEOUT_SECONDS)
    for proc in alive:
        try:
            proc.kill()
        except psutil.NoSuchProcess:
            continue


def _is_port_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def wait_for_port(host: str, port: int, timeout: float = PORT_RELEASE_TIMEOUT_SECONDS) -> None:
    """Block until ``host:port`` can be bound, or exit after ``timeout`` seconds."""
    deadline = time.monotonic() + timeout
    while not _is_port_free(host, port):
        if time.monotonic() > deadline:
            logger.error("Port %s is still in use after %.0fs. Aborting.", port, timeout)
            sys.exit(1)
        time.sleep(0.25)


def run_migrations() -> None:
    """Upgrade the database schema to the latest Alembic revision."""
    logger.info("Applying database migrations...")
    alembic_cfg = Config(str(Path(BASE_DIR) / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(Path(BASE_DIR) / "migrations"))
    command.upgrade(alembic_cfg, "head")
    # Alembic's fileConfig() replaces the root logger config; restore ours.
    configure_logging(get_settings().log_level)
    logger.info("Database is up to date.")


def parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run the InnoVisionPH Hackathon API.")
    parser.add_argument("--host", default=settings.host, help="Bind host.")
    parser.add_argument("--port", type=int, default=settings.port, help="Bind port.")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload.")
    parser.add_argument("--skip-migrations", action="store_true", help="Skip migrations.")
    return parser.parse_args()


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    args = parse_args()

    kill_port(args.port)
    wait_for_port(args.host, args.port)

    if not args.skip_migrations:
        run_migrations()

    reload_enabled = settings.debug and not args.no_reload
    logger.info("Starting server at http://%s:%s (reload=%s)", args.host, args.port, reload_enabled)
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=reload_enabled,
        reload_dirs=[str(Path(BASE_DIR) / "app")] if reload_enabled else None,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
