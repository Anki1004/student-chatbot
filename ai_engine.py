"""
ai_engine.py — AI Academic Platform
=====================================
8-tier fallback cascade:
  1. NVIDIA NIM  (round-robin keys)  — Llama 3.3 / Mistral / Nemotron
  2. OpenRouter   (3 free models)
  3. Gemini Flash (round-robin keys)
  4. Claude Haiku
  5. Rules Engine (deterministic FAQ)
  6. Caller fallback
  7. Static error message

Public API:
  get_response(prompt, system_prompt, fallback_msg) -> (text, source)
  ai_available() -> bool
"""

from __future__ import annotations
import re
import streamlit as st

DEBUG: bool = False

# ── Model lists ──────────────────────────────────────────────────────
NVIDIA_MODELS = [
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.1-24b-instruct",
    "nvidia/llama-3.1-nemotron-70b-instruct",
]
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

OPENROUTER_MODELS = [
    "stepfun/step-3.5-flash:free",
    "arcee-ai/trinity-large-preview:free",
    "liquid/lfm-2.5-1.2b-thinking:free",
]


# ── Helpers ──────────────────────────────────────────────────────────
def _log(tag: str, msg: str) -> None:
    if DEBUG:
        print(f"[AI-ENGINE | {tag}] {msg}", flush=True)


def _load_keys(secret_name: str) -> list[str]:
    try:
        raw = st.secrets[secret_name]
        if isinstance(raw, str):
            return [k.strip() for k in raw.split(",") if k.strip()]
        return [str(k).strip() for k in raw if str(k).strip()]
    except Exception:
        return []


def _load_key(secret_name: str) -> str | None:
    try:
        key = str(st.secrets[secret_name]).strip()
        return key or None
    except Exception:
        return None


# ── 1. NVIDIA NIM ────────────────────────────────────────────────────
def _call_nvidia(prompt: str, system_prompt: str) -> str | None:
    try:
        import requests
    except ImportError:
        return None

    keys = _load_keys("NVIDIA_NIM_KEYS")
    if not keys:
        return None

    n = len(keys)
    start = int(st.session_state.get("_nvidia_idx", 0)) % n

    for i in range(n):
        idx = (start + i) % n
        key = keys[idx]
        for model in NVIDIA_MODELS:
            try:
                _log("NVIDIA", f"key[{idx}] → {model}")
                resp = requests.post(
                    NVIDIA_URL,
                    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "stream": False,
                    },
                    timeout=45,
                )
                if resp.status_code in (401, 429):
                    break  # bad key or rate limited → next key
                if resp.status_code != 200:
                    continue  # try next model
                choices = resp.json().get("choices", [])
                text = (choices[0].get("message", {}).get("content") or "").strip() if choices else ""
                if text:
                    st.session_state["_nvidia_idx"] = (idx + 1) % n
                    _log("NVIDIA", f"✓ key[{idx}] {model}")
                    return text
            except Exception as exc:
                _log("NVIDIA", f"key[{idx}] {model} FAIL: {exc}")
                break
    return None


# ── 2-4. OpenRouter ──────────────────────────────────────────────────
def _call_openrouter(prompt: str, system_prompt: str) -> str | None:
    try:
        import requests
    except ImportError:
        return None

    key = _load_key("OPENROUTER_API_KEY")
    if not key:
        return None

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    for model in OPENROUTER_MODELS:
        try:
            _log("OPENROUTER", f"→ {model}")
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": 2048,
                    "temperature": 0.7,
                },
                timeout=45,
            )
            if resp.status_code != 200:
                continue
            choices = resp.json().get("choices", [])
            text = (choices[0].get("message", {}).get("content") or "").strip() if choices else ""
            if text:
                _log("OPENROUTER", f"✓ {model}")
                return text
        except Exception as exc:
            _log("OPENROUTER", f"{model} FAIL: {exc}")
    return None


