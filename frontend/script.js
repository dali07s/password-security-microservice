/* =====================================================================
 * Password Security — Microservice Dashboard
 * Plain-vanilla JS frontend for the FastAPI backend.
 *
 * SECURITY NOTES:
 *  - Passwords / TOTP codes are NEVER stored in localStorage/sessionStorage
 *    and never written to the console.
 *  - Sensitive inputs are cleared after each operation.
 *  - All user-controlled content is inserted via textContent (never
 *    innerHTML with user data).
 * ===================================================================== */

"use strict";

/* Base URL of the FastAPI backend (local development). */
const API_BASE = "http://127.0.0.1:8000";

/* ------------------------------------------------------------------ */
/* Helpers                                                             */
/* ------------------------------------------------------------------ */

/** Return the first defined value among a list of possible keys. */
function pick(obj, keys, fallback = null) {
  for (const k of keys) {
    if (obj && obj[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return fallback;
}

/** Generic JSON API call with consistent error handling. */
async function apiPost(path, body) {
  let response;
  try {
    response = await fetch(API_BASE + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch (err) {
    return {
      ok: false,
      status: 0,
      message:
        "Cannot reach the backend at " + API_BASE +
        ". Is the FastAPI server running (uvicorn)?",
    };
  }

  let data = null;
  const text = await response.text();
  if (text) {
    try { data = JSON.parse(text); }
    catch { /* non-JSON body */ }
  }

  if (!response.ok) {
    let message = "Request failed (HTTP " + response.status + ").";
    if (response.status === 422) {
      const detail = data && data.detail;
      if (Array.isArray(detail)) {
        message = "Validation error: " +
          detail.map((d) => (d.loc ? d.loc.join(".") + ": " : "") + (d.msg || "")).join("; ");
      } else if (typeof detail === "string") {
        message = "Validation error: " + detail;
      } else {
        message = "Invalid input — please check the entered values.";
      }
    } else if (response.status === 429) {
      message = "Rate limit exceeded. Please wait a moment and try again.";
    } else if (response.status >= 500) {
      const detail = data && data.detail;
      message = "Server error" +
        (typeof detail === "string" ? ": " + detail : "") +
        ". Please try again later.";
    } else if (data && typeof data.detail === "string") {
      message = data.detail;
    }
    return { ok: false, status: response.status, message, data };
  }
  return { ok: true, status: response.status, data: data || {} };
}

/** Button loading state: show spinner, disable to prevent double submit. */
function setLoading(btn, loading) {
  btn.disabled = loading;
  const spinner = btn.querySelector(".btn__spinner");
  const label = btn.querySelector(".btn__label");
  if (spinner) spinner.hidden = !loading;
  if (label) label.textContent = loading ? "Working…" : btn.dataset.label;
}

/** Remember the original button label once. */
function rememberLabels() {
  document.querySelectorAll(".btn").forEach((btn) => {
    const label = btn.querySelector(".btn__label");
    if (label && !btn.dataset.label) btn.dataset.label = label.textContent;
  });
}

/** Build a result element safely (no innerHTML with user content). */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = String(text);
  return node;
}

/** Show an alert box inside a result container. */
function showAlert(container, kind, text) {
  container.textContent = "";
  const box = el("div", "alert alert--" + kind);
  box.appendChild(el("p", null, text));
  container.appendChild(box);
  container.hidden = false;
}

/** Hide a result container. */
function hideResult(container) {
  container.textContent = "";
  container.hidden = true;
}

/** Toast notification. */
let toastTimer = null;
function toast(message) {
  const t = document.getElementById("toast");
  t.textContent = message;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { t.hidden = true; }, 2600);
}

/** Copy text to clipboard with fallback and visual feedback. */
async function copyText(text, btn) {
  let copied = false;
  try {
    await navigator.clipboard.writeText(text);
    copied = true;
  } catch {
    // Fallback for non-secure contexts (e.g. file://)
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { copied = document.execCommand("copy"); } catch { copied = false; }
    ta.remove();
  }
  if (copied) {
    const original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = original; }, 1800);
    toast("Copied to clipboard.");
  } else {
    toast("Copy failed — please select and copy manually.");
  }
}

/** Create a small copy button bound to a value getter. */
function copyButton(getValue) {
  const btn = el("button", "btn--small", "Copy");
  btn.type = "button";
  btn.addEventListener("click", () => {
    const value = getValue();
    if (value) copyText(value, btn);
  });
  return btn;
}

/* ------------------------------------------------------------------ */
/* Navigation (single-page sections)                                   */
/* ------------------------------------------------------------------ */

function initNavigation() {
  const sections = document.querySelectorAll(".section");
  const links = document.querySelectorAll(".nav-link");
  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const menuBtn = document.getElementById("menu-btn");

  function showSection(id) {
    sections.forEach((s) => s.classList.toggle("is-visible", s.id === id));
    links.forEach((l) => l.classList.toggle("is-active", l.dataset.section === id));
    if (location.hash !== "#" + id) history.replaceState(null, "", "#" + id);
    closeSidebar();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function closeSidebar() {
    sidebar.classList.remove("is-open");
    overlay.hidden = true;
  }

  links.forEach((l) => l.addEventListener("click", (e) => {
    e.preventDefault();
    showSection(l.dataset.section);
  }));

  // Dashboard cards also navigate
  document.querySelectorAll(".card--link").forEach((card) => {
    card.addEventListener("click", (e) => {
      e.preventDefault();
      const id = card.getAttribute("href").slice(1);
      showSection(id);
    });
  });

  menuBtn.addEventListener("click", () => {
    sidebar.classList.add("is-open");
    overlay.hidden = false;
  });
  overlay.addEventListener("click", closeSidebar);

  // Initial section from URL hash
  const initial = (location.hash || "#dashboard").slice(1);
  const target = document.getElementById(initial);
  showSection(target && target.classList.contains("section") ? initial : "dashboard");
}

/* ------------------------------------------------------------------ */
/* A. Password Strength Checker                                        */
/* ------------------------------------------------------------------ */

const STRENGTH_LABELS = ["Very Weak", "Weak", "Fair", "Good", "Strong"];

function initStrengthChecker() {
  const form = document.getElementById("strength-form");
  const input = document.getElementById("strength-input");
  const btn = document.getElementById("strength-btn");
  const result = document.getElementById("strength-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const password = input.value;
    if (!password) return;

    hideResult(result);
    setLoading(btn, true);
    const res = await apiPost("/api/password/strength", { password });
    setLoading(btn, false);
    input.value = ""; // never retain passwords

    if (!res.ok) { showAlert(result, "error", res.message); return; }

    const d = res.data;
    const score = Number(pick(d, ["score", "strength_score"], -1));
    const clamped = Math.max(0, Math.min(4, isNaN(score) ? -1 : score));
    const label = pick(d, ["strength", "strength_label", "label"],
      clamped >= 0 ? STRENGTH_LABELS[clamped] : "Unknown");
    const length = pick(d, ["length", "password_length"]);
    const diversity = pick(d, ["character_diversity", "diversity", "charset_size", "unique_characters"]);
    const guesses = pick(d, ["estimated_guesses", "guesses", "guess_count", "entropy_guesses"]);
    let feedback = pick(d, ["feedback", "recommendations", "suggestions"], []);

    renderStrengthResult(result, { score: clamped, label, length, diversity, guesses, feedback });
  });
}

function renderStrengthResult(container, r) {
  container.textContent = "";

  const verdict = el("div", "verdict " + (r.score >= 3 ? "verdict--ok" : "verdict--bad"),
    "Strength: " + r.label + (r.score >= 0 ? "  ·  Score " + r.score + "/4" : ""));
  container.appendChild(verdict);

  // Meter
  const meter = el("div", "meter");
  const bar = el("div", "meter__bar");
  for (let i = 0; i < 5; i++) {
    const seg = el("div", "meter__seg");
    if (r.score >= 0 && i <= r.score) seg.classList.add("s" + r.score);
    bar.appendChild(seg);
  }
  meter.appendChild(bar);
  const lab = el("div", "meter__label");
  lab.appendChild(el("span", null, "Strength indicator"));
  const scoreSpan = el("span", "meter__score " + (r.score >= 0 ? "c" + r.score : ""), r.label);
  lab.appendChild(scoreSpan);
  meter.appendChild(lab);
  container.appendChild(meter);

  // Stats
  const stats = el("div", "stats");
  if (r.length !== null && r.length !== undefined)
    stats.appendChild(stat("Length", r.length));
  if (r.diversity !== null && r.diversity !== undefined)
    stats.appendChild(stat("Character diversity", r.diversity));
  if (r.guesses !== null && r.guesses !== undefined)
    stats.appendChild(stat("Estimated guesses", formatNumber(r.guesses)));
  if (stats.children.length) container.appendChild(stats);

  // Feedback
  if (typeof r.feedback === "string") r.feedback = r.feedback ? [r.feedback] : [];
  if (Array.isArray(r.feedback) && r.feedback.length) {
    const list = el("ul", "feedback");
    r.feedback.forEach((f) => list.appendChild(el("li", null, f)));
    container.appendChild(el("h4", null, "Recommendations"));
    container.appendChild(list);
  }
  container.hidden = false;
}

function stat(label, value) {
  const s = el("div", "stat");
  s.appendChild(el("span", "stat__label", label));
  s.appendChild(el("span", "stat__value", value));
  return s;
}

function formatNumber(n) {
  const num = Number(n);
  if (isNaN(num)) return String(n);
  if (num >= 1e12) return num.toExponential(2);
  return num.toLocaleString("en-US");
}

/* ------------------------------------------------------------------ */
/* B. Secure Password Generator                                        */
/* ------------------------------------------------------------------ */

function initGenerator() {
  const form = document.getElementById("generator-form");
  const slider = document.getElementById("gen-length");
  const out = document.getElementById("gen-length-out");
  const btn = document.getElementById("generator-btn");
  const result = document.getElementById("generator-result");

  slider.addEventListener("input", () => { out.textContent = slider.value; });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideResult(result);
    setLoading(btn, true);
    const res = await apiPost("/api/password/generate", { length: Number(slider.value) });
    setLoading(btn, false);

    if (!res.ok) { showAlert(result, "error", res.message); return; }

    const password = pick(res.data, ["password", "generated_password", "value"]);
    if (!password) { showAlert(result, "error", "Backend response did not contain a password."); return; }

    renderSecretOutput(result, password, "Generated password");
  });
}

