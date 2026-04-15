"""
prompts.py — All AI prompts & system instructions
====================================================
Single source of truth for every prompt used in the platform.
"""

# ── Base context injected into every AI call ────────────────────────
BASE_CONTEXT = (
    "You are an AI Study Assistant for college students "
    "(BCA, BTech, BBA, BSc, BCom, MBA). "
    "Help with programming, CS theory, mathematics, business subjects, "
    "and exam preparation. Be educational, student-friendly, and precise."
)

# ── Mode-specific system prompts ────────────────────────────────────
MODE_PROMPTS: dict[str, str] = {
    "General Study Assistant": (
        "You are a helpful AI Study Assistant for college students. "
        "Answer clearly and concisely with relevant examples. "
        "Use structured formatting when helpful."
    ),
    "Programming Helper": (
        "You are an expert programming tutor for CS students. "
        "Explain concepts with code examples and step-by-step breakdowns. "
        "Mention real-world applications. Always format code in fenced blocks."
    ),
    "Code Debugger": (
        "You are a professional code debugging assistant. "
        "Identify errors systematically, explain WHY the error occurs, "
        "provide corrected code with improvements, and mention best practices."
    ),
    "Quiz Generator": (
        "You are an academic quiz creator for university exams. "
        "Generate MCQs with 4 options each. "
        "Mark the correct answer clearly. Include brief explanations."
    ),
    "Notes Summarizer": (
        "You are an exam preparation specialist. "
        "Convert lengthy notes into structured bullet points. "
        "Highlight key definitions, formulas, and important concepts. "
        "Format for easy revision scanning."
    ),
    "Assignment Writer": (
        "You are an academic assignment assistant. "
        "Structure content with: Title, Introduction, Body (with headings), "
        "Conclusion, References. Use formal academic language. "
        "Target the requested word count."
    ),
    "Study Planner": (
        "You are a study planning expert. "
        "Create realistic day-by-day study schedules. "
        "Balance topics, include revision slots, and add motivational tips."
    ),
    "Exam Prep": (
        "You are an examination paper specialist. "
        "Generate realistic exam papers with MCQ, short answer, and long answer sections. "
        "Match university exam patterns with proper marks distribution."
    ),
}


def build_system_prompt(mode: str) -> str:
    mode_text = MODE_PROMPTS.get(mode, MODE_PROMPTS["General Study Assistant"])
    return f"{BASE_CONTEXT}\n\n{mode_text}"


def build_user_prompt(user_input: str, mode: str) -> str:
    wrappers = {
        "Quiz Generator":    f"Generate MCQs on the following topic:\n\n{user_input}",
        "Notes Summarizer":  f"Summarise the following notes:\n\n{user_input}",
        "Assignment Writer": f"Write a well-structured academic assignment on:\n\n{user_input}",
        "Code Debugger":     f"Debug and explain the following code:\n\n{user_input}",
    }
    return wrappers.get(mode, user_input)


# ── Vision prompt for OCR / Assignment Solver ───────────────────────
VISION_PROMPT = (
    "You are an expert at reading assignment and exam question papers "
    "(printed or handwritten). "
    "Extract ALL the questions from this image exactly as written. "
    "Number each question clearly: Q1., Q2., Q3. etc. "
    "Include sub-parts (a, b, c) if present. "
    "Skip headers like college name, subject, date — only return the questions. "
    "Do NOT answer them."
)

# ── Tool-specific prompt templates ──────────────────────────────────

NOTES_SUMMARY = (
    "Summarise the following academic notes in {length} "
    "using {format} format. "
    "Preserve all key definitions, formulas, and important facts.\n\nNOTES:\n{notes}"
)

ASSIGNMENT_GEN = (
    "Write a {style} on '{topic}' for a {audience} student. "
    "Target length: approximately {words} words. "
    "Structure: Introduction → Main Body (with subheadings) → Conclusion → References. "
    "Use formal academic English. Include relevant examples and data where applicable."
)

ASSIGNMENT_CHECK = (
    "Review the following student assignment and provide constructive feedback.\n\n"
    "Evaluate each criterion on a scale of 1-10:\n"
    "1. Grammar & Spelling\n"
    "2. Sentence Clarity\n"
    "3. Structure & Flow\n"
    "4. Argument Quality\n"
    "5. Academic Tone\n\n"
    "Format your response EXACTLY as:\n"
    "SCORES:\n"
    "Grammar: [1-10]\n"
    "Clarity: [1-10]\n"
    "Structure: [1-10]\n"
    "Argument: [1-10]\n"
    "Tone: [1-10]\n"
    "Overall Grade: [A/B/C/D]\n\n"
    "FEEDBACK:\n"
    "[Detailed constructive feedback with specific improvements]\n\n"
    "ASSIGNMENT:\n{text}"
)

