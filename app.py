"""
app.py — AI Academic Platform v3.0
====================================
Architecture:
  app.py       → UI routing, session state, all page functions
  ai_engine.py → NVIDIA NIM → OpenRouter → Gemini → Claude → Rules Engine
  utils.py     → All offline Python utilities
  prompts.py   → Centralised AI prompts
  styles.py    → All CSS

23 Tools · Multi-provider AI · Live Web Search · Gamification
"""

from __future__ import annotations

import re
import random
from datetime import datetime, date

import streamlit as st

from ai_engine import get_response, ai_available, call_vision
from prompts import (
    build_system_prompt, build_user_prompt, VISION_PROMPT,
    NOTES_SUMMARY, ASSIGNMENT_GEN, ASSIGNMENT_CHECK, EXAM_PAPER,
    QUIZ_GEN, MATH_SOLVE, FLASHCARD_GEN, VIVA_PREP, MOCK_VIVA,
    FORMULA_SHEET, CODE_DEBUG, CODE_EXPLAIN, CODE_OPTIMISE,
    CODE_WRITE, CODE_CONVERT, TRANSLATE, STUDY_RECOMMEND,
    STUDY_TIPS, ASSIGNMENT_SOLVER, WEB_SEARCH_SYNTHESIZE,
    DIAGRAM_GEN,
)
from utils import (
    extract_pdf_text, pdf_stats, find_relevant_pdf_content,
    execute_python, detect_language, strip_markdown,
    track_feature, get_most_used, session_duration,
    update_study_tracking, detect_user_info, get_user_profile_summary,
    get_recommendations, build_study_plan, build_citation,
    parse_quiz, parse_flashcards, parse_viva_qa,
    tavily_search, tavily_available,
    should_visualize, clean_mermaid,
)
from styles import CSS

TOOL_COUNT = 24

# ═════════════════════════════════════════════════════════════════════
#  Page config (MUST be first Streamlit call)
# ═════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="AI Academic Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject CSS
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# Header
st.markdown(
    '<div class="app-header animate-in">'
    '<h1>🎓 AI Academic Platform</h1>'
    f'<p>Your intelligent study companion · <span class="tool-count">{TOOL_COUNT} AI Tools + Live Web Search</span></p>'
    '</div>',
    unsafe_allow_html=True,
)


# ═════════════════════════════════════════════════════════════════════
#  Navigation
# ═════════════════════════════════════════════════════════════════════

NAV = [
    "🏠 Home",
    "🖼️ Image OCR",
    "📄 PDF Study Chat",
    "📝 Notes Summarizer",
    "✍️ Assignment Generator",
    "✓ Assignment Checker",
    "📅 Study Planner",
    "🧾 Exam Paper Generator",
    "💻 Code Runner",
    "🎓 Study Recommender",
    "📝 Study Notepad",
    "📊 Dashboard",
    "💬 AI Chat",
    "🧩 Quiz Generator",
    "🐛 Code Helper",
    "🧮 Math Solver",
    "📇 Flashcard Maker",
    "🎤 Viva Prep",
    "📖 Citation Generator",
    "🌐 Language Translator",
    "📐 Formula Sheet",
    "🔍 Web Search",
    "📸 Assignment Solver",
    "🌳 Visual Explainer",
]

NAV_MODE = {
    "🏠 Home":                 "General Study Assistant",
    "🖼️ Image OCR":            "General Study Assistant",
    "📄 PDF Study Chat":       "General Study Assistant",
    "📝 Notes Summarizer":     "Notes Summarizer",
    "✍️ Assignment Generator": "Assignment Writer",
    "✓ Assignment Checker":    "General Study Assistant",
    "📅 Study Planner":        "Study Planner",
    "🧾 Exam Paper Generator": "Exam Prep",
    "💻 Code Runner":          "Programming Helper",
    "🎓 Study Recommender":    "General Study Assistant",
    "📝 Study Notepad":        "General Study Assistant",
    "📊 Dashboard":            "General Study Assistant",
    "💬 AI Chat":              "General Study Assistant",
    "🧩 Quiz Generator":       "Quiz Generator",
    "🐛 Code Helper":          "Code Debugger",
    "🧮 Math Solver":          "General Study Assistant",
    "📇 Flashcard Maker":      "General Study Assistant",
    "🎤 Viva Prep":            "Exam Prep",
    "📖 Citation Generator":   "General Study Assistant",
    "🌐 Language Translator":  "General Study Assistant",
    "📐 Formula Sheet":        "General Study Assistant",
    "🔍 Web Search":           "General Study Assistant",
    "📸 Assignment Solver":    "Assignment Writer",
    "🌳 Visual Explainer":    "General Study Assistant",
}


# ═════════════════════════════════════════════════════════════════════
#  Rank system
# ═════════════════════════════════════════════════════════════════════

RANKS = [
    (0,    "🥉 Bronze",  "rank-bronze",  100),
    (100,  "🥈 Silver",  "rank-silver",  300),
    (300,  "🥇 Gold",    "rank-gold",    600),
    (600,  "💎 Diamond", "rank-diamond", 1000),
    (1000, "👑 Master",  "rank-master",  99999),
]

def get_rank(pts: int) -> tuple[str, str, int, int]:
    for i, (thresh, label, css, _) in enumerate(RANKS):
        if i == len(RANKS) - 1 or pts < RANKS[i + 1][0]:
            nxt = RANKS[i + 1][0] if i < len(RANKS) - 1 else thresh + 1
            return label, css, thresh, nxt
    return RANKS[-1][1], RANKS[-1][2], RANKS[-1][0], RANKS[-1][0] + 1


# ═════════════════════════════════════════════════════════════════════
#  Session state
# ═════════════════════════════════════════════════════════════════════

_DEFAULTS = {
    "nav":              "🏠 Home",
    "mode":             "General Study Assistant",
    "messages":         [],
    "session_start_dt": datetime.now(),
    "questions_asked":  0,
    "topics_studied":   [],
    "points":           0,
    "streak":           1,
    "best_streak":      1,
    "last_active_date": datetime.now().date(),
    "badges":           [],
    "user_name":        None,
    "feature_usage": {
        "AI Chat": 0, "PDF Study Chat": 0, "Quiz Generator": 0,
        "Code Helper": 0, "Notes Summarizer": 0, "Assignment Generator": 0,
        "Assignment Checker": 0, "Study Planner": 0, "Exam Paper Generator": 0,
        "Code Runner": 0, "Study Recommender": 0, "Math Solver": 0,
        "Flashcard Maker": 0, "Viva Prep": 0, "Citation Generator": 0,
        "Language Translator": 0, "Formula Sheet": 0, "Web Search": 0,
        "Assignment Solver": 0, "Image OCR": 0,
    },
    "pdf_content":       None,
    "pdf_filename":      None,
    "pdf_chat_history":  [],
    "code_output":       "",
    "code_error":        "",
    "_nvidia_idx":       0,
    "_gemini_idx":       0,
    "flashcards":        [],
    "quiz_data":         None,
    "quiz_answers":      {},
    "quiz_submitted":    False,
    "viva_data":         None,
    "notepad_notes":     "",
    "notepad_bookmarks": [],
    "citation_list":     [],
    "last_diagram":      None,   # mermaid code for last visual topic
    "last_diagram_topic": "",
    "diagram_auto":      True,   # auto-generate diagrams in AI chat
}

for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ═════════════════════════════════════════════════════════════════════
#  Shared helpers
# ═════════════════════════════════════════════════════════════════════

def _ai(prompt, mode, fallback=None, history=None, pdf_ctx=None):
    system = build_system_prompt(mode)
    user = build_user_prompt(prompt, mode)
    if history:
        ctx = [f"{'Student' if m['role']=='user' else 'AI'}: {m['content'][:200]}" for m in history[-6:]]
        user = "Previous context:\n" + "\n".join(ctx) + "\n\n" + user
    if pdf_ctx:
        user = f"REFERENCE DOCUMENT:\n{pdf_ctx}\n\n{user}"
    return get_response(user, system, fallback)


def _render(prompt, mode, pdf_ctx=None):
    resp, src = _ai(prompt, mode, history=st.session_state.messages, pdf_ctx=pdf_ctx)
    st.markdown(resp, unsafe_allow_html=True)
    return resp


def _msg(role, content):
    st.session_state.messages.append({
        "role": role, "content": content,
        "timestamp": datetime.now().strftime("%H:%M"),
    })


def _hr():
    st.markdown('<hr class="divider">', unsafe_allow_html=True)


def _points(n=5):
    st.session_state.points += n
    pts = st.session_state.points
    badges = st.session_state.badges
    checks = [(100, "🥈 Silver Scholar"), (300, "🥇 Gold Brain"), (600, "💎 Diamond Mind")]
    for threshold, badge in checks:
        if pts >= threshold and badge not in badges:
            badges.append(badge)
            st.toast(f"🏅 Badge unlocked: {badge}!", icon="🏅")


def _dl(data, filename, label="⬇️ Download"):
    st.download_button(label=label, data=data, file_name=filename,
                       mime="text/plain", use_container_width=True)


def _render_mermaid(code: str, height: int = 480) -> None:
    """Render a Mermaid diagram with dark glassmorphism styling."""
    code = clean_mermaid(code)
    if not code or len(code) < 10:
        return
    # Escape for safe JS string embedding (no backticks or $)
    js_safe = code.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{
    background: transparent;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: {height}px;
    padding: 12px 8px;
  }}
  #diagram-wrap {{
    width: 100%;
    background: linear-gradient(135deg, #0c1220 0%, #0a0f1e 100%);
    border: 1px solid rgba(129,140,248,0.18);
    border-radius: 16px;
    padding: 24px 16px 16px;
    position: relative;
    overflow: auto;
    min-height: {height - 40}px;
  }}
  #diagram-wrap::before {{
    content: '📊 Visual Diagram';
    position: absolute;
    top: 10px; left: 16px;
    font-size: 11px;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 1.5px;
  }}
  #diagram-wrap::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #38bdf8, #34d399);
    border-radius: 16px 16px 0 0;
  }}
  .mermaid {{
    display: flex;
    justify-content: center;
    margin-top: 8px;
  }}
  /* Mermaid node overrides for dark theme */
  .mermaid svg {{
    border-radius: 8px;
    max-width: 100%;
  }}
</style>
</head>
<body>
<div id="diagram-wrap">
  <div class="mermaid" id="chart"></div>
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: false,
    theme: 'dark',
    themeVariables: {{
      background:          '#0c1220',
      primaryColor:        '#1e3a5f',
      primaryTextColor:    '#e2e8f0',
      primaryBorderColor:  '#38bdf8',
      lineColor:           '#64748b',
      secondaryColor:      '#2d1b69',
      tertiaryColor:       '#064e3b',
      edgeLabelBackground: '#0c1220',
      clusterBkg:          '#111827',
      titleColor:          '#c7d2fe',
      fontFamily:          'Inter, sans-serif',
      fontSize:            '14px',
      nodeBorder:          '#334155',
      mainBkg:             '#1e293b',
    }},
    flowchart: {{ curve: 'basis', padding: 24, nodeSpacing: 50, rankSpacing: 60 }},
    securityLevel: 'loose',
  }});
  const code = `{js_safe}`;
  try {{
    const uid = 'mg-' + Math.random().toString(36).slice(2,9);
    const {{ svg }} = await mermaid.render(uid, code);
    document.getElementById('chart').innerHTML = svg;
  }} catch(err) {{
    document.getElementById('chart').innerHTML =
      '<div style="text-align:center;padding:2rem 1rem;">' +
      '<div style="font-size:2rem;margin-bottom:0.6rem;">⚠️</div>' +
      '<div style="font-weight:700;color:#f87171;margin-bottom:0.4rem;">Diagram render error</div>' +
      '<div style="font-size:0.82rem;color:#64748b;max-width:380px;margin:0 auto 1rem;">' +
      'The AI generated invalid Mermaid syntax. Click <b>Generate Diagram</b> again — it varies each run.</div>' +
      '<pre style="text-align:left;background:#0f172a;border:1px solid #1e293b;border-radius:8px;' +
      'padding:0.8rem;font-size:0.73rem;color:#64748b;max-height:180px;overflow:auto;">' +
      code.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;") + "</pre></div>";
  }}