/** Render a generated secret (password / passphrase) with a copy button. */
function renderSecretOutput(container, value, caption) {
  container.textContent = "";
  const row = el("div", "output");
  row.appendChild(el("span", "output__value", value));
  row.appendChild(copyButton(() => value));
  container.appendChild(el("h4", null, caption));
  container.appendChild(row);
  container.appendChild(el("p", "field__hint",
    "Generated locally by the backend's cryptographically secure RNG — copy it and store it in a password manager."));
  container.hidden = false;
}

/* ------------------------------------------------------------------ */
/* C. Memorable Passphrase Generator                                   */
/* ------------------------------------------------------------------ */

function initPassphrase() {
  const form = document.getElementById("passphrase-form");
  const slider = document.getElementById("pass-words");
  const out = document.getElementById("pass-words-out");
  const btn = document.getElementById("passphrase-btn");
  const result = document.getElementById("passphrase-result");

  slider.addEventListener("input", () => { out.textContent = slider.value; });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideResult(result);
    setLoading(btn, true);
    const res = await apiPost("/api/passphrase/generate", { number_of_words: Number(slider.value) });
    setLoading(btn, false);

    if (!res.ok) { showAlert(result, "error", res.message); return; }

    const phrase = pick(res.data, ["passphrase", "words", "generated_passphrase"]);
    const phraseText = Array.isArray(phrase) ? phrase.join(" ") : phrase;
    if (!phraseText) { showAlert(result, "error", "Backend response did not contain a passphrase."); return; }

    renderSecretOutput(result, phraseText, "Generated passphrase");
  });
}

