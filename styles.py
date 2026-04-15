"""
styles.py — All CSS for the AI Academic Platform
"""

CSS = """
/* ── Import Fonts ─────────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Root Variables ───────────────────────────────────────────────── */
:root {
    --bg-primary:      #050812;
    --bg-surface:      #0c1220;
    --bg-card:         #0f1829;
    --bg-card-hover:   #162035;
    --bg-elevated:     #1a2540;
    --border:          rgba(255,255,255,0.06);
    --border-hover:    rgba(99,102,241,0.4);
    --border-active:   rgba(99,102,241,0.7);
    --text-primary:    #f1f5f9;
    --text-secondary:  #94a3b8;
    --text-muted:      #475569;
    --accent-indigo:   #818cf8;
    --accent-blue:     #38bdf8;
    --accent-green:    #34d399;
    --accent-amber:    #fbbf24;
    --accent-red:      #f87171;
    --accent-purple:   #c084fc;
    --accent-pink:     #f472b6;
    --glow-indigo:     0 0 20px rgba(129,140,248,0.25);
    --glow-blue:       0 0 20px rgba(56,189,248,0.25);
    --glow-green:      0 0 20px rgba(52,211,153,0.25);
    --gradient-primary:  linear-gradient(135deg, #818cf8 0%, #38bdf8 100%);
    --gradient-warm:     linear-gradient(135deg, #fbbf24 0%, #f87171 100%);
    --gradient-purple:   linear-gradient(135deg, #c084fc 0%, #818cf8 100%);
    --gradient-green:    linear-gradient(135deg, #34d399 0%, #38bdf8 100%);
    --gradient-surface:  linear-gradient(180deg, #0c1220 0%, #050812 100%);
    --radius-xs:  6px;
    --radius-sm:  10px;
    --radius-md:  14px;
    --radius-lg:  18px;
    --radius-xl:  24px;
    --radius-2xl: 32px;
    --shadow-sm:  0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3);
    --shadow-md:  0 4px 16px rgba(0,0,0,0.5), 0 2px 6px rgba(0,0,0,0.3);
    --shadow-lg:  0 8px 32px rgba(0,0,0,0.6), 0 4px 12px rgba(0,0,0,0.4);
    --font-body:  'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono:  'JetBrains Mono', 'Fira Code', monospace;
    --transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global Reset & Base ──────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

.stApp {
    background: var(--bg-primary) !important;
    font-family: var(--font-body) !important;
    color: var(--text-primary) !important;
}

/* ── Hide Streamlit chrome ────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }

/* ── Scrollbar ────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-surface); }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(129,140,248,0.6); }

/* ═══════════════════════════════════════════════════════════════════ */
/*  APP HEADER                                                         */
/* ═══════════════════════════════════════════════════════════════════ */
.app-header {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0a0f1e 0%, #111827 40%, #0c1629 100%);
    border: 1px solid rgba(129,140,248,0.15);
    border-radius: var(--radius-xl);
    padding: 1.6rem 2.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
}
.app-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 60% 80% at 20% 50%, rgba(129,140,248,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 50% 70% at 80% 50%, rgba(56,189,248,0.06) 0%, transparent 60%);
    pointer-events: none;
}
.app-header::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(129,140,248,0.5) 40%, rgba(56,189,248,0.5) 60%, transparent 100%);
}
.app-header h1 {
    font-size: 1.9rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 35%, #38bdf8 70%, #7dd3fc 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.35rem;
    position: relative;
}
.app-header p {
    color: var(--text-muted);
    font-size: 0.88rem;
    margin: 0;
    position: relative;
    font-weight: 400;
}
.tool-count {
    background: rgba(129,140,248,0.12);
    color: var(--accent-indigo);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(129,140,248,0.25);
    letter-spacing: 0.02em;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  GLASS CARDS                                                        */
/* ═══════════════════════════════════════════════════════════════════ */
.card {
    background: rgba(15, 24, 41, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.85rem;
    transition: var(--transition);
    line-height: 1.7;
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06), transparent);
    pointer-events: none;
}
.card:hover {
    border-color: rgba(129,140,248,0.25);
    background: rgba(22, 32, 53, 0.9);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

/* Accent stripe variants */
.card-green  { border-left: 3px solid var(--accent-green);  }
.card-blue   { border-left: 3px solid var(--accent-blue);   }
.card-purple { border-left: 3px solid var(--accent-purple); }
.card-amber  { border-left: 3px solid var(--accent-amber);  }
.card-red    { border-left: 3px solid var(--accent-red);    }

.card-green::after  { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--accent-green), rgba(52,211,153,0.2)); border-radius: 3px 0 0 3px; }
.card-blue::after   { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--accent-blue), rgba(56,189,248,0.2)); border-radius: 3px 0 0 3px; }
.card-purple::after { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--accent-purple), rgba(192,132,252,0.2)); border-radius: 3px 0 0 3px; }
.card-amber::after  { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--accent-amber), rgba(251,191,36,0.2)); border-radius: 3px 0 0 3px; }
.card-red::after    { content: ''; position: absolute; top: 0; left: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--accent-red), rgba(248,113,113,0.2)); border-radius: 3px 0 0 3px; }

/* ═══════════════════════════════════════════════════════════════════ */
/*  KPI METRIC CARDS                                                   */
/* ═══════════════════════════════════════════════════════════════════ */
.kpi {
    background: rgba(15, 24, 41, 0.8);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.1rem 0.8rem;
    text-align: center;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(129,140,248,0.2), transparent);
}
.kpi:hover {
    border-color: rgba(129,140,248,0.3);
    box-shadow: var(--glow-indigo);
}
.kpi h3 {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.02em;
}
.kpi p {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin: 0.25rem 0 0;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  RANK BADGES                                                        */
/* ═══════════════════════════════════════════════════════════════════ */
.rank-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.rank-bronze  { background: rgba(205,127,50,0.12);  color: #d97706; border: 1px solid rgba(205,127,50,0.25); }
.rank-silver  { background: rgba(203,213,225,0.10); color: #cbd5e1; border: 1px solid rgba(203,213,225,0.2); }
.rank-gold    { background: rgba(251,191,36,0.12);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.3);  box-shadow: 0 0 12px rgba(251,191,36,0.1); }
.rank-diamond { background: rgba(56,189,248,0.12);  color: #38bdf8; border: 1px solid rgba(56,189,248,0.3);  box-shadow: 0 0 12px rgba(56,189,248,0.1); }
.rank-master  { background: rgba(192,132,252,0.12); color: #c084fc; border: 1px solid rgba(192,132,252,0.3); box-shadow: 0 0 12px rgba(192,132,252,0.15); }

/* ═══════════════════════════════════════════════════════════════════ */
/*  PROGRESS BAR                                                       */
/* ═══════════════════════════════════════════════════════════════════ */
.progress-bar {
    width: 100%;
    height: 5px;
    background: rgba(255,255,255,0.05);
    border-radius: 3px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    background: var(--gradient-primary);
    border-radius: 3px;
    transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}
.progress-fill::after {
    content: '';
    position: absolute;
    top: 0; right: 0; bottom: 0;
    width: 40px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4));
    animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
    0%   { transform: translateX(-40px); opacity: 0; }
    50%  { opacity: 1; }
    100% { transform: translateX(40px);  opacity: 0; }
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  FLASHCARDS                                                         */
/* ═══════════════════════════════════════════════════════════════════ */
.flashcard {
    background: rgba(15,24,41,0.85);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.3rem;
    margin-bottom: 0.85rem;
    min-height: 148px;
    transition: var(--transition-slow);
    position: relative;
    overflow: hidden;
}
.flashcard::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--gradient-primary);
    opacity: 0;
    transition: opacity 0.2s;
}
.flashcard:hover {
    border-color: rgba(129,140,248,0.4);
    transform: translateY(-3px);
    box-shadow: var(--shadow-md), var(--glow-indigo);
}
.flashcard:hover::before { opacity: 1; }
.flashcard-q {
    font-weight: 600;
    color: var(--accent-blue);
    margin-bottom: 0.65rem;
    font-size: 0.96rem;
}
.flashcard-a {
    color: var(--text-secondary);
    font-size: 0.9rem;
    border-top: 1px solid var(--border);
    padding-top: 0.65rem;
    line-height: 1.6;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  QUIZ INTERACTIVE                                                   */
/* ═══════════════════════════════════════════════════════════════════ */
.quiz-option {
    background: rgba(15,24,41,0.8);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1.1rem;
    margin-bottom: 0.45rem;
    cursor: pointer;
    transition: var(--transition);
    font-size: 0.93rem;
}
.quiz-option:hover {
    border-color: rgba(129,140,248,0.5);
    background: rgba(129,140,248,0.08);
    transform: translateX(3px);
}
.quiz-correct {
    border-color: var(--accent-green) !important;
    background: rgba(52,211,153,0.1) !important;
    box-shadow: 0 0 12px rgba(52,211,153,0.15) !important;
}
.quiz-wrong {
    border-color: var(--accent-red) !important;
    background: rgba(248,113,113,0.1) !important;
    box-shadow: 0 0 12px rgba(248,113,113,0.12) !important;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  SIDEBAR                                                            */
/* ═══════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #070d1a 0%, #050812 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.5rem;
}

/* Sidebar radio nav buttons */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px !important;
}
section[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border-radius: var(--radius-sm);
    padding: 0.4rem 0.8rem;
    transition: var(--transition);
    cursor: pointer;
    font-size: 0.88rem !important;
    font-weight: 500;
    color: var(--text-secondary) !important;
    width: 100%;
    display: block;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(129,140,248,0.08);
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
section[data-testid="stSidebar"] .stRadio [data-checked="true"] + label {
    background: rgba(129,140,248,0.12);
    color: var(--accent-indigo) !important;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  SCORE BADGES                                                       */
/* ═══════════════════════════════════════════════════════════════════ */
.score-pill {
    display: inline-block;
    padding: 4px 16px;
    border-radius: 20px;
    font-weight: 800;
    font-size: 0.88rem;
    letter-spacing: 0.04em;
}
.score-a { background: rgba(52,211,153,0.15);  color: var(--accent-green);  border: 1px solid rgba(52,211,153,0.3); }
.score-b { background: rgba(56,189,248,0.15);  color: var(--accent-blue);   border: 1px solid rgba(56,189,248,0.3); }
.score-c { background: rgba(251,191,36,0.15);  color: var(--accent-amber);  border: 1px solid rgba(251,191,36,0.3); }
.score-d { background: rgba(248,113,113,0.15); color: var(--accent-red);    border: 1px solid rgba(248,113,113,0.3); }

/* ═══════════════════════════════════════════════════════════════════ */
/*  CITATION BOX                                                       */
/* ═══════════════════════════════════════════════════════════════════ */
.citation-box {
    background: rgba(15,24,41,0.85);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-amber);
    border-radius: var(--radius-sm);
    padding: 1rem 1.3rem;
    margin-bottom: 0.65rem;
    font-family: var(--font-mono);
    font-size: 0.87rem;
    line-height: 1.75;
    color: var(--text-secondary);
    transition: var(--transition);
}
.citation-box:hover {
    border-color: rgba(251,191,36,0.4);
    background: rgba(22,32,53,0.9);
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  SECTION DIVIDER                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
.divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.3rem 0;
    position: relative;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  STATUS DOTS                                                        */
/* ═══════════════════════════════════════════════════════════════════ */
.status-online  { color: var(--accent-green); }
.status-offline { color: var(--accent-red);   }

/* ═══════════════════════════════════════════════════════════════════ */
/*  CATEGORY HEADER                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
.cat-header {
    font-size: 0.82rem;
    font-weight: 700;
    margin: 1rem 0 0.55rem;
    padding-left: 0.7rem;
    border-left: 3px solid;
    text-transform: uppercase;
    letter-spacing: 1.2px;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  FOOTER                                                             */
/* ═══════════════════════════════════════════════════════════════════ */
.app-footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.73rem;
    padding: 2rem 0 1.2rem;
    border-top: 1px solid var(--border);
    margin-top: 2.5rem;
    letter-spacing: 0.02em;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  ANIMATIONS                                                         */
/* ═══════════════════════════════════════════════════════════════════ */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseDot {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.4; }
}
.animate-in {
    animation: fadeSlideIn 0.4s ease-out both;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  STREAMLIT WIDGET OVERRIDES                                         */
/* ═══════════════════════════════════════════════════════════════════ */

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #38bdf8 100%) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.01em;
    transition: var(--transition) !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.3) !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
    filter: brightness(1.08) !important;
}
.stButton > button[kind="primary"]:active {
    transform: translateY(0) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: rgba(129,140,248,0.4) !important;
    color: var(--text-primary) !important;
    background: rgba(129,140,248,0.06) !important;
}

/* Text inputs */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    transition: var(--transition) !important;
}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(129,140,248,0.6) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.1), var(--glow-indigo) !important;
    outline: none !important;
}
div[data-testid="stTextArea"] textarea::placeholder,
div[data-testid="stTextInput"] input::placeholder {
    color: var(--text-muted) !important;
}

/* Selectbox */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}
div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: rgba(129,140,248,0.5) !important;
}

/* Slider */
div[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background: var(--accent-indigo) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.2) !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] > div > div:last-child > div {
    background: var(--gradient-primary) !important;
}

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(15,24,41,0.6) !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    padding: 3px !important;
    gap: 2px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    transition: var(--transition) !important;
    padding: 0.45rem 1rem !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(129,140,248,0.15) !important;
    color: var(--accent-indigo) !important;
    font-weight: 600 !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: rgba(15,24,41,0.8) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.9rem 1rem !important;
    transition: var(--transition) !important;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(129,140,248,0.25) !important;
}
div[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    color: var(--text-muted) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
div[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.02em;
}

/* Expander */
details[data-testid="stExpander"] {
    background: rgba(15,24,41,0.7) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden;
}
details[data-testid="stExpander"] summary {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 0.75rem 1rem !important;
    transition: var(--transition) !important;
}
details[data-testid="stExpander"] summary:hover {
    color: var(--text-primary) !important;
    background: rgba(129,140,248,0.05) !important;
}

/* Info / success / warning / error boxes */
div[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border-width: 1px !important;
    font-size: 0.9rem !important;
}
div[role="alert"][data-baseweb="notification"] {
    border-radius: var(--radius-sm) !important;
}

/* File uploader */
div[data-testid="stFileUploadDropzone"] {
    background: rgba(15,24,41,0.7) !important;
    border: 2px dashed rgba(129,140,248,0.25) !important;
    border-radius: var(--radius-md) !important;
    transition: var(--transition) !important;
}
div[data-testid="stFileUploadDropzone"]:hover {
    border-color: rgba(129,140,248,0.5) !important;
    background: rgba(129,140,248,0.04) !important;
}

/* Number input */
div[data-testid="stNumberInput"] input {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* Date input */
div[data-testid="stDateInput"] input {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
}

/* Checkbox */
div[data-testid="stCheckbox"] label {
    color: var(--text-secondary) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

/* Chat messages */
div[data-testid="stChatMessage"] {
    background: rgba(15,24,41,0.7) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 0.6rem !important;
    transition: var(--transition) !important;
}
div[data-testid="stChatMessage"]:hover {
    border-color: rgba(129,140,248,0.15) !important;
}

/* Chat input */
div[data-testid="stChatInput"] textarea {
    background: rgba(15,24,41,0.95) !important;
    border: 1px solid rgba(129,140,248,0.2) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(129,140,248,0.5) !important;
    box-shadow: 0 0 0 3px rgba(129,140,248,0.1) !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1rem 0 !important;
}

/* Bar chart text */
div[data-testid="stVegaLiteChart"] text {
    fill: var(--text-muted) !important;
}

/* Code blocks */
div[data-testid="stCode"] > div {
    background: rgba(8,14,26,0.95) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
code {
    font-family: var(--font-mono) !important;
    font-size: 0.88em !important;
}

/* Download button */
.stDownloadButton > button {
    background: rgba(15,24,41,0.9) !important;
    border: 1px solid rgba(52,211,153,0.3) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--accent-green) !important;
    font-weight: 600 !important;
    transition: var(--transition) !important;
}
.stDownloadButton > button:hover {
    background: rgba(52,211,153,0.08) !important;
    border-color: rgba(52,211,153,0.5) !important;
    box-shadow: 0 0 12px rgba(52,211,153,0.15) !important;
    transform: translateY(-1px) !important;
}

/* Spinner */
div[data-testid="stSpinner"] > div {
    border-color: rgba(129,140,248,0.15) !important;
    border-top-color: var(--accent-indigo) !important;
}

/* Toast notifications */
div[data-testid="stToast"] {
    background: rgba(15,24,41,0.95) !important;
    border: 1px solid rgba(129,140,248,0.2) !important;
    border-radius: var(--radius-md) !important;
    backdrop-filter: blur(12px) !important;
    box-shadow: var(--shadow-lg) !important;
}

/* Caption text */
small[data-testid="stCaptionContainer"],
.stCaption {
    color: var(--text-muted) !important;
    font-size: 0.82rem !important;
}

/* Column layout spacing */
div[data-testid="column"] {
    padding: 0 0.35rem !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {
    padding-left: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
    padding-right: 0 !important;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  PAGE HEADINGS                                                      */
/* ═══════════════════════════════════════════════════════════════════ */
.stMarkdown h3 {
    font-size: 1.25rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.01em;
    margin-bottom: 1rem !important;
}
.stMarkdown h4 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    margin-bottom: 0.65rem !important;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  SIDEBAR DIVIDER                                                    */
/* ═══════════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] hr {
    border-top: 1px solid rgba(255,255,255,0.05) !important;
    margin: 0.75rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════════ */
/*  VISUAL EXPLAINER / MERMAID DIAGRAMS                               */
/* ═══════════════════════════════════════════════════════════════════ */

/* Iframe container for Mermaid */
iframe[title="st.components.v1.html"] {
    border: none !important;
    border-radius: var(--radius-md) !important;
    background: transparent !important;
}

/* Quick-topic buttons (pill style) */
.stButton > button[data-testid*="qt_"],
.stButton > button[key*="qt_"] {
    background: rgba(15,24,41,0.8) !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    padding: 0.35rem 0.5rem !important;
    border-radius: var(--radius-sm) !important;
}
.stButton > button[data-testid*="qt_"]:hover {
    border-color: rgba(129,140,248,0.5) !important;
    color: var(--accent-indigo) !important;
    background: rgba(129,140,248,0.08) !important;
}

/* Toggle widget */
div[data-testid="stToggle"] label {
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
div[data-testid="stToggle"] [data-checked="true"] {
    background-color: var(--accent-indigo) !important;
}

/* Diagram topic label */
.diagram-label {
    font-weight: 700;
    color: var(--accent-indigo);
    font-size: 1rem;
    margin-bottom: 0.25rem;
}
"""
