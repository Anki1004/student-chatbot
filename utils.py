"""
utils.py — AI Academic Platform
=================================
Pure-Python utilities that do NOT call any AI API.
All functions work offline.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import os
from datetime import datetime, date, timedelta
from io import BytesIO

import streamlit as st


# ═════════════════════════════════════════════════════════════════════
#  1. Text helpers
# ═════════════════════════════════════════════════════════════════════

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "dare", "ought",
    "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
    "as", "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "each",
    "every", "both", "few", "more", "most", "other", "some", "such", "no",
    "nor", "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "about", "up",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "it", "its", "i", "me", "my", "we", "our", "you", "your", "he",
    "him", "his", "she", "her", "they", "them", "their",
}


def extract_code_block(text: str) -> tuple[str | None, str | None]:
    match = re.search(r"```(\w+)?\n([\s\S]*?)```", text)
    if match:
        return (match.group(1) or "").strip() or None, match.group(2).strip()
    if "\n" in text and any(s in text for s in ["def ", "class ", "{", "}", "import "]):
        return None, text.strip()
    return None, None


def detect_language(code: str, hinted: str | None = None) -> str:
    if hinted:
        return hinted.lower()
    checks = {
        "python":     [r"\bdef\b", r"\bimport\b", r"print\("],
        "java":       [r"\bpublic class\b", r"System\.out\.println", r"\bstatic void main\b"],
        "cpp":        [r"#include\s*<", r"std::", r"int\s+main\s*\("],
        "c":          [r"#include\s*<stdio\.h>", r"printf\("],
        "javascript": [r"\bfunction\b", r"console\.log\(", r"=>"],
        "sql":        [r"\bSELECT\b", r"\bINSERT\b", r"\bFROM\b"],
    }
    for lang, patterns in checks.items():
        if any(re.search(p, code, flags=re.IGNORECASE) for p in patterns):
            return lang
    return "text"


def chunk_text(text: str, max_size: int = 8000) -> list[str]:
    if len(text) <= max_size:
        return [text]
    chunks, current, current_len = [], [], 0
    for para in text.split("\n\n"):
        if current_len + len(para) > max_size and current:
            chunks.append("\n\n".join(current))
            current, current_len = [para], len(para)
        else:
            current.append(para)
            current_len += len(para)
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def strip_markdown(text: str) -> str:
    """Remove ALL markdown formatting for handwriting-style output."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_(.+?)_', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\-]\s+', '   ', text, flags=re.MULTILINE)
    text = re.sub(r'\*', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    for pat in [r'^.*?assignment submission.*?\n', r'^.*?submitted by.*?\n',
                r'^.*?introduction\s*\n', r'^.*?conclusion\s*\n']:
        text = re.sub(pat, '', text, flags=re.IGNORECASE | re.MULTILINE)
    return text.strip()


# ═════════════════════════════════════════════════════════════════════
#  2. PDF helpers (with stopword-filtered relevance)
# ═════════════════════════════════════════════════════════════════════

def extract_pdf_text(uploaded_file) -> tuple[str | None, str | None]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, "pypdf not installed. Run: pip install pypdf"
    try:
        reader = PdfReader(BytesIO(uploaded_file.read()))
        pages = []
        for num, page in enumerate(reader.pages, 1):
            t = page.extract_text() or ""
            if t.strip():
                pages.append(f"[Page {num}]\n{t}")
        full = "\n\n".join(pages)
        if not full.strip():
            return None, "No extractable text found in this PDF."
        return full, None
    except Exception as exc:
        return None, f"Error reading PDF: {exc}"


def pdf_stats(text: str) -> dict:
    """Return page count, word count, char count for a PDF text."""
    pages = text.count("[Page ")
    words = len(text.split())
    return {"pages": pages, "words": words, "chars": len(text)}


def find_relevant_pdf_content(pdf_text: str, query: str, max_length: int = 6000) -> str:
    """Score chunks against query with stopword filtering."""
    query_words = {w for w in query.lower().split() if len(w) > 2 and w not in STOPWORDS}
    chunks = chunk_text(pdf_text, max_size=2000)
    if len(chunks) <= 1:
        return pdf_text[:max_length]

    scored = []
    for chunk in chunks:
        lower = chunk.lower()
        score = sum(1 for w in query_words if w in lower)
        scored.append((score, chunk))
    scored.sort(reverse=True, key=lambda x: x[0])
    top = [c for s, c in scored[:3] if s > 0] or [chunks[0]]
    return "\n\n".join(top)[:max_length]


# ═════════════════════════════════════════════════════════════════════
#  3. Session analytics
# ═════════════════════════════════════════════════════════════════════

def track_feature(name: str) -> None:
    usage = st.session_state.get("feature_usage", {})
    if name in usage:
        usage[name] += 1


def get_most_used() -> list[tuple[str, int]]:
    return sorted(
        st.session_state.get("feature_usage", {}).items(),
        key=lambda x: x[1], reverse=True,
    )


def session_duration() -> str:
    start: datetime = st.session_state.get("session_start_dt", datetime.now())
    total = int((datetime.now() - start).total_seconds() / 60)
    h, m = divmod(total, 60)
    return f"{h}h {m}m" if h else f"{m}m"


# ═════════════════════════════════════════════════════════════════════
#  4. Study tracking
# ═════════════════════════════════════════════════════════════════════

_CS_TOPICS = [
    "python", "java", "c++", "javascript", "sql", "html", "css",
    "dbms", "database", "os", "operating system", "networking",
    "data structures", "algorithms", "dsa", "oops", "object oriented",
    "ai", "machine learning", "cloud", "web development",
    "software engineering", "mathematics", "statistics", "calculus",
]


def extract_topics(text: str) -> list[str]:
    lower = text.lower()
    return [t.title() for t in _CS_TOPICS if t in lower]


def update_study_tracking(user_text: str) -> None:
    topics = extract_topics(user_text)
    existing = st.session_state.get("topics_studied", [])
    for t in topics:
        if t not in existing:
            existing.append(t)
    st.session_state.topics_studied = existing
    st.session_state.questions_asked = st.session_state.get("questions_asked", 0) + 1

    # Streak logic
    today = date.today()
    last = st.session_state.get("last_active_date", today)
    if today == last + timedelta(days=1):
        st.session_state.streak = st.session_state.get("streak", 1) + 1
        st.session_state.best_streak = max(
            st.session_state.get("best_streak", 1), st.session_state.streak
        )
    elif today > last + timedelta(days=1):
        st.session_state.streak = 1
    st.session_state.last_active_date = today


# ═════════════════════════════════════════════════════════════════════
#  5. User profile
# ═════════════════════════════════════════════════════════════════════

def detect_user_info(text: str) -> None:
    match = re.search(r"my name is ([a-zA-Z]+)", text, re.IGNORECASE)
    if match:
        st.session_state["user_name"] = match.group(1).capitalize()


def get_user_profile_summary() -> str:
    parts = []
    if st.session_state.get("user_name"):
        parts.append(f"👤 **{st.session_state['user_name']}**")
    q = st.session_state.get("questions_asked", 0)
    t = len(st.session_state.get("topics_studied", []))
    parts.append(f"❓ Questions asked: **{q}**")
    parts.append(f"📚 Topics explored: **{t}**")
    return "\n\n".join(parts) if parts else "No profile data yet."


# ═════════════════════════════════════════════════════════════════════
#  6. Safe Python code runner (improved blocklist)
# ═════════════════════════════════════════════════════════════════════

_BLOCKED = [
    "import os", "import sys", "import subprocess", "import shutil",
    "import socket", "import signal", "import ctypes", "import pickle",
    "__import__", "open(", "eval(", "exec(", "compile(",
    "os.system", "os.popen", "os.remove", "os.rmdir",
    "getattr(", "setattr(", "delattr(", "globals(", "locals(",
    "breakpoint(", "importlib",
]


def execute_python(code: str, timeout: int = 10) -> tuple[str, str]:
    """Execute code safely. Returns (stdout, stderr)."""
    for b in _BLOCKED:
        if b in code:
            return "", f"⛔ Blocked: '{b}' is not allowed for security reasons."

    tmp = ""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            [sys.executable, tmp], capture_output=True, text=True, timeout=timeout,
        )
        return result.stdout[:4000], result.stderr[:2000]
    except subprocess.TimeoutExpired:
        return "", f"⏱️ Code timed out after {timeout} seconds."
    except Exception as exc:
        return "", str(exc)
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