EXAM_PAPER = (
    "Generate a university-style exam paper for: **{subject}**\n"
    "Total Marks: {marks} | Duration: {duration} | Difficulty: {difficulty}\n\n"
    "Format:\n"
    "Section A: MCQs (20% of marks)\n"
    "Section B: Short Answer (30% of marks, 3-4 questions)\n"
    "Section C: Long Answer (50% of marks, 2-3 questions)\n\n"
    "Include marks per question. Write clearly numbered questions."
    "{answer_key}"
)

QUIZ_GEN = (
    "Create a {level}-difficulty quiz on **{topic}** with exactly {num} questions.\n"
    "For each question provide EXACTLY this format:\n\n"
    "Q1. [Question text]\n"
    "A) [option]\n"
    "B) [option]\n"
    "C) [option]\n"
    "D) [option]\n"
    "CORRECT: [A/B/C/D]\n"
    "EXPLANATION: [1-2 sentences]\n\n"
    "Number questions clearly Q1, Q2, Q3, etc."
)

MATH_SOLVE = (
    "Solve the following math problem{topic_note} for a college student:\n\n"
    "{problem}\n\n"
    "{step_instruction}\n"
    "Format each step clearly numbered.\n"
    "State the final answer clearly at the end.\n"
    "{graph_instruction}"
)

FLASHCARD_GEN = (
    "Create {num} flashcards for studying: '{topic}'\n\n"
    "Card type: {card_type}\n\n"
    "Format EXACTLY as:\n"
    "CARD 1\n"
    "Q: [front of card — question/term]\n"
    "A: [back of card — answer/definition]\n\n"
    "CARD 2\n"
    "Q: ...\n"
    "A: ...\n\n"
    "Make the questions specific and the answers concise (1-3 sentences max). "
    "Cover the most important concepts."
)

VIVA_PREP = (
    "Generate {num} {difficulty}-level {viva_type} questions for '{subject}' "
    "along with detailed model answers.\n\n"
    "Format EXACTLY as:\n"
    "Q1: [Question]\n"
    "A1: [Model Answer — 2-4 sentences, clear and academic]\n\n"
    "Q2: ...\nA2: ...\n\n"
    "Include both theoretical and application/scenario questions. "
    "Cover all major sub-topics of {subject}."
)

MOCK_VIVA = (
    "A student was asked this viva question:\n"
    "QUESTION: {question}\n\n"
    "The student answered:\n"
    "STUDENT ANSWER: {student_answer}\n\n"
    "MODEL ANSWER: {model_answer}\n\n"
    "Evaluate the student's answer:\n"
    "1. Score out of 10\n"
    "2. What was good\n"
    "3. What was missing or wrong\n"
    "4. Improved version of the student's answer\n"
    "Be encouraging but honest."
)

FORMULA_SHEET = (
    "Create a comprehensive {sheet_type} for '{subject}'"
    "{exam_note} ({scope}).\n\n"
    "Format it clearly with:\n"
    "- Organised sections/categories\n"
    "- Every important formula/concept with brief explanation\n"
    "- Examples where helpful\n"
    "- Tables where applicable\n\n"
    "Make it exam-ready and easy to scan quickly."
)

CODE_DEBUG = (
    "Debug this code:\n```\n{code}\n```\n"
    "{error_note}\n"
    "Provide: (1) Root cause, (2) Fixed code, (3) Explanation."
)

CODE_EXPLAIN = (
    "Explain this code line by line for a student:\n```\n{code}\n```\n"
    "Cover: purpose, logic flow, data structures, time/space complexity."
)

CODE_OPTIMISE = (
    "Analyse and optimise this code:\n```\n{code}\n```\n"
    "Provide: (1) Issues found, (2) Optimised version, (3) Big-O analysis."
)

CODE_WRITE = (
    "Write clean, well-commented {lang} code for:\n{desc}\n\n"
    "Include: function/class definition, example usage, and a short explanation."
)

CODE_CONVERT = (
    "Convert the following {from_lang} code to {to_lang}. "
    "Keep the same logic and add comments explaining the differences.\n\n"
    "Code:\n```{from_lang_lower}\n{code}\n```"
)