# ── 5. Gemini ────────────────────────────────────────────────────────
def _call_gemini(prompt: str, system_prompt: str) -> str | None:
    try:
        import google.generativeai as genai
    except ImportError:
        return None

    keys = _load_keys("GEMINI_KEYS")
    if not keys:
        return None

    n = len(keys)
    start = int(st.session_state.get("_gemini_idx", 0)) % n
    full = f"{system_prompt}\n\n{prompt}"

    for i in range(n):
        idx = (start + i) % n
        try:
            _log("GEMINI", f"key[{idx}]")
            genai.configure(api_key=keys[idx])
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={"temperature": 0.7, "max_output_tokens": 2048},
            )
            response = model.generate_content(full)
            text = (response.text or "").strip()
            if text:
                st.session_state["_gemini_idx"] = (idx + 1) % n
                _log("GEMINI", f"✓ key[{idx}]")
                return text
        except Exception as exc:
            _log("GEMINI", f"key[{idx}] FAIL: {exc}")
    return None


# ── 6. Claude ────────────────────────────────────────────────────────
def _call_claude(prompt: str, system_prompt: str) -> str | None:
    try:
        from anthropic import Anthropic
    except ImportError:
        return None

    key = _load_key("CLAUDE_API_KEY")
    if not key:
        return None

    try:
        _log("CLAUDE", "→ claude-3-haiku")
        client = Anthropic(api_key=key, timeout=45.0)
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )
        text = "\n".join(b.text for b in response.content if b.type == "text").strip()
        if text:
            _log("CLAUDE", "✓")
            return text
    except Exception as exc:
        _log("CLAUDE", f"FAIL: {exc}")
    return None


# ── 7. Rules Engine ──────────────────────────────────────────────────
_FAQ: list[tuple[list[str], str]] = [
    (["what is python", "explain python", "define python"],
     "**Python** is a high-level, interpreted programming language known for its clear syntax. "
     "It supports multiple paradigms and is widely used in web development, data science, AI/ML, and automation."),
    (["what is java", "explain java"],
     "**Java** is a class-based, object-oriented language designed for portability (Write Once, Run Anywhere). "
     "It runs on the JVM and is used for enterprise apps, Android development, and large-scale systems."),
    (["what is html", "explain html"],
     "**HTML (HyperText Markup Language)** is the standard markup language for web pages. "
     "HTML5 adds semantic elements, audio/video, and canvas support."),
    (["what is css", "explain css"],
     "**CSS (Cascading Style Sheets)** controls visual presentation — layout, colors, fonts, spacing. "
     "Supports responsive layouts via media queries, Flexbox, and Grid."),
    (["what is javascript", "explain javascript"],
     "**JavaScript** is a dynamic language for interactive web pages. "
     "Runs in browsers and on servers (Node.js), supporting event-driven and async programming."),
    (["what is dbms", "explain dbms"],
     "**DBMS** stores, retrieves, and manages data. Types: Relational (MySQL, PostgreSQL), NoSQL (MongoDB). "
     "Key concepts: ACID, normalization, SQL, indexing, transactions."),
    (["what is operating system", "explain os", "what is os"],
     "**Operating System** manages hardware and provides services to programs. "
     "Key functions: process management, memory, file systems, I/O."),
    (["what is data structure", "explain data structure"],
     "**Data Structures** organize and store data for efficient access. "
     "Common: Arrays, Linked Lists, Stacks, Queues, Trees, Graphs, Hash Tables."),
    (["what is algorithm", "explain algorithm"],
     "**Algorithm** is a step-by-step procedure for solving a problem. "
     "Key concepts: Big-O, sorting, searching, DP, greedy, BFS/DFS."),
    (["what is oops", "explain oops", "what is oop"],
     "**OOP** is based on objects with data (attributes) and code (methods). "
     "Four pillars: Encapsulation, Abstraction, Inheritance, Polymorphism."),
    (["what is machine learning", "explain machine learning", "what is ml"],
     "**Machine Learning** systems learn patterns from data. "
     "Types: Supervised, Unsupervised, Reinforcement Learning."),
    (["what is sql", "explain sql"],
     "**SQL** manages relational databases. Key commands: SELECT, INSERT, UPDATE, DELETE, JOIN, GROUP BY."),
    (["how to study", "study tips"],
     "**Effective Study Strategies:**\n"
     "1. Active Recall — test yourself\n2. Spaced Repetition\n3. Pomodoro Technique\n"
     "4. Feynman Technique\n5. Past Papers\n6. Teach Others"),
]