# ═════════════════════════════════════════════════════════════════════
#  7. Study planner (with priority weighting)
# ═════════════════════════════════════════════════════════════════════

def build_study_plan(
    subjects: list[dict],  # [{"name": str, "priority": "Weak"/"Average"/"Strong"}]
    exam_date: date,
    hours_day: float,
) -> list[dict]:
    today = date.today()
    days_left = (exam_date - today).days
    if days_left <= 0 or not subjects:
        return []

    # Weight subjects by priority
    weights = {"Weak": 3, "Average": 2, "Strong": 1}
    weighted = []
    for s in subjects:
        w = weights.get(s.get("priority", "Average"), 2)
        weighted.extend([s["name"]] * w)

    plan = []
    day = today
    idx = 0
    while day < exam_date:
        is_rev = (exam_date - day).days <= 3
        if is_rev:
            subject = "All Subjects — Revision"
            note = "Final revision: past papers + formula sheets"
        else:
            subject = weighted[idx % len(weighted)]
            note = "Study + practice problems"
            idx += 1
        plan.append({
            "date": day.strftime("%a, %d %b %Y"),
            "subject": subject,
            "hours": hours_day if not is_rev else min(hours_day + 1, 8),
            "note": note,
            "is_revision": is_rev,
        })
        day += timedelta(days=1)
    return plan