</script>
</body>
</html>
"""
    st.components.v1.html(html, height=height, scrolling=True)


# ═════════════════════════════════════════════════════════════════════
#  Sidebar
# ═════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:12px 0 16px">
      <div style="font-size:38px">🎓</div>
      <div style="font-size:1.05rem;font-weight:700;
           background:linear-gradient(135deg,#38bdf8,#818cf8);
           -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent">
        AI Academic Platform
      </div>
      <div style="font-size:0.68rem;color:#475569;letter-spacing:2px;
           text-transform:uppercase;margin-top:2px">
        NVIDIA NIM · Gemini · Claude · Tavily
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Navigation
    st.markdown("#### 📍 Navigate")
    nav_idx = NAV.index(st.session_state.nav) if st.session_state.nav in NAV else 0
    new_nav = st.radio("nav", options=NAV, index=nav_idx, label_visibility="collapsed")
    if new_nav != st.session_state.nav:
        st.session_state.nav = new_nav
        st.session_state.mode = NAV_MODE.get(new_nav, "General Study Assistant")
        st.rerun()

    st.divider()

    # Rank display
    pts = st.session_state.points
    rank_label, rank_css, rank_lo, rank_hi = get_rank(pts)
    pct = min(100, int((pts - rank_lo) / max(1, rank_hi - rank_lo) * 100)) if rank_hi > rank_lo else 100

    st.markdown(f"""
    <div style="padding:0.5rem 0">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.3rem;">
        <span class="rank-badge {rank_css}">{rank_label}</span>
        <span style="font-size:0.85rem;color:#94a3b8">🏅 {pts} pts</span>
      </div>
      <div class="progress-bar"><div class="progress-fill" style="width:{pct}%"></div></div>
      <div style="font-size:0.72rem;color:#64748b;margin-top:2px">{pts - rank_lo} / {rank_hi - rank_lo} to next rank</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Pomodoro Timer (pure JS — no Python reruns)
    with st.expander("⏱️ Pomodoro Timer"):
        st.components.v1.html("""
<div id="pb" style="background:#1e293b;border:1px solid #2d3f5e;border-radius:14px;
     padding:1rem;text-align:center;margin-bottom:0.5rem;">
  <div id="pl" style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:0.3rem;">Focus</div>
  <div id="pt" style="font-size:2.2rem;font-weight:700;color:#6366f1;font-variant-numeric:tabular-nums;letter-spacing:2px;">25:00</div>
  <div style="font-size:0.78rem;color:#475569;margin-top:4px">Sessions: <span id="ps">0</span></div>
</div>
<div style="display:flex;gap:0.4rem;margin-bottom:0.4rem;">
  <button onclick="pS()" style="flex:1;background:linear-gradient(90deg,#6366f1,#38bdf8);color:#fff;border:none;border-radius:8px;padding:0.45rem;cursor:pointer;font-weight:600;">▶ Start</button>
  <button onclick="pP()" style="flex:1;background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:0.45rem;cursor:pointer;font-weight:600;">⏸ Pause</button>
  <button onclick="pR()" style="flex:1;background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:0.45rem;cursor:pointer;font-weight:600;">↺ Reset</button>
</div>
<div style="display:flex;gap:0.4rem;">
  <button onclick="pM(25,'Focus')" style="flex:1;background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:0.35rem;cursor:pointer;font-size:0.78rem;">25m</button>
  <button onclick="pM(5,'Short Break')" style="flex:1;background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:0.35rem;cursor:pointer;font-size:0.78rem;">5m</button>
  <button onclick="pM(15,'Long Break')" style="flex:1;background:#1e293b;color:#94a3b8;border:1px solid #334155;border-radius:8px;padding:0.35rem;cursor:pointer;font-size:0.78rem;">15m</button>
</div>
<script>
var _s=25*60,_r=false,_i=null,_n=0;
function _f(s){var m=Math.floor(s/60),c=s%60;return(m<10?'0':'')+m+':'+(c<10?'0':'')+c;}
function _u(){document.getElementById('pt').innerText=_f(_s);}
function _beep(){try{var c=new(window.AudioContext||window.webkitAudioContext)();var o=c.createOscillator();var g=c.createGain();o.connect(g);g.connect(c.destination);o.type='sine';o.frequency.value=880;g.gain.setValueAtTime(0.5,c.currentTime);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+0.6);o.start(c.currentTime);o.stop(c.currentTime+0.6);}catch(e){}}
function pS(){if(_r)return;_r=true;_i=setInterval(function(){if(_s>0){_s--;_u();}else{clearInterval(_i);_r=false;_n++;document.getElementById('ps').innerText=_n;_s=25*60;_u();_beep();}},1000);}
function pP(){clearInterval(_i);_r=false;}
function pR(){clearInterval(_i);_r=false;_s=25*60;_u();}
function pM(m,l){clearInterval(_i);_r=false;_s=m*60;document.getElementById('pl').innerText=l;_u();}
</script>
        """, height=210)

    st.divider()

    # Profile
    with st.expander("👤 Profile & Achievements"):
        name_val = st.text_input("Your name", value=st.session_state.user_name or "", key="sb_name")
        if name_val != (st.session_state.user_name or ""):
            st.session_state.user_name = name_val or None
        st.markdown(get_user_profile_summary())
        if st.session_state.badges:
            st.markdown("**🎖️ Badges:** " + " ".join(st.session_state.badges))
        else:
            st.caption("No badges yet. Earn 100 pts for Silver Scholar!")

    st.divider()

    # Session stats
    st.markdown("#### 📊 Session Stats")
    c1, c2 = st.columns(2)
    c1.metric("Questions", st.session_state.questions_asked)
    c2.metric("Topics", len(st.session_state.topics_studied))
    c1.metric("🔥 Streak", f"{st.session_state.streak}d")
    c2.metric("Duration", session_duration())

    ai_dot = "🟢" if ai_available() else "🔴"
    web_dot = "🟢" if tavily_available() else "🔴"
    st.caption(f"{ai_dot} AI  {web_dot} Web Search")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ═════════════════════════════════════════════════════════════════════
#  Page Router
# ═════════════════════════════════════════════════════════════════════
page = st.session_state.nav