TRANSLATE = {
    "full": "Translate the following academic text to {lang}. Keep all technical terms accurate.\n\nText:\n{text}",
    "simple": "Explain the following concept in simple, easy-to-understand {lang} for a college student:\n\n{text}",
    "terms": "For the following academic text:\n1. List the key technical terms with their {lang} translations\n2. Provide a brief summary in {lang}\n\nText:\n{text}",
    "bilingual": "Provide a bilingual version:\n- Show the original English\n- Then show the {lang} translation\n\nText:\n{text}",
}

STUDY_RECOMMEND = (
    "Create a personalised learning path for a college CS student.\n"
    "Topics already studied: {studied}\n"
    "Focus area: {focus}\n\n"
    "Provide:\n"
    "1. Next 5 topics to learn (with priority order)\n"
    "2. Why each topic matters\n"
    "3. Free resources (YouTube, books, websites)\n"
    "4. Hands-on practice projects\n"
    "5. Estimated time per topic"
)

STUDY_TIPS = (
    "I have {days} days to prepare for an exam covering: {subjects}. "
    "I study {hours} hours per day. "
    "Give me: 1) priority order for topics, 2) one key tip per subject, "
    "3) a revision strategy for the last 3 days."
)

ASSIGNMENT_SOLVER = (
    "Write college assignment answers that sound exactly like a real student wrote them by hand.\n\n"
    "STRICT RULES — follow every single one:\n"
    "1. NO markdown at all — no **, no *, no #, no underscores, no backticks\n"
    "2. NO title line, NO 'Introduction', NO 'Conclusion', NO subject heading\n"
    "3. Do NOT write the student name anywhere\n"
    "4. Start directly with: Ans 1.  (then the answer), then Ans 2. etc.\n"
    "5. Write {style}\n"
    "6. Use simple, clear, slightly informal academic English\n"
    "7. Vary sentence length naturally\n"
    "8. Use plain numbering like 1) 2) 3) for sub-points — no asterisks or dashes\n"
    "9. Plain text only — as if writing in a ruled notebook\n\n"
    "Subject: {subject}\n\n"
    "QUESTIONS:\n{questions}"
)

DIAGRAM_GEN = (
    "Generate a Mermaid diagram for this academic concept.\n"
    "Output ONLY the raw Mermaid code — no explanation, no markdown fences, no backticks, no extra text whatsoever.\n"
    "The very first character of your response must be the start of the Mermaid diagram.\n\n"
    "Rules:\n"
    "1. Pick the best diagram type:\n"
    "   graph TD        → trees, hierarchies, algorithms, flowcharts, OS, networking, DSA\n"
    "   classDiagram    → OOP, inheritance, class relationships, UML\n"
    "   erDiagram       → databases, entity-relationships, schema\n"
    "   sequenceDiagram → protocols, API calls, process communication\n"
    "2. Max 16 nodes — keep it clean and readable\n"
    "3. Node labels must be short: 1-4 words, no special characters except spaces and ()-\n"
    "4. For graph TD — add colors using classDef (valid properties ONLY: fill, stroke, color):\n"
    "   classDef purple fill:#2d1b69,stroke:#818cf8,color:#e2e8f0\n"
    "   classDef blue   fill:#1e3a5f,stroke:#38bdf8,color:#e2e8f0\n"
    "   classDef green  fill:#064e3b,stroke:#34d399,color:#e2e8f0\n"
    "   classDef amber  fill:#451a03,stroke:#fbbf24,color:#e2e8f0\n"
    "   classDef red    fill:#450a0a,stroke:#f87171,color:#e2e8f0\n"
    "   classDef teal   fill:#134e4a,stroke:#2dd4bf,color:#e2e8f0\n"
    "   Assign with: class NodeID purple\n"
    "5. Edges: A --> B  or  A -- label --> B\n"
    "6. Root node = purple, outputs/leaves = green, errors/limits = red, options = amber\n"
    "7. Do NOT use: rx, ry, font-size, stroke-width, or any CSS property except fill/stroke/color\n\n"
    "Concept to visualise: {concept}"
)

WEB_SEARCH_SYNTHESIZE = (
    "Using the following real web search results, answer this question comprehensively "
    "for a college student:\n\nQuestion: {question}\n\n"
    "Web Search Results:\n{context}\n\n"
    "Provide a well-structured answer. Cite sources by title where relevant. "
    "Be accurate and helpful."
)