# ═════════════════════════════════════════════════════════════════════
#  8. Study recommender (rule-based)
# ═════════════════════════════════════════════════════════════════════

_RESOURCES: dict[str, list[str]] = {
    "python":           ["docs.python.org", "realpython.com", "Python Crash Course (book)"],
    "java":             ["docs.oracle.com/javase", "Head First Java (book)"],
    "data structures":  ["visualgo.net", "CLRS (book)"],
    "dbms":             ["sqlzoo.net", "Database System Concepts — Silberschatz"],
    "operating system": ["studytonight.com/os", "Modern Operating Systems — Tanenbaum"],
    "networking":       ["cisco.com training", "Kurose & Ross (book)"],
    "mathematics":      ["khanacademy.org", "brilliant.org"],
    "machine learning": ["fast.ai", "Andrew Ng Coursera", "Hands-On ML (book)"],
}


def get_recommendations() -> str:
    topics = [t.lower() for t in st.session_state.get("topics_studied", [])]
    lines = ["### 📚 Recommended Resources\n"]
    matched = False
    for topic, resources in _RESOURCES.items():
        if any(topic in t or t in topic for t in topics):
            lines.append(f"**{topic.title()}**")
            for r in resources:
                lines.append(f"  • {r}")
            matched = True
    if not matched:
        lines.append(
            "Start learning a topic and I'll personalise recommendations!\n\n"
            "Popular starting points: Python · DBMS · Data Structures · OS"
        )
    return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════════
#  9. Citation builder (programmatic — not AI-dependent)
# ═════════════════════════════════════════════════════════════════════

def build_citation(
    style: str,
    source_type: str,
    authors: str,
    year: str,
    title: str,
    **kwargs,
) -> dict[str, str]:
    """Build a formatted citation. Returns {"full": ..., "inline": ...}."""
    authors = authors.strip() or "Unknown"
    year = year.strip() or "n.d."
    title = title.strip()

    if style.startswith("APA"):
        return _apa_citation(source_type, authors, year, title, **kwargs)
    elif style.startswith("MLA"):
        return _mla_citation(source_type, authors, year, title, **kwargs)
    elif style == "IEEE":
        return _ieee_citation(source_type, authors, year, title, **kwargs)
    else:
        # Harvard / Chicago — use APA-like as default
        return _apa_citation(source_type, authors, year, title, **kwargs)


def _apa_citation(stype, authors, year, title, **kw) -> dict:
    if stype == "Book":
        full = f"{authors} ({year}). *{title}*. {kw.get('publisher', '')}."
    elif stype == "Journal Article":
        full = (f"{authors} ({year}). {title}. *{kw.get('journal', '')}*, "
                f"{kw.get('volume', '')}({kw.get('issue', '')}), {kw.get('pages', '')}.")
        if kw.get("doi"):
            full += f" https://doi.org/{kw['doi']}"
    elif stype == "Website":
        full = f"{authors} ({year}). *{title}*. Retrieved from {kw.get('url', '')}"
    else:
        full = f"{authors} ({year}). {title}. {kw.get('publisher', '')}."

    first_author = authors.split(",")[0].split("&")[0].strip().split()[-1] if authors != "Unknown" else "Unknown"
    inline = f"({first_author}, {year})"
    return {"full": full.strip(), "inline": inline}


