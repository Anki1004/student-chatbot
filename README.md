# 🎓 AI Academic Platform v3.0

A modular, multi-provider AI study companion for college students (BCA, BTech, BBA, BSc, BCom, MBA).  
Built with Streamlit · 23 AI Tools · Live Web Search · Gamification.

---

## 📂 Project Structure

```
AI-Academic-Platform/
├── app.py               ← Main UI, routing, all 23 page functions
├── ai_engine.py         ← 8-tier AI fallback cascade
├── utils.py             ← Offline utilities, parsers, code runner
├── prompts.py           ← All AI prompts (single source of truth)
├── styles.py            ← All CSS (dark theme)
├── requirements.txt     ← Python dependencies
├── secrets.toml.example ← Template for API keys
├── .gitignore
├── .streamlit/
│   └── config.toml      ← Streamlit theme config
└── README.md
```

---

## 🛠️ 23 Tools

| #  | Tool                | Description                                    |
|----|---------------------|------------------------------------------------|
| 1  | 🏠 Home             | Dashboard with quick access + all tools grid   |
| 2  | 🖼️ Image OCR        | AI Vision + Tesseract OCR + AI follow-up       |
| 3  | 📄 PDF Study Chat   | Upload PDF → chat, summarise, quiz from PDF    |
| 4  | 📝 Notes Summarizer | Notes → summary (supports PDF source)          |
| 5  | ✍️ Assignment Gen   | Topic → full assignment with originality mode  |
| 6  | ✓ Assignment Check  | AI feedback with parsed criterion scores       |
| 7  | 📅 Study Planner    | Priority-weighted day-by-day schedule + AI tips|
| 8  | 🧾 Exam Paper Gen   | Subject → realistic exam paper                 |
| 9  | 💻 Code Runner      | Run Python + AI Explain Error button           |
| 10 | 🎓 Study Recommender| AI-first personalised learning paths           |
| 11 | 📝 Study Notepad    | Notes + bookmarks (replaces broken Study Room) |
| 12 | 📊 Dashboard        | Session analytics, tool usage charts, goals    |
| 13 | 💬 AI Chat          | General assistant with suggested prompts       |
| 14 | 🧩 Quiz Generator   | Generate → Take interactive quiz with scoring  |
| 15 | 🐛 Code Helper      | Debug, explain, optimise, write, convert code  |
| 16 | 🧮 Math Solver      | Step-by-step solutions + quick reference       |
| 17 | 📇 Flashcard Maker  | AI flashcards + study mode with shuffle        |
| 18 | 🎤 Viva Prep        | Generate Q&A + Mock Viva with AI feedback      |
| 19 | 📖 Citation Gen     | Programmatic APA/MLA/IEEE citations            |
| 20 | 🌐 Translator       | Academic content translation, side-by-side     |
| 21 | 📐 Formula Sheet    | Generate exam-ready formula sheets             |
| 22 | 🔍 Web Search       | Tavily-powered with 4 search modes             |
| 23 | 📸 Assignment Solver| Photo → AI answers → printable A4 page         |

---

## 🔄 AI Fallback Cascade

```
User request
     │
     ▼
1. NVIDIA NIM (Llama 3.3 / Mistral / Nemotron — round-robin keys)
     │ all fail?
     ▼
2. OpenRouter (3 free models)
     │ all fail?
     ▼
3. Gemini 1.5 Flash (round-robin keys)
     │ fails?
     ▼
4. Claude 3 Haiku
     │ fails?
     ▼
5. Rules Engine (deterministic FAQ for common topics)
     │ no match?
     ▼
6. Safe fallback message (never crashes the app)
```

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd AI-Academic-Platform
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your API keys:

| Provider    | Get key from                        | Required? |
|-------------|-------------------------------------|-----------|
| NVIDIA NIM  | https://build.nvidia.com            | Optional  |
| OpenRouter  | https://openrouter.ai/keys          | Optional  |
| Gemini      | https://aistudio.google.com/apikey  | Optional  |
| Claude      | https://console.anthropic.com       | Optional  |
| Tavily      | https://tavily.com                  | Optional  |

You need **at least one** AI provider key. The app cascades through all configured providers.

### 3. Run

```bash
streamlit run app.py
```

---

## 🚀 Deploy to Streamlit Cloud

1. Push to GitHub (ensure `secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo → select `app.py`
4. Add your API keys in **Settings → Secrets** (paste your `secrets.toml` content)
5. Deploy!

---

## 🔐 Security

- API keys stored only in `.streamlit/secrets.toml` (never committed)
- Code Runner blocks dangerous imports: `os`, `sys`, `subprocess`, `eval`, `exec`, `open()`, `getattr`, `importlib`, etc.
- User inputs are HTML-escaped before rendering
- Errors logged to terminal only — never exposed to users

---

## 📋 What's New in v3.0

| Feature | v2.0 | v3.0 |
|---------|------|------|
| Tool count | Inconsistent (13/17/20/21/22) | Consistent: **23** everywhere |
| Quiz | Text dump only | **Interactive quiz** with scoring |
| Viva Prep | Questions only | **Mock Viva** with AI feedback |
| Assignment Checker | Raw text feedback | **Parsed scores** per criterion |
| Study Planner | Round-robin subjects | **Priority-weighted** (weak/avg/strong) |
| Image OCR | Tesseract only | **AI Vision** (NVIDIA + Gemini) + follow-up |
| Study Room | Fake collaboration | Replaced with **Study Notepad** (honest) |
| PDF Chat | Basic | **Stats** + Summarise + Quiz from PDF |
| Code Runner | Error shows raw stderr | **AI Explain Error** button |
| Flashcards | Basic flip | **Shuffle** + study mode |
| Citations | AI-generated (unreliable) | **Programmatic** APA/MLA/IEEE |
| Translator | Single output | **Side-by-side** comparison |
| AI Chat | Blank start | **Suggested prompts** for new users |
| Home page | Hardcoded quick access | Dynamic + **live AI/Web status** |
| Prompts | Scattered in app.py | **Centralised** in `prompts.py` |
| CSS | Inline everywhere | **Dedicated** `styles.py` module |
| Dead code | `_source_badge()`, etc. | Removed |
| PDF relevance | No stopword filtering | **Stopword-filtered** scoring |
| Code sandbox | Weak blocklist | **Expanded** blocklist |