def _rules_engine(prompt: str) -> str | None:
    lower = prompt.lower().strip()
    # Strip common prefixes
    for prefix in ["generate", "summarise", "write", "debug"]:
        if lower.startswith(prefix):
            parts = lower.split("\n\n", 1)
            if len(parts) > 1:
                lower = parts[1]

    for patterns, answer in _FAQ:
        if any(p in lower for p in patterns):
            _log("RULES", "✓ matched")
            return answer
    return None


# ── Vision helpers (for OCR & Assignment Solver) ─────────────────────
def call_vision(image_bytes: bytes, prompt: str, mime: str = "image/jpeg") -> str | None:
    """Try NVIDIA Vision → Gemini Vision. Returns text or None."""
    result = _nvidia_vision(image_bytes, prompt, mime)
    if result:
        return result
    return _gemini_vision(image_bytes, prompt)


def _nvidia_vision(image_bytes: bytes, prompt: str, mime: str) -> str | None:
    try:
        import requests, base64
    except ImportError:
        return None
    keys = _load_keys("NVIDIA_NIM_KEYS")
    if not keys:
        return None
    try:
        b64 = base64.b64encode(image_bytes).decode()
        resp = requests.post(
            "https://integrate.api.nvidia.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {keys[0]}", "Content-Type": "application/json"},
            json={
                "model": "meta/llama-3.2-90b-vision-instruct",
                "messages": [{"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
                    {"type": "text", "text": prompt},
                ]}],
                "max_tokens": 1024, "temperature": 0.1, "stream": False,
            },
            timeout=30,
        )
        if resp.status_code != 200:
            return None
        choices = resp.json().get("choices", [])
        return (choices[0].get("message", {}).get("content") or "").strip() or None
    except Exception:
        return None


def _gemini_vision(image_bytes: bytes, prompt: str) -> str | None:
    try:
        import google.generativeai as genai
        from PIL import Image as PILImage
        import io
    except ImportError:
        return None
    keys = _load_keys("GEMINI_KEYS")
    if not keys:
        return None
    try:
        genai.configure(api_key=keys[0])
        model = genai.GenerativeModel("gemini-1.5-flash")
        img = PILImage.open(io.BytesIO(image_bytes))
        response = model.generate_content([prompt, img])
        return (response.text or "").strip() or None
    except Exception:
        return None


# ── Public API ───────────────────────────────────────────────────────
def get_response(
    prompt: str,
    system_prompt: str = "You are a helpful academic AI assistant for college students.",
    fallback_msg: str | None = None,
) -> tuple[str, str]:
    """
    Returns (answer, source_label).
    Cascades through all providers; never crashes.
    """
    # 1. NVIDIA NIM
    text = _call_nvidia(prompt, system_prompt)
    if text:
        return text, "nvidia"

    # 2-4. OpenRouter
    text = _call_openrouter(prompt, system_prompt)
    if text:
        return text, "openrouter"

    # 5. Gemini
    text = _call_gemini(prompt, system_prompt)
    if text:
        return text, "gemini"

    # 6. Claude
    text = _call_claude(prompt, system_prompt)
    if text:
        return text, "claude"

    # 7. Rules Engine
    text = _rules_engine(prompt)
    if text:
        return text, "rules"

    # 8. Fallbacks
    if fallback_msg:
        return fallback_msg, "offline"

    return (
        "⚠️ AI service temporarily unavailable. "
        "Please check your API keys in `.streamlit/secrets.toml` and try again.",
        "error",
    )


def ai_available() -> bool:
    return bool(
        _load_keys("NVIDIA_NIM_KEYS")
        or _load_key("OPENROUTER_API_KEY")
        or _load_keys("GEMINI_KEYS")
        or _load_key("CLAUDE_API_KEY")
    )