def _mla_citation(stype, authors, year, title, **kw) -> dict:
    if stype == "Book":
        full = f"{authors}. *{title}*. {kw.get('publisher', '')}, {year}."
    elif stype == "Website":
        full = f"{authors}. \"{title}.\" *{kw.get('site_name', 'Web')}*, {year}, {kw.get('url', '')}."
    else:
        full = f"{authors}. \"{title}.\" {kw.get('publisher', '')}, {year}."
    first_author = authors.split(",")[0].strip().split()[-1] if authors != "Unknown" else "Unknown"
    inline = f"({first_author} {kw.get('pages', '')})" if kw.get("pages") else f"({first_author})"
    return {"full": full.strip(), "inline": inline}


def _ieee_citation(stype, authors, year, title, **kw) -> dict:
    if stype == "Journal Article":
        full = (f"{authors}, \"{title},\" *{kw.get('journal', '')}*, "
                f"vol. {kw.get('volume', '')}, pp. {kw.get('pages', '')}, {year}.")
    else:
        full = f"{authors}, \"{title},\" {kw.get('publisher', '')}, {year}."
    inline = "[1]"
    return {"full": full.strip(), "inline": inline}


# ═════════════════════════════════════════════════════════════════════
#  10. Quiz parser (for interactive quiz mode)
# ═════════════════════════════════════════════════════════════════════

def parse_quiz(raw: str) -> list[dict]:
    """Parse AI-generated quiz into structured data.
    Returns: [{"question": str, "options": {"A":..,"B":..}, "correct": "A", "explanation": str}]
    """
    questions = []
    # Split by Q1., Q2., etc.
    blocks = re.split(r'Q\d+[\.\)]\s*', raw)
    for block in blocks:
        if not block.strip():
            continue
        lines = block.strip().split("\n")
        q_text = lines[0].strip() if lines else ""
        options = {}
        correct = ""
        explanation = ""
        for line in lines[1:]:
            line = line.strip()
            opt_match = re.match(r'^([A-D])\)\s*(.+)', line)
            if opt_match:
                options[opt_match.group(1)] = opt_match.group(2).strip()
                continue
            corr_match = re.match(r'CORRECT:\s*([A-D])', line, re.IGNORECASE)
            if corr_match:
                correct = corr_match.group(1).upper()
                continue
            exp_match = re.match(r'EXPLANATION:\s*(.+)', line, re.IGNORECASE)
            if exp_match:
                explanation = exp_match.group(1).strip()
                continue
        if q_text and len(options) >= 2 and correct:
            questions.append({
                "question": q_text,
                "options": options,
                "correct": correct,
                "explanation": explanation,
            })
    return questions


# ═════════════════════════════════════════════════════════════════════
#  11. Flashcard parser
# ═════════════════════════════════════════════════════════════════════

def parse_flashcards(raw: str) -> list[dict]:
    """Parse AI flashcard output into [{"q": ..., "a": ...}]."""
    cards = []
    blocks = re.split(r'CARD\s+\d+', raw, flags=re.IGNORECASE)
    for block in blocks:
        q = re.search(r'Q:\s*(.+?)(?=\nA:|\Z)', block, re.DOTALL | re.IGNORECASE)
        a = re.search(r'A:\s*(.+?)(?=\n\n|\Z)', block, re.DOTALL | re.IGNORECASE)
        if q and a:
            cards.append({"q": q.group(1).strip(), "a": a.group(1).strip()})
    return cards


# ═════════════════════════════════════════════════════════════════════
#  12. Viva Q&A parser
# ═════════════════════════════════════════════════════════════════════

def parse_viva_qa(raw: str) -> list[tuple[str, str]]:
    """Parse viva Q&A into [(question, answer), ...]."""
    return re.findall(
        r'Q\d+[:.]\s*(.+?)\nA\d+[:.]\s*(.+?)(?=\nQ\d+|\Z)',
        raw, re.DOTALL,
    )


# ═════════════════════════════════════════════════════════════════════
#  13. Tavily web search helper
# ═════════════════════════════════════════════════════════════════════

def tavily_search(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
    include_answer: bool = True,
    topic: str = "general",
) -> dict | None:
    try:
        from tavily import TavilyClient
    except ImportError:
        return None
    try:
        key = str(st.secrets.get("TAVILY_API_KEY", "")).strip()
        if not key:
            return None
        client = TavilyClient(api_key=key)
        return client.search(
            query=query, search_depth=search_depth,
            max_results=max_results, include_answer=include_answer, topic=topic,
        )
    except Exception:
        return None


# ═════════════════════════════════════════════════════════════════════
#  14. Visual diagram detector
# ═════════════════════════════════════════════════════════════════════