# ─── 🏠 HOME ────────────────────────────────────────────────────────
if page == "🏠 Home":
    name_str = f" {st.session_state.user_name}," if st.session_state.user_name else ","
    pts = st.session_state.points
    rank_label, rank_css, _, _ = get_rank(pts)

    st.markdown(f"""
    <div class="animate-in" style="background:linear-gradient(135deg,#1e293b 0%,#0f2044 100%);
         border:1px solid #2d3f5e;border-radius:18px;padding:2rem 2.5rem;
         margin-bottom:1.5rem;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
      <div>
        <div style="font-size:1.8rem;font-weight:700;color:#e2e8f0;margin-bottom:0.3rem;">
          Hey{name_str} ready to study? 🎓
        </div>
        <div style="font-size:0.95rem;color:#64748b;margin-bottom:0.8rem;">
          AI-powered platform · {TOOL_COUNT} tools · Multi-provider AI + Live Web Search
        </div>
        <div style="display:flex;gap:0.8rem;flex-wrap:wrap;">
          <span style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid #10b981;
               padding:3px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">
               {"✓ AI Online" if ai_available() else "✗ AI Offline"}</span>
          <span style="background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid #38bdf8;
               padding:3px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;">
               {"✓ Web Search" if tavily_available() else "✗ No Web"}</span>
          <span class="rank-badge {rank_css}">{rank_label}</span>
        </div>
      </div>
      <div style="text-align:center;">
        <div style="font-size:3rem;font-weight:800;
             background:linear-gradient(135deg,#6366f1,#38bdf8);
             -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;">
          {pts}
        </div>
        <div style="font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Points Earned</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Dynamic quick access — show most-used tools
    st.markdown('<div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;'
                'letter-spacing:1.5px;margin-bottom:0.6rem;font-weight:600;">⚡ Quick Access</div>',
                unsafe_allow_html=True)

    quick_defaults = [
        ("💬", "AI Chat", "💬 AI Chat"),
        ("🌳", "Visual", "🌳 Visual Explainer"),
        ("🔍", "Web Search", "🔍 Web Search"),
        ("📄", "PDF Chat", "📄 PDF Study Chat"),
        ("🧩", "Quiz", "🧩 Quiz Generator"),
        ("🧮", "Math", "🧮 Math Solver"),
        ("📇", "Flashcards", "📇 Flashcard Maker"),
        ("📊", "Dashboard", "📊 Dashboard"),
    ]
    qcols = st.columns(len(quick_defaults))
    for i, (icon, label, nav_key) in enumerate(quick_defaults):
        with qcols[i]:
            if st.button(f"{icon}\n{label}", key=f"q_{nav_key}", use_container_width=True):
                st.session_state.nav = nav_key
                st.session_state.mode = NAV_MODE.get(nav_key, "General Study Assistant")
                st.rerun()

    _hr()

    # All tools grid
    st.markdown(f'<div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;'
                f'letter-spacing:1.5px;margin-bottom:1rem;font-weight:600;">🛠️ All {TOOL_COUNT} Tools</div>',
                unsafe_allow_html=True)

    categories = [
        ("📚 Study & Writing", "#10b981", [
            ("📄", "PDF Study Chat", "📄 PDF Study Chat"),
            ("📝", "Notes Summarizer", "📝 Notes Summarizer"),
            ("✍️", "Assignment Gen", "✍️ Assignment Generator"),
            ("✓", "Assignment Check", "✓ Assignment Checker"),
            ("📖", "Citation Gen", "📖 Citation Generator"),
            ("📸", "Assignment Solver", "📸 Assignment Solver"),
        ]),
        ("🎯 Exam Prep", "#f59e0b", [
            ("📅", "Study Planner", "📅 Study Planner"),
            ("🧾", "Exam Paper", "🧾 Exam Paper Generator"),
            ("🧩", "Quiz Generator", "🧩 Quiz Generator"),
            ("📇", "Flashcards", "📇 Flashcard Maker"),
            ("🎤", "Viva Prep", "🎤 Viva Prep"),
            ("📐", "Formula Sheet", "📐 Formula Sheet"),
        ]),
        ("💻 Programming", "#6366f1", [
            ("💻", "Code Runner", "💻 Code Runner"),
            ("🐛", "Code Helper", "🐛 Code Helper"),
            ("🧮", "Math Solver", "🧮 Math Solver"),
            ("🌳", "Visual Explainer", "🌳 Visual Explainer"),
        ]),
        ("🌐 AI & Research", "#38bdf8", [
            ("💬", "AI Chat", "💬 AI Chat"),
            ("🔍", "Web Search", "🔍 Web Search"),
            ("🎓", "Recommender", "🎓 Study Recommender"),
            ("🌐", "Translator", "🌐 Language Translator"),
            ("🖼️", "Image OCR", "🖼️ Image OCR"),
        ]),
        ("📊 Productivity", "#a855f7", [
            ("📊", "Dashboard", "📊 Dashboard"),
            ("📝", "Study Notepad", "📝 Study Notepad"),
        ]),
    ]

    for cat_label, cat_color, cat_tools in categories:
        st.markdown(
            f'<div class="cat-header" style="color:{cat_color};border-color:{cat_color};">'
            f'{cat_label}</div>', unsafe_allow_html=True)
        cols = st.columns(min(len(cat_tools), 6))
        for i, (icon, name, key) in enumerate(cat_tools):
            with cols[i % len(cols)]:
                if st.button(f"{icon} {name}", key=f"h_{key}", use_container_width=True):
                    st.session_state.nav = key
                    st.session_state.mode = NAV_MODE.get(key, "General Study Assistant")
                    st.rerun()


# ─── 🖼️ IMAGE OCR (improved — uses AI Vision) ───────────────────────
elif page == "🖼️ Image OCR":
    track_feature("Image OCR")
    st.markdown("### 🖼️ Image-to-Text (OCR)")
    st.info("Upload an image of handwritten notes, a diagram, or question paper. Uses AI Vision for best results.")

    uploaded = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg", "bmp", "webp"])
    if uploaded:
        st.image(uploaded, caption="Uploaded image", use_container_width=True)
        img_bytes = uploaded.getvalue()
        mime = f"image/{uploaded.type.split('/')[-1]}" if "/" in uploaded.type else "image/jpeg"

        with st.spinner("Extracting text with AI Vision…"):
            ocr_text = call_vision(img_bytes, VISION_PROMPT, mime)

        if not ocr_text:
            st.warning("AI Vision unavailable — trying local OCR…")
            try:
                from PIL import Image as PILImage
                import pytesseract, io
                img = PILImage.open(io.BytesIO(img_bytes))
                ocr_text = pytesseract.image_to_string(img).strip()
            except Exception as e:
                st.error(f"OCR failed: {e}")

        if ocr_text:
            st.success("✅ Text extracted!")
            st.text_area("Extracted Text", ocr_text, height=200)
            _dl(ocr_text, "ocr_text.txt", "⬇️ Download Text")
            _points(5)

            # Follow-up: Ask AI about this text
            _hr()
            st.markdown("#### 💬 Ask AI about this text")
            follow_up = st.text_input("Ask a question about the extracted text…",
                                       placeholder="Summarise this / Explain / Answer these questions")
            if st.button("🤖 Ask AI", type="primary") and follow_up.strip():
                prompt = f"Extracted text from image:\n{ocr_text}\n\nUser question: {follow_up}"
                with st.spinner("Thinking…"):
                    resp, src = _ai(prompt, "General Study Assistant")
                st.markdown(f'<div class="card card-blue">{resp}</div>', unsafe_allow_html=True)
                _points(5)
    else:
        st.caption("Upload an image to begin.")


# ─── 📄 PDF STUDY CHAT (improved — shows stats) ─────────────────────
elif page == "📄 PDF Study Chat":
    track_feature("PDF Study Chat")
    st.markdown("### 📄 PDF Study Chat")

    uploaded = st.file_uploader("Upload a PDF", type=["pdf"])
    if uploaded:
        if uploaded.name != st.session_state.pdf_filename:
            with st.spinner("📖 Reading PDF…"):
                text, err = extract_pdf_text(uploaded)
            if err:
                st.error(err)
            else:
                st.session_state.pdf_content = text
                st.session_state.pdf_filename = uploaded.name
                st.session_state.pdf_chat_history = []
                stats = pdf_stats(text)
                st.success(f"✅ Loaded: **{uploaded.name}** — {stats['pages']} pages, ~{stats['words']:,} words")

    if st.session_state.pdf_content:
        st.caption(f"📎 Active: {st.session_state.pdf_filename}")
        _pdf_stats = pdf_stats(st.session_state.pdf_content)
        c1, c2, c3 = st.columns(3)
        c1.metric("Pages", _pdf_stats["pages"])
        c2.metric("Words", f"{_pdf_stats['words']:,}")
        c3.metric("Characters", f"{_pdf_stats['chars']:,}")

        _hr()

        # Quick actions
        qa1, qa2 = st.columns(2)
        if qa1.button("📝 Summarise Entire PDF", use_container_width=True):
            with st.spinner("Summarising…"):
                resp, src = _ai(
                    f"Summarise the key points of this document:\n\n{st.session_state.pdf_content[:6000]}",
                    "Notes Summarizer"
                )
            st.markdown(f'<div class="card card-green">{resp}</div>', unsafe_allow_html=True)
            _points(10)

        if qa2.button("🧩 Generate Quiz from PDF", use_container_width=True):
            with st.spinner("Generating quiz…"):
                resp, src = _ai(
                    f"Create 5 MCQs based on this document:\n\n{st.session_state.pdf_content[:6000]}",
                    "Quiz Generator"
                )
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(10)

        _hr()

        # Chat interface
        for msg in st.session_state.pdf_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input("Ask a question about the PDF…")
        if question:
            with st.chat_message("user"):
                st.markdown(question)
            st.session_state.pdf_chat_history.append({"role": "user", "content": question})

            ctx = find_relevant_pdf_content(st.session_state.pdf_content, question)
            with st.chat_message("assistant"):
                answer = _render(question, "General Study Assistant", pdf_ctx=ctx)
            st.session_state.pdf_chat_history.append({"role": "assistant", "content": answer})
            update_study_tracking(question)
            _points(5)

        if st.button("🗑️ Clear PDF", use_container_width=True):
            st.session_state.pdf_content = None
            st.session_state.pdf_filename = None
            st.session_state.pdf_chat_history = []
            st.rerun()
    elif not uploaded:
        st.info("👆 Upload a PDF to start studying.")


# ─── 📝 NOTES SUMMARIZER ────────────────────────────────────────────
elif page == "📝 Notes Summarizer":
    track_feature("Notes Summarizer")
    st.markdown("### 📝 Notes Summarizer")

    # Pull from PDF if available
    source_tab = st.radio("Source", ["✏️ Paste Notes", "📄 From Uploaded PDF"],
                          horizontal=True, label_visibility="collapsed")

    if source_tab == "📄 From Uploaded PDF" and st.session_state.pdf_content:
        notes = st.session_state.pdf_content[:8000]
        st.success(f"Using content from: {st.session_state.pdf_filename}")
    elif source_tab == "📄 From Uploaded PDF":
        st.warning("No PDF uploaded. Go to PDF Study Chat first, or paste notes below.")
        notes = ""
    else:
        notes = st.text_area("Paste your notes", height=260,
                             placeholder="Paste lecture notes, textbook passages, or any text…")

    word_count = len(notes.split()) if notes.strip() else 0
    st.caption(f"Input words: {word_count}")

    c1, c2 = st.columns(2)
    length = c1.select_slider("Summary length", ["Very Short", "Short", "Medium", "Detailed"], value="Medium")
    fmt = c2.selectbox("Format", ["Bullet Points", "Paragraph", "Key Terms Only", "Q&A Format"])
    length_map = {"Very Short": "3 sentences", "Short": "5 sentences",
                  "Medium": "8-10 sentences", "Detailed": "15+ sentences"}

    if st.button("✨ Summarize", type="primary"):
        if not notes.strip():
            st.warning("Please paste some notes to summarize.")
        else:
            prompt = NOTES_SUMMARY.format(length=length_map[length], format=fmt, notes=notes)
            update_study_tracking(notes[:200])
            with st.spinner("Summarising…"):
                resp, src = _ai(prompt, "Notes Summarizer", fallback="Summary unavailable.")
            st.markdown(f'<div class="card card-green">{resp}</div>', unsafe_allow_html=True)
            summary_words = len(resp.split())
            st.caption(f"Summary: {summary_words} words (compressed {round((1 - summary_words/max(1,word_count))*100)}%)")
            _points(5)
            _dl(resp, "summary.txt", "⬇️ Download Summary")
            _msg("user", notes[:200] + "…")
            _msg("assistant", resp)


# ─── ✍️ ASSIGNMENT GENERATOR ────────────────────────────────────────
elif page == "✍️ Assignment Generator":
    track_feature("Assignment Generator")
    st.markdown("### ✍️ Assignment Generator")

    c1, c2 = st.columns(2)
    topic = c1.text_input("Assignment topic", placeholder="e.g. Cloud Computing and its Applications")
    words = c1.number_input("Target word count", 500, 5000, 1000, step=250)
    style = c2.selectbox("Style", ["Academic Essay", "Technical Report", "Case Study", "Lab Report", "Research Paper"])
    audience = c2.selectbox("Academic Level", ["Undergraduate", "Postgraduate", "High School"])
    rephrase = c2.checkbox("🔄 Rephrase for originality", value=True)

    if st.button("📄 Generate Assignment", type="primary"):
        if not topic.strip():
            st.warning("Please enter an assignment topic.")
        else:
            prompt = ASSIGNMENT_GEN.format(style=style, topic=topic, audience=audience, words=words)
            if rephrase:
                prompt += ("\n\nIMPORTANT: Use varied vocabulary, unique sentence structures, "
                          "and avoid common AI-generated patterns. Write naturally.")
            update_study_tracking(topic)
            with st.spinner("Writing assignment…"):
                resp, src = _ai(prompt, "Assignment Writer",
                                fallback=f"Assignment generation unavailable. Topic: {topic}")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(10)
            _dl(resp, f"assignment_{topic[:25].replace(' ','_')}.txt", "⬇️ Download Assignment")
            _msg("user", prompt[:200])
            _msg("assistant", resp)


# ─── ✓ ASSIGNMENT CHECKER (improved — parsed scores) ────────────────
elif page == "✓ Assignment Checker":
    track_feature("Assignment Checker")
    st.markdown("### ✓ Assignment Checker")
    st.info("Paste your assignment to get AI feedback with scores on each criterion.")

    text = st.text_area("Paste your assignment", height=300,
                        placeholder="Paste the full text of your assignment here…")

    if st.button("🔍 Check Assignment", type="primary"):
        if not text.strip():
            st.warning("Please paste your assignment.")
        else:
            # Basic stats
            words = text.split()
            sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Words", len(words))
            c2.metric("Sentences", len(sentences))
            c3.metric("Avg Sent", f"{round(len(words)/max(1,len(sentences)),1)} words")
            c4.metric("Paragraphs", len([p for p in text.split("\n\n") if p.strip()]))

            _hr()
            # Send up to 5000 chars for better coverage
            prompt = ASSIGNMENT_CHECK.format(text=text[:5000])
            with st.spinner("Analysing…"):
                resp, src = _ai(prompt, "General Study Assistant",
                                fallback="AI feedback unavailable.")

            # Try to parse scores from response
            score_map = {}
            for line in resp.split("\n"):
                for key in ["Grammar", "Clarity", "Structure", "Argument", "Tone"]:
                    m = re.search(rf'{key}:\s*(\d+)', line, re.IGNORECASE)
                    if m:
                        score_map[key] = int(m.group(1))
                grade_m = re.search(r'Overall Grade:\s*([A-D])', line, re.IGNORECASE)
                if grade_m:
                    score_map["Grade"] = grade_m.group(1)

            if score_map:
                # Visual score display
                cols = st.columns(len([k for k in score_map if k != "Grade"]) + 1)
                i = 0
                for key in ["Grammar", "Clarity", "Structure", "Argument", "Tone"]:
                    if key in score_map:
                        val = score_map[key]
                        color = "#10b981" if val >= 7 else "#f59e0b" if val >= 5 else "#ef4444"
                        with cols[i]:
                            st.markdown(
                                f'<div class="kpi"><h3 style="color:{color}">{val}/10</h3>'
                                f'<p>{key}</p></div>', unsafe_allow_html=True)
                        i += 1
                if "Grade" in score_map:
                    g = score_map["Grade"]
                    css = {"A": "score-a", "B": "score-b", "C": "score-c"}.get(g, "score-d")
                    with cols[i]:
                        st.markdown(
                            f'<div class="kpi"><h3><span class="score-pill {css}">{g}</span></h3>'
                            f'<p>Grade</p></div>', unsafe_allow_html=True)

            _hr()
            st.markdown(f'<div class="card card-blue">{resp}</div>', unsafe_allow_html=True)
            _points(5)
            _dl(resp, f"feedback_{datetime.now().strftime('%Y%m%d_%H%M')}.txt", "⬇️ Download Feedback")


# ─── 📅 STUDY PLANNER (improved — priority weighting) ───────────────
elif page == "📅 Study Planner":
    track_feature("Study Planner")
    st.markdown("### 📅 Study Planner")

    c1, c2 = st.columns(2)
    exam_date = c1.date_input("Exam date", value=date.today().replace(month=min(date.today().month + 1, 12)))
    hours_day = c1.slider("Hours per day", 1.0, 10.0, 4.0, 0.5)
    subjects_raw = c2.text_area("Subjects (one per line)", height=140,
                                placeholder="Python Programming\nDBMS\nOperating Systems")
    st.caption("💡 Mark priority: add `(weak)` or `(strong)` after subject name. Default is Average.")
    ai_tips = c2.checkbox("✨ Add AI study tips", value=True)

    if st.button("📅 Generate Plan", type="primary"):
        # Parse subjects with priority
        subjects = []
        for line in subjects_raw.splitlines():
            line = line.strip()
            if not line:
                continue
            priority = "Average"
            if "(weak)" in line.lower():
                priority = "Weak"
                line = re.sub(r'\(weak\)', '', line, flags=re.IGNORECASE).strip()
            elif "(strong)" in line.lower():
                priority = "Strong"
                line = re.sub(r'\(strong\)', '', line, flags=re.IGNORECASE).strip()
            subjects.append({"name": line, "priority": priority})

        if not subjects:
            st.warning("Enter at least one subject.")
        elif exam_date <= date.today():
            st.warning("Exam date must be in the future.")
        else:
            plan = build_study_plan(subjects, exam_date, hours_day)
            days = (exam_date - date.today()).days
            st.success(f"📅 {days}-day plan · {len(subjects)} subjects · {hours_day}h/day · {round(days*hours_day)}h total")

            plan_text = f"Study Plan — Exam: {exam_date}\n\n"
            for entry in plan[:60]:
                color = "card-red" if entry["is_revision"] else "card-green"
                st.markdown(
                    f'<div class="card {color}" style="padding:0.6rem 1.2rem;margin-bottom:0.4rem;">'
                    f'<b>{entry["date"]}</b>  —  {entry["subject"]}  '
                    f'<span style="color:#64748b">({entry["hours"]}h)</span><br>'
                    f'<span style="font-size:0.82rem;color:#94a3b8">{entry["note"]}</span>'
                    f'</div>', unsafe_allow_html=True)
                plan_text += f"{entry['date']} — {entry['subject']} ({entry['hours']}h)\n{entry['note']}\n\n"

            _points(10)
            _dl(plan_text, "study_plan.txt", "⬇️ Download Study Plan")

            if ai_tips:
                _hr()
                st.markdown("### ✨ AI Study Tips")
                subj_names = ", ".join(s["name"] for s in subjects)
                prompt = STUDY_TIPS.format(days=days, subjects=subj_names, hours=hours_day)
                with st.spinner("Getting AI tips…"):
                    resp, src = _ai(prompt, "Study Planner",
                                    fallback="Focus on weak areas first, practice past papers in the final 3 days.")
                st.markdown(f'<div class="card card-purple">{resp}</div>', unsafe_allow_html=True)


# ─── 🧾 EXAM PAPER GENERATOR ────────────────────────────────────────
elif page == "🧾 Exam Paper Generator":
    track_feature("Exam Paper Generator")
    st.markdown("### 🧾 Exam Paper Generator")

    c1, c2 = st.columns(2)
    subject = c1.text_input("Subject", placeholder="DBMS, Python, Computer Networks…")
    difficulty = c1.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
    duration = c2.selectbox("Duration", ["1 Hour", "2 Hours", "3 Hours"])
    marks = c2.selectbox("Total Marks", ["40", "50", "75", "100"])
    include_ans = c2.checkbox("Include Answer Key")

    if st.button("📋 Generate Exam Paper", type="primary"):
        if not subject.strip():
            st.warning("Please enter a subject.")
        else:
            ans_note = "\n\nAlso provide a complete answer key at the end." if include_ans else ""
            prompt = EXAM_PAPER.format(
                subject=subject, marks=marks, duration=duration,
                difficulty=difficulty, answer_key=ans_note
            )
            update_study_tracking(subject)
            with st.spinner("Generating exam paper…"):
                resp, src = _ai(prompt, "Exam Prep",
                                fallback=f"Exam paper generation unavailable. Subject: {subject}")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(10)
            _dl(resp, f"exam_{subject[:20].replace(' ','_')}.txt", "⬇️ Download Exam Paper")


# ─── 💻 CODE RUNNER (improved — AI explain error) ────────────────────
elif page == "💻 Code Runner":
    track_feature("Code Runner")
    st.markdown("### 💻 Python Code Runner")
    st.warning("⚠️ Runs Python only. Dangerous imports are blocked for security.")

    snippets = {
        "— blank —":          "# Write your Python code here\nprint('Hello, World!')",
        "Hello World":        "print('Hello, World!')\nprint(2 ** 10)",
        "Fibonacci":          "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        print(a, end=' ')\n        a, b = b, a+b\nfib(12)",
        "List Comprehension": "squares = [x**2 for x in range(1, 11)]\nprint('Squares:', squares)",
        "Sorting":            "def bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\nprint(bubble_sort([64,34,25,12,22,11,90]))",
        "Class Example":      "class Student:\n    def __init__(self, name, grade):\n        self.name = name\n        self.grade = grade\n    def __repr__(self):\n        return f'Student({self.name}, grade={self.grade})'\n\ns = Student('Alice', 'A')\nprint(s)",
    }
    starter = st.selectbox("Load starter snippet", list(snippets.keys()))
    code = st.text_area("Python code", value=snippets[starter], height=300)
    timeout = st.slider("Timeout (seconds)", 3, 15, 8)

    if st.button("▶️ Run Code", type="primary"):
        if not code.strip():
            st.warning("Please enter some Python code.")
        else:
            with st.spinner("Executing…"):
                stdout, stderr = execute_python(code, timeout)
            if stdout:
                st.success("✅ Output")
                st.code(stdout, language="text")
            if stderr:
                if "Blocked" in stderr or "timed out" in stderr:
                    st.warning(stderr)
                else:
                    st.error("❌ Error")
                    st.code(stderr, language="text")

                    # AI Explain Error button
                    if st.button("🤖 AI Explain This Error", key="explain_err"):
                        prompt = f"This Python code:\n```python\n{code}\n```\nProduced this error:\n{stderr}\n\nExplain the error simply and show how to fix it."
                        with st.spinner("Analysing error…"):
                            resp, src = _ai(prompt, "Code Debugger")
                        st.markdown(f'<div class="card card-blue">{resp}</div>', unsafe_allow_html=True)

            if not stdout and not stderr:
                st.info("Code ran with no output.")
            _points(5)


# ─── 🎓 STUDY RECOMMENDER ───────────────────────────────────────────
elif page == "🎓 Study Recommender":
    track_feature("Study Recommender")
    st.markdown("### 🎓 Personalised Study Recommender")

    # AI recommendations by default
    extra = st.text_input("Focus area", placeholder="e.g. Data Structures, Machine Learning")
    studied = st.session_state.topics_studied

    if st.button("🎓 Get AI Recommendations", type="primary"):
        prompt = STUDY_RECOMMEND.format(
            studied=", ".join(studied) if studied else "None yet",
            focus=extra or "General CS"
        )
        with st.spinner("Building learning path…"):
            resp, src = _ai(prompt, "General Study Assistant", fallback=get_recommendations())
        st.markdown(f'<div class="card card-purple">{resp}</div>', unsafe_allow_html=True)
        _points(5)
        _dl(resp, "learning_path.txt", "⬇️ Download Learning Path")

    _hr()
    st.markdown("#### 📚 Quick Resource Links")
    st.markdown(f'<div class="card">{get_recommendations()}</div>', unsafe_allow_html=True)


# ─── 📝 STUDY NOTEPAD (replaces broken Study Room) ──────────────────
elif page == "📝 Study Notepad":
    st.markdown("### 📝 Study Notepad")
    st.info("Your personal study notepad — take notes, bookmark important questions, and keep a review list.")

    tab1, tab2 = st.tabs(["📝 Notes", "🔖 Bookmarks"])

    with tab1:
        notes = st.text_area("Your Notes", value=st.session_state.notepad_notes,
                             height=300, placeholder="Type your study notes here…")
        if notes != st.session_state.notepad_notes:
            st.session_state.notepad_notes = notes

        c1, c2 = st.columns(2)
        if c1.button("💾 Save Notes", use_container_width=True):
            st.session_state.notepad_notes = notes
            st.toast("Notes saved!", icon="✅")
        if c2.button("📝 Summarise with AI", use_container_width=True) and notes.strip():
            with st.spinner("Summarising…"):
                resp, src = _ai(f"Summarise these study notes concisely:\n\n{notes[:3000]}", "Notes Summarizer")
            st.markdown(f'<div class="card card-green">{resp}</div>', unsafe_allow_html=True)
        if notes.strip():
            _dl(notes, "study_notes.txt", "⬇️ Download Notes")

    with tab2:
        bm = st.session_state.notepad_bookmarks
        new_bm = st.text_input("Add a bookmark / review item", placeholder="e.g. Review OSI model layers")
        if st.button("🔖 Add") and new_bm.strip():
            bm.append({"text": new_bm.strip(), "added": datetime.now().strftime("%d %b %H:%M")})
            st.rerun()
        if bm:
            for i, item in enumerate(bm):
                st.markdown(
                    f'<div class="card" style="padding:0.5rem 1rem;margin-bottom:0.3rem;">'
                    f'<b>🔖</b> {item["text"]} '
                    f'<span style="color:#64748b;font-size:0.78rem">({item["added"]})</span></div>',
                    unsafe_allow_html=True)
            if st.button("🗑️ Clear All Bookmarks"):
                st.session_state.notepad_bookmarks = []
                st.rerun()
        else:
            st.caption("No bookmarks yet. Add review items above!")


# ─── 📊 DASHBOARD ───────────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.markdown("### 📊 Study Dashboard")

    total_actions = sum(st.session_state.feature_usage.values())
    pts = st.session_state.points
    rank_label, rank_css, _, _ = get_rank(pts)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi"><h3>{st.session_state.questions_asked}</h3><p>Questions</p></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi"><h3>{len(st.session_state.topics_studied)}</h3><p>Topics</p></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi"><h3>{session_duration()}</h3><p>Duration</p></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="kpi"><h3>{pts}</h3><p>Points</p></div>',
                    unsafe_allow_html=True)

    _hr()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 📈 Tool Usage")
        feat_data = {f: v for f, v in get_most_used() if v > 0}
        if feat_data:
            try:
                import pandas as pd
                df = pd.DataFrame({"Tool": list(feat_data.keys()), "Uses": list(feat_data.values())})
                df = df.sort_values("Uses", ascending=False)
                st.bar_chart(df.set_index("Tool"), use_container_width=True, height=280)
            except ImportError:
                for feat, count in sorted(feat_data.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f'<div class="card" style="padding:0.5rem 1rem;margin-bottom:0.3rem;"><b>{feat}</b>: {count}</div>',
                                unsafe_allow_html=True)
        else:
            st.info("Use tools to see your usage chart.")

    with c2:
        st.markdown("#### 📚 Topics Studied")
        topics = st.session_state.topics_studied
        if topics:
            for t in topics[-15:]:
                st.markdown(f'<div class="card" style="padding:0.45rem 1rem;margin-bottom:0.3rem;">• {t}</div>',
                            unsafe_allow_html=True)
        else:
            st.caption("No topics tracked yet — start chatting!")

    _hr()
    st.markdown("#### 🎯 Session Goals")
    goals = [
        ("Questions", st.session_state.questions_asked, 10, "💬"),
        ("Topics", len(st.session_state.topics_studied), 5, "📚"),
        ("Points", pts, 50, "🏅"),
        ("Tools Used", total_actions, 10, "🛠️"),
    ]
    gcols = st.columns(4)
    for i, (label, current, target, icon) in enumerate(goals):
        p = min(100, int(current / max(1, target) * 100))
        with gcols[i]:
            st.markdown(
                f'<div class="card" style="text-align:center;padding:0.9rem;">'
                f'<div style="font-size:1.6rem">{icon}</div>'
                f'<div style="font-weight:700;font-size:1.1rem;color:#e2e8f0;">{current}/{target}</div>'
                f'<div style="font-size:0.78rem;color:#64748b;margin-bottom:0.4rem">{label}</div>'
                f'<div class="progress-bar"><div class="progress-fill" style="width:{p}%"></div></div>'
                f'</div>', unsafe_allow_html=True)

    if st.button("🔄 Reset Stats"):
        for k in ["questions_asked", "topics_studied", "messages"]:
            st.session_state[k] = 0 if k == "questions_asked" else []
        st.session_state.feature_usage = {k: 0 for k in st.session_state.feature_usage}
        st.rerun()


# ─── 💬 AI CHAT (with auto visual diagrams) ─────────────────────────
elif page == "💬 AI Chat":
    track_feature("AI Chat")

    # Header row with auto-diagram toggle
    h1, h2 = st.columns([5, 2])
    h1.markdown("### 💬 AI Chat")
    h1.caption("Ask anything — multi-provider AI cascade · auto visual diagrams")
    auto_diag = h2.toggle("🌳 Auto Diagram", value=st.session_state.diagram_auto,
                           help="Auto-generate a colourful diagram for visual topics")
    if auto_diag != st.session_state.diagram_auto:
        st.session_state.diagram_auto = auto_diag

    # Suggested prompts for new users
    if not st.session_state.messages:
        st.markdown("#### 💡 Try asking:")
        suggests = [
            "Explain Binary Search Tree",
            "How does BFS work?",
            "Explain OOP inheritance",
            "OSI model layers",
            "Quick sort algorithm",
            "TCP/IP handshake",
            "What is normalization in DBMS?",
            "Explain Dijkstra algorithm",
            "Stack vs Queue",
        ]
        scols = st.columns(3)
        for i, s in enumerate(suggests):
            with scols[i % 3]:
                if st.button(s, key=f"sug_{i}", use_container_width=True):
                    st.session_state["_pending_prompt"] = s
                    st.rerun()

    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Show last diagram (persists across reruns)
    if st.session_state.last_diagram:
        _render_mermaid(st.session_state.last_diagram, height=500)
        st.caption(f"📊 Diagram: *{st.session_state.last_diagram_topic}*")
        if st.button("✕ Clear Diagram", key="clear_diag"):
            st.session_state.last_diagram = None
            st.session_state.last_diagram_topic = ""
            st.rerun()

    prompt = st.chat_input("Ask anything… e.g. 'Explain binary search tree'")
    # Pending prompt from suggested buttons
    if not prompt and st.session_state.get("_pending_prompt"):
        prompt = st.session_state.pop("_pending_prompt")

    if prompt:
        detect_user_info(prompt)
        update_study_tracking(prompt)
        with st.chat_message("user"):
            st.markdown(prompt)
        _msg("user", prompt)

        with st.chat_message("assistant"):
            answer = _render(prompt, st.session_state.mode)
        _msg("assistant", answer)
        _points(5)

        # ── Auto diagram generation ──────────────────────────────────
        if st.session_state.diagram_auto and should_visualize(prompt + " " + answer):
            concept = prompt[:300]
            diag_prompt = DIAGRAM_GEN.format(concept=concept)
            with st.spinner("🎨 Generating visual diagram…"):
                raw_diag, _ = _ai(diag_prompt, "General Study Assistant")
            code = clean_mermaid(raw_diag)
            if code and len(code) > 20:
                st.session_state.last_diagram = code
                st.session_state.last_diagram_topic = prompt[:80]
                st.rerun()   # rerun so diagram renders in correct position


# ─── 🧩 QUIZ GENERATOR (improved — interactive mode) ────────────────
elif page == "🧩 Quiz Generator":
    track_feature("Quiz Generator")
    st.markdown("### 🧩 Quiz Generator")

    tab_gen, tab_take = st.tabs(["✨ Generate Quiz", "📝 Take Quiz"])

    with tab_gen:
        c1, c2, c3 = st.columns(3)
        topic = c1.text_input("Quiz topic", placeholder="DBMS, Python OOP, OSI Model…")
        num_q = c2.slider("Questions", 3, 15, 5)
        level = c3.select_slider("Difficulty", ["Easy", "Mixed", "Hard"], value="Mixed")

        if st.button("🧩 Generate Quiz", type="primary"):
            if not topic.strip():
                st.warning("Please enter a quiz topic.")
            else:
                prompt = QUIZ_GEN.format(level=level.lower(), topic=topic, num=num_q)
                update_study_tracking(topic)
                with st.spinner("Generating quiz…"):
                    resp, src = _ai(prompt, "Quiz Generator",
                                    fallback=f"Quiz generation unavailable. Topic: {topic}")

                # Parse into interactive quiz
                parsed = parse_quiz(resp)
                if parsed:
                    st.session_state.quiz_data = parsed
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.success(f"✅ {len(parsed)} questions generated! Go to **Take Quiz** tab.")
                    _points(10)
                else:
                    # Fallback: show raw
                    st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
                    _points(10)
                _dl(resp, f"quiz_{topic[:20].replace(' ','_')}.txt", "⬇️ Download Quiz")

    with tab_take:
        qdata = st.session_state.quiz_data
        if not qdata:
            st.info("Generate a quiz first in the Generate tab.")
        else:
            submitted = st.session_state.quiz_submitted
            answers = st.session_state.quiz_answers

            for i, q in enumerate(qdata):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                opts = list(q["options"].items())
                selected = st.radio(
                    f"q_{i}", [f"{k}) {v}" for k, v in opts],
                    key=f"quiz_q_{i}", label_visibility="collapsed",
                    disabled=submitted,
                )
                if selected:
                    answers[i] = selected[0]  # Just the letter

                if submitted:
                    correct = q["correct"]
                    user_ans = answers.get(i, "")
                    if user_ans == correct:
                        st.markdown(f'<div class="quiz-correct" style="padding:0.5rem 1rem;border-radius:8px;">✅ Correct!</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(
                            f'<div class="quiz-wrong" style="padding:0.5rem 1rem;border-radius:8px;">'
                            f'❌ Wrong — Correct: {correct}) {q["options"].get(correct, "")}</div>',
                            unsafe_allow_html=True)
                    if q.get("explanation"):
                        st.caption(f"💡 {q['explanation']}")
                st.markdown("---")

            if not submitted:
                if st.button("✅ Submit Quiz", type="primary"):
                    st.session_state.quiz_submitted = True
                    # Calculate score
                    correct_count = sum(1 for i, q in enumerate(qdata) if answers.get(i) == q["correct"])
                    total = len(qdata)
                    pct = round(correct_count / total * 100)
                    _points(correct_count * 5)
                    st.rerun()
            else:
                correct_count = sum(1 for i, q in enumerate(qdata) if answers.get(i) == q["correct"])
                total = len(qdata)
                pct = round(correct_count / total * 100)
                color = "#10b981" if pct >= 70 else "#f59e0b" if pct >= 50 else "#ef4444"
                st.markdown(
                    f'<div class="card" style="text-align:center;padding:1.5rem;">'
                    f'<div style="font-size:2.5rem;font-weight:800;color:{color};">{pct}%</div>'
                    f'<div style="font-size:1.1rem;color:#e2e8f0;">{correct_count}/{total} Correct</div>'
                    f'</div>', unsafe_allow_html=True)

                if st.button("🔄 New Quiz"):
                    st.session_state.quiz_data = None
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()


# ─── 🐛 CODE HELPER ─────────────────────────────────────────────────
elif page == "🐛 Code Helper":
    track_feature("Code Helper")
    st.markdown("### 🐛 Code Helper")

    tabs = st.tabs(["🔍 Debug", "📖 Explain", "⚡ Optimise", "✍️ Write", "🔄 Convert"])

    with tabs[0]:
        code = st.text_area("Paste code", height=250, key="dbg_code", placeholder="# Paste code…")
        err = st.text_input("Error message (optional)", key="dbg_err")
        if st.button("🔍 Analyse", key="dbg_btn", type="primary") and code.strip():
            prompt = CODE_DEBUG.format(code=code, error_note=f"\nError: {err}" if err else "")
            with st.spinner("Analysing…"):
                resp, _ = _ai(prompt, "Code Debugger", fallback="AI unavailable.")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(5)

    with tabs[1]:
        code = st.text_area("Paste code", height=250, key="exp_code")
        if st.button("📖 Explain", key="exp_btn", type="primary") and code.strip():
            prompt = CODE_EXPLAIN.format(code=code)
            with st.spinner("Explaining…"):
                resp, _ = _ai(prompt, "Programming Helper")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(5)

    with tabs[2]:
        code = st.text_area("Paste code", height=250, key="opt_code")
        if st.button("⚡ Optimise", key="opt_btn", type="primary") and code.strip():
            prompt = CODE_OPTIMISE.format(code=code)
            with st.spinner("Optimising…"):
                resp, _ = _ai(prompt, "Code Debugger")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(5)

    with tabs[3]:
        desc = st.text_area("Describe what the code should do", height=120, key="wrt_desc")
        lang = st.selectbox("Language", ["Python", "Java", "C++", "C", "JavaScript", "SQL", "Go"], key="wrt_lang")
        if st.button("✍️ Generate", key="wrt_btn", type="primary") and desc.strip():
            prompt = CODE_WRITE.format(lang=lang, desc=desc)
            with st.spinner("Writing…"):
                resp, _ = _ai(prompt, "Programming Helper")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(5)

    with tabs[4]:
        code = st.text_area("Paste code", height=220, key="cvt_code")
        c1, c2 = st.columns(2)
        # Auto-detect source language
        detected = detect_language(code) if code.strip() else "python"
        lang_list = ["Python", "Java", "C++", "C", "JavaScript", "Go"]
        det_idx = next((i for i, l in enumerate(lang_list) if l.lower() == detected), 0)
        from_l = c1.selectbox("From", lang_list, index=det_idx, key="from_l")
        to_l = c2.selectbox("To", lang_list, key="to_l")
        if st.button("🔄 Convert", key="cvt_btn", type="primary") and code.strip():
            prompt = CODE_CONVERT.format(from_lang=from_l, to_lang=to_l,
                                          from_lang_lower=from_l.lower(), code=code)
            with st.spinner("Converting…"):
                resp, _ = _ai(prompt, "Programming Helper")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(5)


# ─── 🧮 MATH SOLVER (improved — plotly graphing) ────────────────────
elif page == "🧮 Math Solver":
    track_feature("Math Solver")
    st.markdown("### 🧮 Math Problem Solver")

    c1, c2 = st.columns([3, 1])
    problem = c1.text_area("Math Problem", height=120,
                           placeholder="e.g. Solve x² - 5x + 6 = 0\nor: Find the derivative of f(x) = 3x³ + 2x² - x + 5")
    subject = c2.selectbox("Topic", ["Auto-Detect", "Algebra", "Calculus", "Statistics",
                                      "Discrete Math", "Linear Algebra", "Probability", "Trigonometry"])
    show_steps = c2.checkbox("Show all steps", value=True)

    if st.button("🧮 Solve", type="primary"):
        if not problem.strip():
            st.warning("Please enter a math problem.")
        else:
            topic_note = f" ({subject})" if subject != "Auto-Detect" else ""
            step_inst = ("Provide a detailed step-by-step solution, explaining each step clearly."
                        if show_steps else "Provide a concise solution.")
            prompt = MATH_SOLVE.format(
                topic_note=topic_note, problem=problem,
                step_instruction=step_inst, graph_instruction=""
            )
            update_study_tracking(f"Math: {problem[:30]}")
            with st.spinner("Solving…"):
                resp, src = _ai(prompt, "General Study Assistant",
                                fallback="Math solver unavailable.")
            st.markdown(f'<div class="card card-blue">{resp}</div>', unsafe_allow_html=True)
            _points(5)
            _dl(resp, "math_solution.txt", "⬇️ Download Solution")

    _hr()
    st.markdown("#### 📐 Quick Reference")
    ref_tabs = st.tabs(["Algebra", "Calculus", "Statistics", "Discrete Math"])
    with ref_tabs[0]:
        st.markdown("**Quadratic:** x = (-b ± √(b²-4ac)) / 2a  \n"
                    "**Exponents:** aⁿ·aᵐ = aⁿ⁺ᵐ  \n"
                    "**Logs:** log(ab) = log(a)+log(b)")
    with ref_tabs[1]:
        st.markdown("**Power Rule:** d/dx[xⁿ] = n·xⁿ⁻¹  \n"
                    "**Chain Rule:** d/dx[f(g(x))] = f'(g(x))·g'(x)  \n"
                    "**Integration:** ∫xⁿ dx = xⁿ⁺¹/(n+1) + C")
    with ref_tabs[2]:
        st.markdown("**Mean:** μ = Σx / n  \n"
                    "**Variance:** σ² = Σ(x-μ)² / n  \n"
                    "**Bayes:** P(A|B) = P(B|A)·P(A) / P(B)")
    with ref_tabs[3]:
        st.markdown("**Combinations:** C(n,r) = n! / (r!(n-r)!)  \n"
                    "**Sum:** Σk = n(n+1)/2  \n"
                    "**Big-O:** O(1) < O(log n) < O(n) < O(n²) < O(2ⁿ)")


# ─── 📇 FLASHCARD MAKER (improved — shuffle + know/learning) ────────
elif page == "📇 Flashcard Maker":
    track_feature("Flashcard Maker")
    st.markdown("### 📇 Flashcard Maker")

    tab1, tab2 = st.tabs(["✨ Generate", "📋 Study Mode"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        topic = c1.text_area("Topic or Notes", height=160,
                             placeholder="e.g. 'OS concepts' or paste notes…")
        num = c2.slider("Cards", 5, 20, 10)
        ctype = c2.selectbox("Type", ["Definition", "Q&A", "Fill in the Blank", "Mixed"])

        if st.button("📇 Generate Flashcards", type="primary"):
            if not topic.strip():
                st.warning("Enter a topic or paste notes.")
            else:
                prompt = FLASHCARD_GEN.format(num=num, topic=topic[:200], card_type=ctype)
                update_study_tracking(topic[:40])
                with st.spinner("Creating flashcards…"):
                    resp, _ = _ai(prompt, "General Study Assistant", fallback="Unavailable.")
                cards = parse_flashcards(resp)
                if cards:
                    st.session_state.flashcards = cards
                    st.success(f"✅ {len(cards)} flashcards created! Go to Study Mode.")
                    _points(10)
                    cols = st.columns(2)
                    for i, card in enumerate(cards):
                        with cols[i % 2]:
                            st.markdown(
                                f'<div class="flashcard">'
                                f'<div class="flashcard-q">❓ {card["q"]}</div>'
                                f'<div class="flashcard-a">💡 {card["a"]}</div>'
                                f'</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)

    with tab2:
        cards = st.session_state.flashcards
        if not cards:
            st.info("Generate flashcards first.")
        else:
            # Controls
            c1, c2 = st.columns([1, 1])
            if c1.button("🔀 Shuffle"):
                random.shuffle(st.session_state.flashcards)
                st.session_state["card_idx"] = 0
                st.session_state["show_ans"] = False
                st.rerun()

            if "card_idx" not in st.session_state:
                st.session_state["card_idx"] = 0
            if "show_ans" not in st.session_state:
                st.session_state["show_ans"] = False

            idx = st.session_state["card_idx"] % len(cards)
            card = cards[idx]
            shown = st.session_state["show_ans"]

            face = ("❓ " + card["q"]) if not shown else ("💡 " + card["a"])
            st.markdown(
                f'<div class="card animate-in" style="text-align:center;min-height:180px;'
                f'display:flex;flex-direction:column;justify-content:center;padding:2rem;">'
                f'<div style="font-size:0.8rem;color:#64748b;margin-bottom:1rem">Card {idx+1}/{len(cards)}</div>'
                f'<div style="font-size:1.2rem;font-weight:600;color:#e2e8f0">{face}</div>'
                f'</div>', unsafe_allow_html=True)

            bc1, bc2, bc3 = st.columns(3)
            if bc1.button("◀ Prev"):
                st.session_state["card_idx"] = (idx - 1) % len(cards)
                st.session_state["show_ans"] = False
                st.rerun()
            if bc2.button("👁 Flip Card"):
                st.session_state["show_ans"] = not shown
                st.rerun()
            if bc3.button("Next ▶"):
                st.session_state["card_idx"] = (idx + 1) % len(cards)
                st.session_state["show_ans"] = False
                st.rerun()


# ─── 🎤 VIVA PREP (improved — mock viva mode) ───────────────────────
elif page == "🎤 Viva Prep":
    track_feature("Viva Prep")
    st.markdown("### 🎤 Viva / Interview Preparation")

    tab_gen, tab_mock = st.tabs(["✨ Generate Questions", "🎯 Mock Viva"])

    with tab_gen:
        c1, c2 = st.columns(2)
        subject = c1.text_input("Subject", placeholder="DBMS, OS, ML…")
        num_q = c1.slider("Questions", 5, 20, 10)
        vtype = c2.selectbox("Type", ["Viva Voce", "Technical Interview",
                                       "HR Interview", "Lab Viva", "Project Defence"])
        diff = c2.select_slider("Difficulty", ["Basic", "Intermediate", "Advanced"], value="Intermediate")

        if st.button("🎤 Generate Questions", type="primary"):
            if not subject.strip():
                st.warning("Enter a subject.")
            else:
                prompt = VIVA_PREP.format(num=num_q, difficulty=diff.lower(),
                                          viva_type=vtype, subject=subject)
                update_study_tracking(subject)
                with st.spinner("Preparing questions…"):
                    resp, _ = _ai(prompt, "Exam Prep", fallback=f"Viva prep unavailable for {subject}.")

                pairs = parse_viva_qa(resp)
                if pairs:
                    st.session_state.viva_data = [{"q": q.strip(), "a": a.strip()} for q, a in pairs]
                    _points(10)
                    for i, (q, a) in enumerate(pairs, 1):
                        st.markdown(
                            f'<div class="card card-amber" style="margin-bottom:0.6rem;">'
                            f'<div style="font-weight:700;color:#f59e0b;margin-bottom:0.4rem">Q{i}. {q.strip()}</div>'
                            f'<div style="color:#cbd5e1;font-size:0.95rem">{a.strip()}</div>'
                            f'</div>', unsafe_allow_html=True)
                    dl_text = "\n\n".join([f"Q{i+1}: {p['q']}\nA{i+1}: {p['a']}" for i, p in enumerate(st.session_state.viva_data)])
                    _dl(dl_text, f"viva_{subject[:20]}.txt", "⬇️ Download")
                else:
                    st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)

    with tab_mock:
        vdata = st.session_state.viva_data
        if not vdata:
            st.info("Generate viva questions first, then practice here.")
        else:
            st.markdown("#### 🎯 Practice Mode — Answer and get AI feedback")
            if "mock_idx" not in st.session_state:
                st.session_state["mock_idx"] = 0

            idx = st.session_state["mock_idx"] % len(vdata)
            item = vdata[idx]

            st.markdown(f'<div class="card card-amber" style="padding:1rem;">'
                        f'<b>Q{idx+1}.</b> {item["q"]}</div>', unsafe_allow_html=True)

            student_ans = st.text_area("Your answer:", height=120, key=f"mock_ans_{idx}",
                                       placeholder="Type your answer here…")

            c1, c2, c3 = st.columns(3)
            if c1.button("📝 Check My Answer", type="primary") and student_ans.strip():
                prompt = MOCK_VIVA.format(
                    question=item["q"], student_answer=student_ans, model_answer=item["a"]
                )
                with st.spinner("Evaluating…"):
                    resp, _ = _ai(prompt, "Exam Prep")
                st.markdown(f'<div class="card card-blue">{resp}</div>', unsafe_allow_html=True)
                _points(5)

            if c2.button("👁 Show Model Answer"):
                st.markdown(f'<div class="card card-green">{item["a"]}</div>', unsafe_allow_html=True)

            if c3.button("Next Question ▶"):
                st.session_state["mock_idx"] = (idx + 1) % len(vdata)
                st.rerun()


# ─── 📖 CITATION GENERATOR (improved — programmatic) ────────────────
elif page == "📖 Citation Generator":
    track_feature("Citation Generator")
    st.markdown("### 📖 Academic Citation Generator")

    tab1, tab2 = st.tabs(["📚 Generate", "📋 My Citations"])

    with tab1:
        c1, c2 = st.columns([2, 1])
        stype = c1.selectbox("Source Type", ["Book", "Journal Article", "Website",
                                              "Research Paper", "Conference Paper", "Thesis/Dissertation"])
        cstyle = c2.selectbox("Style", ["APA 7th Edition", "MLA 9th Edition", "IEEE", "Harvard"])

        col1, col2 = st.columns(2)
        authors = col1.text_input("Author(s)", placeholder="Smith, J. & Doe, A.")
        year = col2.text_input("Year", placeholder="2023")
        title = st.text_input("Title", placeholder="Title of the work")

        kwargs = {}
        if stype in ["Book", "Thesis/Dissertation"]:
            kwargs["publisher"] = col1.text_input("Publisher / Institution")
        elif stype == "Journal Article":
            kwargs["journal"] = col1.text_input("Journal Name")
            kwargs["volume"] = col2.text_input("Volume(Issue)")
            kwargs["pages"] = st.text_input("Pages", placeholder="45-67")
            kwargs["doi"] = st.text_input("DOI (optional)")
        elif stype == "Website":
            kwargs["url"] = st.text_input("URL")

        if st.button("📖 Generate Citation", type="primary"):
            if not title.strip():
                st.warning("Enter at least a title.")
            else:
                cite = build_citation(cstyle, stype, authors, year, title, **kwargs)
                st.markdown(f'<div class="citation-box"><b>Full Citation:</b><br>{cite["full"]}</div>',
                            unsafe_allow_html=True)
                st.markdown(f'<div class="citation-box"><b>In-text:</b> {cite["inline"]}</div>',
                            unsafe_allow_html=True)

                st.session_state.citation_list.append({
                    "style": cstyle, "type": stype, "title": title,
                    "full": cite["full"], "inline": cite["inline"],
                })
                st.toast("Citation added!", icon="✅")
                _points(5)

    with tab2:
        cites = st.session_state.citation_list
        if not cites:
            st.info("Generate citations in the first tab.")
        else:
            st.markdown(f"#### Your Citations ({len(cites)})")
            all_text = "REFERENCE LIST\n" + "=" * 50 + "\n\n"
            for i, c in enumerate(cites, 1):
                st.markdown(
                    f'<div class="citation-box">'
                    f'<div style="font-size:0.75rem;color:#64748b;margin-bottom:0.3rem">'
                    f'{i}. [{c["style"]}] {c["type"]}</div>{c["full"]}'
                    f'<br><span style="color:#64748b;font-size:0.85rem">In-text: {c["inline"]}</span>'
                    f'</div>', unsafe_allow_html=True)
                all_text += f"{i}. {c['full']}\n\n"
            _dl(all_text, "references.txt", "⬇️ Download All")
            if st.button("🗑️ Clear"):
                st.session_state.citation_list = []
                st.rerun()


# ─── 🌐 LANGUAGE TRANSLATOR (improved — side-by-side) ───────────────
elif page == "🌐 Language Translator":
    track_feature("Language Translator")
    st.markdown("### 🌐 Study Content Translator")

    c1, c2 = st.columns([3, 1])
    text = c1.text_area("Text to Translate", height=200,
                        placeholder="Paste academic content here…")
    lang = c2.selectbox("Translate To", [
        "Hindi", "Marathi", "Bengali", "Tamil", "Telugu", "Gujarati",
        "Punjabi", "Urdu", "Kannada", "Malayalam",
        "Spanish", "French", "German", "Arabic", "Chinese (Simplified)",
        "English",
    ])
    mode = c2.selectbox("Mode", ["Full Translation", "Simple Explanation",
                                  "Key Terms + Translation", "Bilingual"])

    if st.button("🌐 Translate", type="primary"):
        if not text.strip():
            st.warning("Enter text to translate.")
        else:
            mode_map = {"Full Translation": "full", "Simple Explanation": "simple",
                        "Key Terms + Translation": "terms", "Bilingual": "bilingual"}
            prompt = TRANSLATE[mode_map[mode]].format(lang=lang, text=text)
            with st.spinner(f"Translating to {lang}…"):
                resp, _ = _ai(prompt, "General Study Assistant", fallback="Translation unavailable.")

            # Side-by-side display for bilingual and full
            col_o, col_t = st.columns(2)
            with col_o:
                st.markdown("**Original:**")
                st.markdown(f'<div class="card">{text[:2000]}</div>', unsafe_allow_html=True)
            with col_t:
                st.markdown(f"**{lang}:**")
                st.markdown(f'<div class="card card-green">{resp}</div>', unsafe_allow_html=True)

            _points(5)
            _dl(resp, f"translation_{lang.split()[0].lower()}.txt", f"⬇️ Download {lang}")


# ─── 📐 FORMULA SHEET ───────────────────────────────────────────────
elif page == "📐 Formula Sheet":
    track_feature("Formula Sheet")
    st.markdown("### 📐 Formula & Cheatsheet Generator")

    c1, c2 = st.columns(2)
    subject = c1.text_input("Subject", placeholder="Physics, Math, DBMS…")
    sheet_type = c1.selectbox("Type", [
        "Formula Sheet (Equations & Formulas)",
        "Cheatsheet (Key Concepts & Definitions)",
        "Quick Reference (Commands & Syntax)",
        "Theory Notes (Important Points)",
    ])
    scope = c2.selectbox("Scope", ["Complete", "Exam Focused", "Beginner", "Advanced"])
    exam = c2.text_input("Exam / Chapter (optional)")

    if st.button("📐 Generate Sheet", type="primary"):
        if not subject.strip():
            st.warning("Enter a subject.")
        else:
            exam_note = f" — {exam}" if exam.strip() else ""
            prompt = FORMULA_SHEET.format(
                sheet_type=sheet_type, subject=subject, exam_note=exam_note, scope=scope
            )
            update_study_tracking(subject)
            with st.spinner("Generating…"):
                resp, _ = _ai(prompt, "Exam Prep", fallback=f"Unavailable for {subject}.")
            st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
            _points(10)
            _dl(resp, f"formula_{subject[:20].replace(' ','_')}.txt", "⬇️ Download")


# ─── 🔍 WEB SEARCH ──────────────────────────────────────────────────
elif page == "🔍 Web Search":
    track_feature("Web Search")
    st.markdown("### 🔍 Live Web Search")

    if not tavily_available():
        st.error("Tavily API key not configured. Add TAVILY_API_KEY to `.streamlit/secrets.toml`.")
    else:
        st.success("🟢 Tavily Web Search active")

        c1, c2, c3 = st.columns([4, 1, 1])
        query = c1.text_input("Search", placeholder="e.g. Latest AI developments 2025")
        depth = c2.selectbox("Depth", ["basic", "advanced"])
        max_r = c3.slider("Results", 3, 10, 5)

        tab_g, tab_a, tab_n, tab_ai = st.tabs(["🌐 General", "📚 Academic", "📰 News", "🤖 AI + Search"])

        with tab_g:
            if st.button("🔍 Search", key="ws_g", type="primary") and query.strip():
                with st.spinner(f'Searching "{query}"…'):
                    data = tavily_search(query, depth, max_r, True, "general")
                if not data:
                    st.error("Search failed.")
                else:
                    if data.get("answer"):
                        st.markdown(f'<div class="card card-blue"><b>🤖 AI Answer</b><br>{data["answer"]}</div>',
                                    unsafe_allow_html=True)
                    for i, r in enumerate(data.get("results", []), 1):
                        score = int(r.get("score", 0) * 100)
                        _title = (r.get("title","") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        _url = (r.get("url","") or "#").replace('"','%22')
                        _content = (r.get("content","") or "")[:300].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        st.markdown(
                            f'<div class="card">'
                            f'<a href="{_url}" target="_blank" rel="noopener noreferrer" style="color:#38bdf8;font-weight:600;">'
                            f'{i}. {_title}</a>'
                            f'<span style="float:right;font-size:0.75rem;color:#64748b;">{score}%</span>'
                            f'<div style="font-size:0.88rem;color:#cbd5e1;margin-top:0.3rem;">'
                            f'{_content}…</div></div>', unsafe_allow_html=True)
                    _points(5)

        with tab_a:
            if st.button("📚 Search Academic", key="ws_a", type="primary") and query.strip():
                with st.spinner("Searching academic sources…"):
                    data = tavily_search(f"{query} academic research paper", depth, max_r, True, "general")
                if data:
                    for r in data.get("results", []):
                        _title = (r.get("title","") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        _url = (r.get("url","") or "#").replace('"','%22')
                        _content = (r.get("content","") or "")[:250].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        st.markdown(
                            f'<div class="card card-purple">'
                            f'<a href="{_url}" target="_blank" rel="noopener noreferrer" style="color:#a855f7;font-weight:600;">'
                            f'{_title}</a>'
                            f'<div style="font-size:0.88rem;color:#cbd5e1;margin-top:0.3rem;">'
                            f'{_content}…</div></div>', unsafe_allow_html=True)

        with tab_n:
            if st.button("📰 Search News", key="ws_n", type="primary") and query.strip():
                with st.spinner("Searching news…"):
                    data = tavily_search(f"{query} latest news", depth, max_r, True, "news")
                if data:
                    for r in data.get("results", []):
                        _title = (r.get("title","") or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        _url = (r.get("url","") or "#").replace('"','%22')
                        _content = (r.get("content","") or "")[:250].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                        st.markdown(
                            f'<div class="card card-amber">'
                            f'<a href="{_url}" target="_blank" rel="noopener noreferrer" style="color:#f59e0b;font-weight:600;">'
                            f'{_title}</a>'
                            f'<div style="font-size:0.88rem;color:#cbd5e1;margin-top:0.3rem;">'
                            f'{_content}…</div></div>', unsafe_allow_html=True)

        with tab_ai:
            st.info("AI searches the web first, then synthesises a comprehensive answer.")
            ask = st.text_area("Your question", height=100, key="ws_ask_q",
                               placeholder="e.g. Best free ML resources in 2025?")
            if st.button("🤖 Search & Answer", key="ws_ask", type="primary") and ask.strip():
                with st.spinner("Searching + synthesising…"):
                    data = tavily_search(ask, "advanced", max_r, True)

                if not data:
                    with st.spinner("Web failed — using AI only…"):
                        resp, _ = _ai(ask, "General Study Assistant")
                    st.markdown(f'<div class="card">{resp}</div>', unsafe_allow_html=True)
                else:
                    ctx = "\n\n---\n\n".join([
                        f"Source: {r.get('title','')}\nURL: {r.get('url','')}\n{r.get('content','')[:500]}"
                        for r in data.get("results", [])[:5]
                    ])
                    prompt = WEB_SEARCH_SYNTHESIZE.format(question=ask, context=ctx)
                    with st.spinner("AI synthesising…"):
                        resp, _ = _ai(prompt, "General Study Assistant",
                                      fallback=data.get("answer", "Unable to synthesise."))
                    st.markdown(f'<div class="card card-green"><b>🤖 AI Answer — web-backed</b><br>{resp}</div>',
                                unsafe_allow_html=True)
                    with st.expander("🔗 Sources"):
                        for r in data.get("results", []):
                            st.markdown(f"- [{r.get('title','')}]({r.get('url','#')})")
                    _msg("user", ask)
                    _msg("assistant", resp)
                    _points(10)


# ─── 📸 ASSIGNMENT SOLVER ───────────────────────────────────────────
elif page == "📸 Assignment Solver":
    track_feature("Assignment Solver")
    st.markdown("### 📸 Assignment Solver — Photo to Answer Sheet")
    st.info("📷 Upload a photo of your question paper → AI extracts questions → generates answers → printable A4 page")

    st.markdown("#### Step 1 — Upload Question Paper")
    uploaded_img = st.file_uploader("Upload image", type=["jpg", "jpeg", "png", "bmp", "webp"], key="asolver_img")

    extracted_q = ""

    if uploaded_img:
        col_img, col_q = st.columns(2)
        with col_img:
            st.image(uploaded_img, caption="Your question paper", use_container_width=True)
        with col_q:
            img_bytes = uploaded_img.getvalue()
            mime = f"image/{uploaded_img.type.split('/')[-1]}" if "/" in uploaded_img.type else "image/jpeg"
            with st.spinner("Reading questions with AI Vision…"):
                extracted_q = call_vision(img_bytes, VISION_PROMPT, mime)
            if not extracted_q:
                st.warning("AI Vision unavailable — trying OCR…")
                try:
                    from PIL import Image as PILImage
                    import pytesseract, io
                    img = PILImage.open(io.BytesIO(img_bytes))
                    extracted_q = pytesseract.image_to_string(img).strip()
                except Exception as e:
                    st.error(f"OCR failed: {e}")
            if extracted_q:
                st.success("✅ Questions extracted!")

        if extracted_q:
            st.markdown("#### Step 2 — Review & Edit")
            extracted_q = st.text_area("Extracted Questions", value=extracted_q, height=200, key="asolver_q")

    if not uploaded_img:
        st.markdown("**— or type manually —**")
        extracted_q = st.text_area("Type/paste questions", height=160,
                                   placeholder="Q1. What is the OSI model?\nQ2. Explain TCP/IP…",
                                   key="asolver_manual")

    if extracted_q and extracted_q.strip():
        _hr()
        st.markdown("#### Step 3 — Personalise")

        c1, c2, c3 = st.columns(3)
        student_name = c1.text_input("Name", value=st.session_state.user_name or "", placeholder="Your Name")
        subject = c2.text_input("Subject", placeholder="DBMS / Python…")
        roll_no = c3.text_input("Roll No.", placeholder="BCA/2022/045")

        c4, c5, c6 = st.columns(3)
        exam_name = c4.text_input("Exam", placeholder="Internal Assessment 2")
        answer_date = c5.text_input("Date", value=datetime.now().strftime("%d-%m-%Y"))
        font_style = c6.selectbox("Handwriting", ["Caveat", "Kalam", "Patrick Hand", "Architects Daughter"])

        font_urls = {
            "Caveat": "https://fonts.googleapis.com/css2?family=Caveat:wght@400;700&display=swap",
            "Kalam": "https://fonts.googleapis.com/css2?family=Kalam:wght@400;700&display=swap",
            "Patrick Hand": "https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap",
            "Architects Daughter": "https://fonts.googleapis.com/css2?family=Architects+Daughter&display=swap",
        }

        answer_style = st.selectbox("Answer Style", [
            "Detailed (150-200 words each)",
            "Medium (80-100 words each)",
            "Points / Bullet Format",
            "Definition + Explanation + Example",
        ])

        _hr()
        if st.button("✍️ Generate Answer Sheet", type="primary", use_container_width=True):
            style_map = {
                "Detailed (150-200 words each)": "detailed paragraphs of 150-200 words per answer",
                "Medium (80-100 words each)": "concise answers of 80-100 words per answer",
                "Points / Bullet Format": "numbered point-wise answers",
                "Definition + Explanation + Example": "answer with definition, explanation, and example",
            }
            prompt = ASSIGNMENT_SOLVER.format(
                style=style_map[answer_style],
                subject=subject or "General",
                questions=extracted_q,
            )
            with st.spinner("Generating answers (30-40 seconds)…"):
                resp, src = _ai(prompt, "Assignment Writer", fallback="__FAILED__")

            if resp and resp.strip() != "__FAILED__" and len(resp.strip()) > 30:
                resp = strip_markdown(resp)
                _points(15)

                st.markdown("#### Preview")
                font_url = font_urls[font_style]
                safe = resp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                st.markdown(
                    f'<link href="{font_url}" rel="stylesheet">'
                    f'<div style="font-family:\'{font_style}\',cursive;font-size:1.15rem;line-height:2;'
                    f'color:#1a1a2e;background:#fff;border:1px solid #ddd;border-radius:8px;'
                    f'padding:2rem;max-height:500px;overflow-y:auto;'
                    f'background-image:repeating-linear-gradient(transparent,transparent 39px,#b8d4f0 39px,#b8d4f0 40px);'
                    f'background-size:100% 40px;">'
                    f'<div style="white-space:pre-wrap;">{safe}</div></div>',
                    unsafe_allow_html=True,
                )

                # Download buttons
                _hr()
                def _he(s: str) -> str:
                    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
                safe_resp = resp.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                _safe_name = _he(student_name)
                _safe_roll = _he(roll_no)
                _safe_subj = _he(subject) or ""
                _safe_exam = _he(exam_name) or "Assignment"
                _safe_date = _he(answer_date)
                a4_html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<title>Answer Sheet</title><link href="{font_url}" rel="stylesheet">
<style>*{{margin:0;padding:0;box-sizing:border-box;}}
body{{background:#e8e8e8;display:flex;flex-direction:column;align-items:center;padding:30px 0;font-family:'{font_style}',cursive;}}
.controls{{width:210mm;display:flex;gap:12px;margin-bottom:16px;}}
.controls button{{padding:10px 28px;border:none;border-radius:8px;cursor:pointer;font-weight:700;font-size:15px;}}
.btn-print{{background:#4f46e5;color:#fff;}}.btn-close{{background:#334155;color:#fff;}}
.page{{width:210mm;min-height:297mm;background:#fff;padding:18mm 20mm 18mm 28mm;box-shadow:0 4px 24px rgba(0,0,0,0.18);
position:relative;background-image:repeating-linear-gradient(transparent,transparent 31px,#b8d4f0 31px,#b8d4f0 32px);
background-size:100% 32px;background-position:0 60px;border-left:3px solid #f87171;}}
.header-box{{border:2px solid #334155;border-radius:4px;padding:8px 12px;margin-bottom:10px;background:#fff;
display:grid;grid-template-columns:1fr 1fr;gap:4px 20px;font-size:15px;color:#1e293b;line-height:1.8;}}
.header-box .full{{grid-column:1/-1;}}.header-box b{{color:#3730a3;}}
.content{{font-family:'{font_style}',cursive;font-size:19px;line-height:32px;color:#0f172a;white-space:pre-wrap;margin-top:8px;}}
@media print{{body{{background:#fff;padding:0;}}.controls{{display:none;}}.page{{box-shadow:none;margin:0;width:100%;}}}}
</style></head><body>
<div class="controls"><button class="btn-print" onclick="window.print()">🖨️ Print / Save as PDF</button>
<button class="btn-close" onclick="window.close()">✕ Close</button></div>
<div class="page"><div class="header-box">
<div class="full"><b>Exam:</b> {_safe_exam}</div>
<div><b>Name:</b> {_safe_name}</div><div><b>Roll:</b> {_safe_roll}</div>
<div><b>Subject:</b> {_safe_subj}</div><div><b>Date:</b> {_safe_date}</div>
</div><div class="content">{safe_resp}</div></div></body></html>"""

                d1, d2 = st.columns(2)
                d1.download_button("⬇️ Download HTML (Print as PDF)", a4_html,
                                   file_name=f"answer_sheet_{(student_name or 'student').replace(' ','_')}.html",
                                   mime="text/html", use_container_width=True)
                d2.download_button("⬇️ Download Plain Text", resp,
                                   file_name="answers.txt", mime="text/plain", use_container_width=True)
                st.success("✅ Done! Open the HTML file → Ctrl+P → Save as PDF")
            else:
                st.error("Could not generate answers. Please try again.")


# ─── 🌳 VISUAL EXPLAINER ─────────────────────────────────────────────
elif page == "🌳 Visual Explainer":
    track_feature("Visual Explainer")
    st.markdown("### 🌳 Visual Explainer — Diagrams & Concept Maps")
    st.caption("Type any CS or academic topic → get a colourful, interactive diagram to understand it visually.")

    _hr()

    # ── Quick topic buttons ──────────────────────────────────────────
    st.markdown('<div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;'
                'letter-spacing:1.5px;margin-bottom:0.6rem;font-weight:600;">⚡ Quick Topics</div>',
                unsafe_allow_html=True)
    quick_topics = [
        ("🌲", "Binary Search Tree"),
        ("🔗", "Linked List"),
        ("📚", "Stack & Queue"),
        ("🕸️", "BFS / DFS Graph"),
        ("🔄", "Merge Sort"),
        ("🏗️", "OOP Inheritance"),
        ("🌐", "OSI Model Layers"),
        ("🗄️", "Database ER Diagram"),
        ("⚡", "Dijkstra Algorithm"),
        ("🔒", "Deadlock in OS"),
        ("📦", "TCP/IP Handshake"),
        ("🧮", "Dynamic Programming"),
    ]
    qt_cols = st.columns(6)
    for i, (icon, label) in enumerate(quick_topics):
        with qt_cols[i % 6]:
            if st.button(f"{icon} {label}", key=f"qt_{i}", use_container_width=True):
                st.session_state["_vis_topic"] = label
                st.rerun()

    _hr()

    # ── Custom topic input ───────────────────────────────────────────
    v1, v2 = st.columns([4, 1])
    topic_input = v1.text_input(
        "Topic or concept",
        value=st.session_state.pop("_vis_topic", ""),
        placeholder="e.g. AVL Tree, Quick Sort, OOP Polymorphism, TCP Handshake…",
        label_visibility="collapsed",
    )
    diag_type = v2.selectbox("Type", ["Auto", "Flowchart", "Class Diagram", "ER Diagram", "Sequence"],
                              label_visibility="collapsed")

    type_hint = {
        "Flowchart":    " Use graph TD diagram type (flowchart/tree).",
        "Class Diagram": " Use classDiagram diagram type.",
        "ER Diagram":   " Use erDiagram diagram type.",
        "Sequence":     " Use sequenceDiagram diagram type.",
        "Auto":         "",
    }

    gen_col, _ = st.columns([2, 5])
    generate_clicked = gen_col.button("🎨 Generate Diagram", type="primary", use_container_width=True)

    if generate_clicked and topic_input.strip():
        concept = topic_input.strip()
        forced_type = type_hint.get(diag_type, "")
        diag_prompt = DIAGRAM_GEN.format(concept=concept + forced_type)
        with st.spinner(f"🎨 Generating diagram for '{concept}'…"):
            raw_diag, _ = _ai(diag_prompt, "General Study Assistant")
        code = clean_mermaid(raw_diag)

        if code and len(code) > 15:
            st.session_state["vis_current_code"] = code
            st.session_state["vis_current_topic"] = concept
            update_study_tracking(concept)
            _points(5)
        else:
            st.warning("Could not generate a diagram. Try rephrasing your topic.")

    # ── Render current diagram ───────────────────────────────────────
    if st.session_state.get("vis_current_code"):
        code = st.session_state["vis_current_code"]
        topic_name = st.session_state.get("vis_current_topic", "")

        st.markdown(
            f'<div style="margin:0.5rem 0 0.2rem;">'
            f'<span style="font-weight:700;color:#818cf8;font-size:1rem;">{topic_name}</span>'
            f'<span style="color:#475569;font-size:0.82rem;margin-left:0.5rem;">— visual diagram</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        _render_mermaid(code, height=540)

        # Code + explanation columns
        _hr()
        ec1, ec2 = st.columns([1, 1])

        with ec1:
            with st.expander("🔍 View Mermaid Code"):
                st.code(code, language="text")
            _dl(code, f"diagram_{topic_name[:20].replace(' ','_')}.mmd", "⬇️ Download Diagram Code")

        with ec2:
            if st.button("📖 Explain This Diagram", use_container_width=True):
                with st.spinner("Getting explanation…"):
                    exp_resp, _ = _ai(
                        f"Explain the concept '{topic_name}' in simple terms for a college student. "
                        f"Cover: what it is, how it works, where it's used, and key takeaways. "
                        f"Keep it clear and structured.",
                        "General Study Assistant",
                    )
                st.markdown(f'<div class="card card-blue">{exp_resp}</div>', unsafe_allow_html=True)
                _points(5)

        _hr()

        # ── Related diagrams ─────────────────────────────────────────
        st.markdown("#### 🔗 Explore Related Topics")
        rel_prompt = (
            f"List exactly 6 related CS/academic topics closely connected to '{topic_input}'. "
            f"Return ONLY a comma-separated list of topic names, nothing else."
        )
        if st.button("✨ Suggest Related Topics", use_container_width=False):
            with st.spinner("Finding related topics…"):
                rel_raw, _ = _ai(rel_prompt, "General Study Assistant")
            related = [t.strip() for t in rel_raw.split(",") if t.strip()][:6]
            if related:
                rel_cols = st.columns(min(len(related), 3))
                for i, rel in enumerate(related):
                    with rel_cols[i % 3]:
                        if st.button(f"🌳 {rel}", key=f"rel_{i}", use_container_width=True):
                            st.session_state["_vis_topic"] = rel
                            st.rerun()
    else:
        # Empty state illustration
        st.markdown(
            '<div style="text-align:center;padding:3rem 1rem;color:#334155;">'
            '<div style="font-size:4rem;margin-bottom:1rem;">🌳</div>'
            '<div style="font-size:1.1rem;font-weight:600;color:#475569;margin-bottom:0.4rem;">'
            'Choose a quick topic above or type your own</div>'
            '<div style="font-size:0.88rem;color:#334155;">'
            'Supports: Trees · Graphs · Sorting · OOP · Networking · Databases · OS · Algorithms'
            '</div></div>',
            unsafe_allow_html=True,
        )


# ═════════════════════════════════════════════════════════════════════
#  Footer
# ═════════════════════════════════════════════════════════════════════

st.markdown(
    f'<div class="app-footer">🎓 AI Academic Platform v3.0 · {TOOL_COUNT} Tools + Live Web Search · '
    f'NVIDIA NIM · OpenRouter · Gemini · Claude · Tavily · Built for college students</div>',
    unsafe_allow_html=True,
)