/* ------------------------------------------------------------------ */
/* D. Two-Factor Authentication (TOTP)                                 */
/* ------------------------------------------------------------------ */

function initTwoFA() {
  const setupForm = document.getElementById("twofa-setup-form");
  const verifyForm = document.getElementById("twofa-verify-form");
  const usernameInput = document.getElementById("twofa-username");
  const codeInput = document.getElementById("twofa-code");
  const setupBtn = document.getElementById("twofa-setup-btn");
  const verifyBtn = document.getElementById("twofa-verify-btn");
  const setupResult = document.getElementById("twofa-setup-result");
  const verifyResult = document.getElementById("twofa-verify-result");

  let currentUser = null;
  let currentSecret = null;

  setupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = usernameInput.value.trim();
    if (!username) return;

    hideResult(setupResult);
    setLoading(setupBtn, true);
    const res = await apiPost("/api/2fa/setup", { username });
    setLoading(setupBtn, false);

    if (!res.ok) { showAlert(setupResult, "error", res.message); return; }

    const d = res.data;
    currentUser = username;
    currentSecret = pick(d, ["manual_key", "secret", "totp_secret"]);

    // QR code: may be base64 data, a data-URI, or a URL
    let qrSrc = pick(d, ["qr_code", "qr_code_base64", "qr", "qr_image", "qr_b64"]);
    if (typeof qrSrc === "string" && qrSrc && !qrSrc.startsWith("data:") && !qrSrc.startsWith("http")) {
      qrSrc = "data:image/png;base64," + qrSrc;
    }
    const qrUrl = pick(d, ["qr_code_url", "qr_url", "otpauth_uri", "uri", "provisioning_uri"]);

    setupResult.textContent = "";
    if (qrSrc && qrSrc.startsWith("data:")) {
      const block = el("div", "qr-block");
      const img = document.createElement("img");
      img.src = qrSrc;
      img.alt = "TOTP QR code for " + username;
      block.appendChild(img);
      const meta = el("div", "qr-block__meta");
      meta.appendChild(el("p", null,
        "Scan this QR code with Google Authenticator, Microsoft Authenticator, or any TOTP-compatible app."));
      if (currentSecret) {
        meta.appendChild(el("p", null, "Manual entry key:"));
        const code = el("code", null, currentSecret);
        meta.appendChild(code);
      }
      block.appendChild(meta);
      setupResult.appendChild(block);
    } else if (qrUrl) {
      showAlert(setupResult, "info",
        "The backend returned a provisioning URI instead of an image. URI (safe to open in an authenticator app): " + qrUrl);
    } else {
      showAlert(setupResult, "error",
        "Backend response did not contain a QR code. Check the /api/2fa/setup response schema.");
    }
    setupResult.hidden = false;
    toast("QR code generated for " + username + ".");
  });

  verifyForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const code = codeInput.value.trim();
    if (!/^[0-9]{6}$/.test(code)) {
      showAlert(verifyResult, "warn", "Please enter the six-digit code from your authenticator app.");
      return;
    }
    const username = currentUser || usernameInput.value.trim();
    if (!username) {
      showAlert(verifyResult, "warn", "Please enter a username in the field above or generate a QR code first.");
      return;
    }

    hideResult(verifyResult);
    setLoading(verifyBtn, true);
    const res = await apiPost("/api/2fa/verify", { username, code });
    setLoading(verifyBtn, false);
    codeInput.value = "";

    if (!res.ok) { showAlert(verifyResult, "error", res.message); return; }

    const d = res.data;
    const verified = pick(d, ["verified", "valid", "success", "is_valid"]);

    const verdict = el("div", "verdict " + (verified ? "verdict--ok" : "verdict--bad"),
      verified ? "✓ Code verified — 2FA authentication successful." : "✗ Verification failed. Check the code and try again.");
    verifyResult.textContent = "";
    verifyResult.appendChild(verdict);
    const msg = pick(d, ["message", "detail"]);
    if (msg) verifyResult.appendChild(el("p", "field__hint", String(msg)));
    verifyResult.hidden = false;
  });
}