_VISUAL_KEYWORDS: frozenset[str] = frozenset([
    # Data structures
    "tree", "binary tree", "bst", "avl", "avl tree", "heap", "trie", "b-tree",
    "b+ tree", "red-black tree", "segment tree", "fenwick tree",
    "linked list", "doubly linked", "circular linked", "singly linked",
    "stack", "queue", "deque", "priority queue", "circular queue",
    # Graph algorithms
    "graph", "bfs", "breadth first", "dfs", "depth first",
    "dijkstra", "bellman ford", "kruskal", "prim", "floyd",
    "adjacency list", "adjacency matrix", "spanning tree", "topological sort",
    "minimum spanning", "shortest path",
    # Sorting & searching
    "sorting", "bubble sort", "merge sort", "quick sort", "insertion sort",
    "selection sort", "radix sort", "counting sort", "heap sort", "shell sort",
    "binary search", "linear search", "hashing", "hash table", "hash map",
    # OOP & design
    "oop", "object oriented", "inheritance", "polymorphism", "encapsulation",
    "abstraction", "class diagram", "uml", "design pattern", "singleton",
    "factory pattern", "observer pattern", "mvc",
    # Networking & OS
    "osi model", "osi layer", "tcp", "tcp/ip", "udp", "http", "dns",
    "network layer", "protocol", "handshake", "socket",
    "process scheduling", "round robin", "fcfs", "sjf", "priority scheduling",
    "deadlock", "paging", "segmentation", "virtual memory", "page table",
    "memory management", "cache", "thrashing",
    # Database
    "normalization", "er diagram", "entity relationship", "foreign key",
    "primary key", "database schema", "sql join", "relational", "nosql",
    "transaction", "acid", "indexing",
    # Algorithms & CS theory
    "recursion", "dynamic programming", "memoization", "greedy algorithm",
    "divide and conquer", "backtracking", "flowchart", "algorithm",
    "data structure", "time complexity", "space complexity", "big-o",
    "compilation", "compiler", "lexer", "parser", "automata", "finite state",
    # Architecture
    "microservices", "client server", "rest api", "system design",
    "load balancer", "message queue", "pub sub",
])


def should_visualize(text: str) -> bool:
    """Return True if the topic would benefit from a Mermaid diagram."""
    lower = text.lower()
    return any(kw in lower for kw in _VISUAL_KEYWORDS)


_MERMAID_STARTS = (
    "graph ", "flowchart ", "sequenceDiagram", "classDiagram",
    "erDiagram", "stateDiagram", "gantt", "pie ", "mindmap", "timeline",
)


def clean_mermaid(raw: str) -> str:
    """
    Robustly extract Mermaid code from AI output.
    Handles: fenced blocks, preamble text, trailing explanations.
    """
    if not raw:
        return ""

    # 1. Try to pull code out of a ```mermaid ... ``` or ``` ... ``` fence
    fence = re.search(r'```(?:mermaid)?\s*\n([\s\S]+?)\n?```', raw)
    if fence:
        return fence.group(1).strip()

    code = raw.strip()

    # 2. Strip any leading ``` line
    code = re.sub(r'^```[a-zA-Z]*\s*\n?', '', code)
    # Strip any trailing ``` line
    code = re.sub(r'\n?```\s*$', '', code)
    code = code.strip()

    # 3. If the code already starts with a valid Mermaid keyword, return it
    if any(code.startswith(s) for s in _MERMAID_STARTS):
        # Also strip any trailing explanation text after the diagram
        # (anything after an empty line that doesn't look like Mermaid)
        lines = code.split('\n')
        clean_lines = []
        for line in lines:
            # Stop at lines that look like plain-English explanations
            if clean_lines and re.match(r'^(This |The |Note:|Here|In this|Explanation)', line):
                break
            clean_lines.append(line)
        return '\n'.join(clean_lines).strip()

    # 4. Find the first occurrence of a Mermaid keyword anywhere in the text
    best_idx = len(code)
    for s in _MERMAID_STARTS:
        idx = code.find(s)
        if idx != -1 and idx < best_idx:
            best_idx = idx
    if best_idx < len(code):
        return code[best_idx:].strip()

    # 5. Last resort — return whatever we have
    return code.strip()


def tavily_available() -> bool:
    try:
        import importlib
        if importlib.util.find_spec("tavily") is None:
            return False
        return bool(str(st.secrets.get("TAVILY_API_KEY", "")).strip())
    except Exception:
        return False
