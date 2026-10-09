/**
 * InnoVisionPH Hackathon — Welcome page logic (vanilla JS, ES module).
 *
 * Responsibilities:
 *  - Countdown timer (today Oct 4, 2026 to Oct 9, 2026)
 *  - Backend API & Database connectivity verification
 */

const API_BASE = "/api/v1";
// Target date: October 9, 2026 23:59:59 PH time (UTC+8)
const HACKATHON_TARGET = new Date("2026-10-09T23:59:59+08:00");
const HEALTH_POLL_INTERVAL_MS = 30_000;

const $ = (selector, root = document) => root.querySelector(selector);

/* ------------------------------------------------------------------ */
/* API Client                                                          */
/* ------------------------------------------------------------------ */

async function fetchJson(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

/* ------------------------------------------------------------------ */
/* Backend & Database Connection Status                                */
/* ------------------------------------------------------------------ */

async function refreshSystemStatus() {
  const pill = $("#api-status");
  const pillText = $(".status-pill__text", pill);
  const dbStatusText = $("#db-status-text");
  const projectCount = $("#project-count");

  try {
    const health = await fetchJson("/health");
    const isDbConnected = health.database === "connected";

    pill.classList.toggle("is-online", isDbConnected);
    pill.classList.toggle("is-offline", !isDbConnected);
    pillText.textContent = isDbConnected
      ? `API v${health.version} · DB Connected`
      : "DB Offline";

    if (dbStatusText) {
      dbStatusText.textContent = isDbConnected ? "Connected" : "Disconnected";
    }

    // Connect to sample model table via repository service
    const stats = await fetchJson("/projects/stats");
    if (projectCount) {
      projectCount.textContent = `${stats.total} sample projects`;
    }
  } catch (error) {
    pill.classList.remove("is-online");
    pill.classList.add("is-offline");
    pillText.textContent = "Backend Offline";
    if (dbStatusText) dbStatusText.textContent = "Offline";
    if (projectCount) projectCount.textContent = "0";
  }
}

/* ------------------------------------------------------------------ */
/* Countdown Timer (Today 10/4/2026 -> Oct 9, 2026)                    */
/* ------------------------------------------------------------------ */

function startCountdown() {
  const cells = {
    days: $("#cd-days"),
    hours: $("#cd-hours"),
    minutes: $("#cd-minutes"),
    seconds: $("#cd-seconds"),
  };

  const pad = (value) => String(value).padStart(2, "0");

  const tick = () => {
    const now = Date.now();
    const remainingMs = Math.max(0, HACKATHON_TARGET.getTime() - now);
    const totalSeconds = Math.floor(remainingMs / 1000);

    const days = Math.floor(totalSeconds / 86_400);
    const hours = Math.floor((totalSeconds % 86_400) / 3_600);
    const minutes = Math.floor((totalSeconds % 3_600) / 60);
    const seconds = totalSeconds % 60;

    cells.days.textContent = pad(days);
    cells.hours.textContent = pad(hours);
    cells.minutes.textContent = pad(minutes);
    cells.seconds.textContent = pad(seconds);

    if (remainingMs === 0) {
      const label = $(".countdown__label");
      if (label) label.textContent = "Hackathon Finale reached!";
      clearInterval(timerId);
    }
  };

  const timerId = setInterval(tick, 1000);
  tick();
}

/* ------------------------------------------------------------------ */
/* Initialization                                                     */
/* ------------------------------------------------------------------ */

function init() {
  const yearEl = $("#year");
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());

  startCountdown();
  refreshSystemStatus();
  setInterval(refreshSystemStatus, HEALTH_POLL_INTERVAL_MS);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