/* ------------------------------------------------------------------ */
/* E. Breached Password Checker                                        */
/* ------------------------------------------------------------------ */

function initBreachChecker() {
  const form = document.getElementById("breach-form");
  const input = document.getElementById("breach-input");
  const btn = document.getElementById("breach-btn");
  const result = document.getElementById("breach-result");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const password = input.value;
    if (!password) return;

    hideResult(result);
    setLoading(btn, true);
    const res = await apiPost("/api/password/breach-check", { password });
    setLoading(btn, false);
    input.value = ""; // never retain passwords

    if (!res.ok) { showAlert(result, "error", res.message); return; }

    const d = res.data;
    const found = Boolean(pick(d, ["found", "breached", "is_breached", "pwned", "compromised"], false));
    const count = pick(d, ["count", "appearances", "times_seen", "pwned_count", "breach_count"]);

    result.textContent = "";
    const verdict = el("div", "verdict " + (found ? "verdict--bad" : "verdict--ok"),
      found
        ? "⚠ This password was found in known data breaches."
        : "✓ Good news — this password was NOT found in known breaches.");
    result.appendChild(verdict);

    if (found && count !== null && count !== undefined) {
      const stats = el("div", "stats");
      stats.appendChild(stat("Times seen in breaches", formatNumber(count)));
      result.appendChild(stats);
      const warn = el("div", "alert alert--warn");
      warn.appendChild(el("p", null,
        "If you use this password anywhere, change it immediately and never reuse it."));
      result.appendChild(warn);
    }
    if (!found) {
      const info = el("div", "alert alert--info");
      info.appendChild(el("p", null,
        "Not appearing in breach databases does not guarantee a password is strong — run the strength checker too."));
      result.appendChild(info);
    }
    result.hidden = false;
  });
}

/* ------------------------------------------------------------------ */
/* Clear buttons                                                       */
/* ------------------------------------------------------------------ */

function initClearButtons() {
  const map = {
    strength: ["strength-result", "strength-input"],
    generator: ["generator-result", null],
    passphrase: ["passphrase-result", null],
    twofa: ["twofa-setup-result", "twofa-verify-result", "twofa-username", "twofa-code"],
    breach: ["breach-result", "breach-input"],
  };
  document.querySelectorAll("[data-clear]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const ids = map[btn.dataset.clear] || [];
      ids.forEach((id) => {
        const node = document.getElementById(id);
        if (!node) return;
        if (node.tagName === "INPUT") node.value = "";
        else hideResult(node);
      });
      toast("Cleared.");
    });
  });
}

/* ------------------------------------------------------------------ */
/* Boot                                                                */
/* ------------------------------------------------------------------ */

document.addEventListener("DOMContentLoaded", () => {
  rememberLabels();
  initNavigation();
  initStrengthChecker();
  initGenerator();
  initPassphrase();
  initTwoFA();
  initBreachChecker();
  initClearButtons();
});
