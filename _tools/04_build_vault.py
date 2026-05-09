"""
04_build_vault.py
Build all Obsidian notes for the IB Math AA HL past papers vault:
  - Questions/Past Papers/{note_name}.md  (one per question)
  - Topics/T{N} - {Name}/{sub_code} - {sub_name}.md  (subtopic hub notes)
  - Papers/Paper 1.md, Paper 2.md, Paper 3.md  (paper hub notes)
  - 00 - Dashboard/Dashboard.md  (updated stats)
  - .obsidian/snippets/topic-colors.css
Run: python 04_build_vault.py
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
from collections import defaultdict

VAULT      = Path(r"C:\Users\rober\math-AA-brain")
PAPERS_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")

MAIN_TOPICS = {
    "T1": "Number and Algebra",
    "T2": "Functions",
    "T3": "Geometry and Trigonometry",
    "T4": "Statistics and Probability",
    "T5": "Calculus",
}

SUBTOPICS = {
    "1.1": "Sequences and Series",
    "1.2": "Exponents and Logarithms",
    "1.3": "Binomial Theorem",
    "1.4": "Complex Numbers",
    "1.5": "Proof by Induction",
    "2.1": "Functions and Their Graphs",
    "2.2": "Transformations",
    "2.3": "Rational Functions",
    "2.4": "Exponential and Logarithmic Functions",
    "2.5": "Quadratic Functions",
    "2.6": "Polynomial Functions",
    "3.1": "3D Geometry",
    "3.2": "Trigonometric Ratios and Rules",
    "3.3": "Trigonometric Identities",
    "3.4": "Trigonometric Equations",
    "3.5": "Vectors",
    "3.6": "Lines and Planes",
    "4.1": "Descriptive Statistics",
    "4.2": "Probability",
    "4.3": "Discrete Distributions",
    "4.4": "Binomial Distribution",
    "4.5": "Normal Distribution",
    "4.6": "Hypothesis Testing",
    "4.7": "Continuous Distributions",
    "5.1": "Differentiation",
    "5.2": "Integration",
    "5.3": "Differential Equations",
    "5.4": "Maclaurin Series",
    "5.5": "Kinematics",
}

CSS_CLASSES = {
    "T1": "math-algebra",
    "T2": "math-functions",
    "T3": "math-geometry",
    "T4": "math-stats",
    "T5": "math-calculus",
}

PAPER_CSSCLASS = {1: "math-paper1", 2: "math-paper2", 3: "math-paper3"}


def sub_to_main(code: str) -> str:
    return "T" + code.split(".")[0]


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def question_note(q: dict, paper_data: dict) -> str:
    code   = q.get('subtopic_code', '5.1')
    main   = q.get('main_topic', sub_to_main(code))
    sub_name = SUBTOPICS.get(code, code)
    main_name = MAIN_TOPICS.get(main, main)
    css    = q.get('cssclass', CSS_CLASSES.get(main, 'math-algebra'))
    year   = paper_data['year']
    session = paper_data['session']
    paper  = paper_data['paper']
    tz     = paper_data.get('tz', 0)
    q_num  = q['q_num']
    marks  = q['marks']

    # Image embeds
    q_imgs = q.get('question_images', [])
    if q_imgs:
        img_block = "\n".join(f"![[{img}]]" for img in q_imgs)
    else:
        img_block = "_Image not yet rendered._"

    # MS callout
    ms_imgs = q.get('ms_images', [])
    if ms_imgs:
        ms_lines = "\n".join(f"> ![[{img}]]" for img in ms_imgs)
        ms_block = f"\n\n> [!note]- Mark Scheme\n{ms_lines}"
    else:
        ms_block = ""

    tz_tag = f"tz{tz}" if tz else "tz0"
    paper_link = f"Papers/Paper {paper}"

    sub_css = "subtopic-" + code.replace(".", "-")

    return f"""---
tags: [math-aa, past-paper, {main.lower()}, subtopic-{code}, p{paper}, hl]
cssclasses: [{css}, {sub_css}]
topic: {main}
subtopic: "{code}"
paper_type: P{paper}
year: {year}
session: {session}
timezone: TZ{tz}
level: HL
question_number: {q_num}
marks: {marks}
difficulty:
self_rating:
---

{img_block}{ms_block}

## Linked Concepts
- [[Topics/{main} - {main_name}/{code} - {sub_name}]]
- [[{paper_link}]]
"""


def subtopic_note(code: str, name: str, main: str, main_name: str,
                  question_entries: list[str]) -> str:
    css = CSS_CLASSES.get(main, 'math-algebra')
    q_links = "\n".join(question_entries) if question_entries else "_No questions indexed yet._"

    return f"""---
tags: [math-aa, topic, {main.lower()}, subtopic-{code}]
cssclasses: [{css}]
topic_code: {main}
subtopic_code: "{code}"
---

# {code} — {name}

## Key Concepts
_Add key concepts and formulas here._

## Formulas
See [[Formulas/{main} Formulas]]

## Exercises
_See [[Topics/{main} - {main_name}]] for topic exercise sets._

## IB Exam Questions
{q_links}
"""


def paper_hub_note(paper_num: int, year_groups: dict) -> str:
    css = PAPER_CSSCLASS.get(paper_num, 'math-paper1')
    sections = []
    for year in sorted(year_groups.keys()):
        lines = year_groups[year]
        sections.append(f"## {year}\n" + "\n".join(lines))
    body = "\n\n".join(sections) if sections else "_No questions indexed yet._"

    return f"""---
tags: [math-aa, paper-hub, P{paper_num}]
cssclasses: [{css}]
---

# Paper {paper_num} — All Questions

{body}
"""


def dashboard_note(total_q: int, by_topic: dict, by_paper: dict, by_year: dict) -> str:
    topic_rows = "\n".join(
        f"| {code} — {MAIN_TOPICS[code]} | {by_topic.get(code, 0)} |"
        for code in sorted(MAIN_TOPICS)
    )
    paper_rows = "\n".join(
        f"| Paper {p} | {by_paper.get(p, 0)} |"
        for p in sorted(by_paper)
    )
    year_rows = "\n".join(
        f"| {y} | {by_year[y]} |"
        for y in sorted(by_year)
    )
    return f"""---
type: dashboard
---

# Math AA HL Brain — Dashboard

> IB Math Analysis & Approaches HL — Past Papers Vault

## Statistics

**Total questions indexed:** {total_q}

## By Topic

| Topic | Questions |
|-------|-----------|
{topic_rows}

## By Paper

| Paper | Questions |
|-------|-----------|
{paper_rows}

## By Year

| Year | Questions |
|------|-----------|
{year_rows}

## Navigation

- [[Papers/Paper 1]] · [[Papers/Paper 2]] · [[Papers/Paper 3]]
- [[Topics/T1 - Number and Algebra]] · [[Topics/T2 - Functions]]
- [[Topics/T3 - Geometry and Trigonometry]]
- [[Topics/T4 - Statistics and Probability]] · [[Topics/T5 - Calculus]]
"""


CSS_SNIPPET = """/* ============================================================
   IB Math AA HL Brain — Topic Color Coding
   T1 Algebra=#4A90D9  T2 Functions=#27AE60  T3 Geometry=#E67E22
   T4 Stats=#8E44AD    T5 Calculus=#E74C3C
   Paper1=#F1C40F  Paper2=#1ABC9C  Paper3=#E84393
   ============================================================ */

/* --- Graph view: color nodes by topic tag (t1–t5) --- */
.graph-view.color-fill-tag .tag-t1        { color: #4A90D9; }
.graph-view.color-fill-tag .tag-t2        { color: #27AE60; }
.graph-view.color-fill-tag .tag-t3        { color: #E67E22; }
.graph-view.color-fill-tag .tag-t4        { color: #8E44AD; }
.graph-view.color-fill-tag .tag-t5        { color: #E74C3C; }
.graph-view.color-fill-tag .tag-p1        { color: #F1C40F; }
.graph-view.color-fill-tag .tag-p2        { color: #1ABC9C; }
.graph-view.color-fill-tag .tag-p3        { color: #E84393; }

/* --- Note pane: colored left border + tinted header --- */
.math-algebra   .view-header { border-left: 4px solid #4A90D9; background: rgba(74,144,217,0.06); }
.math-functions .view-header { border-left: 4px solid #27AE60; background: rgba(39,174,96,0.06); }
.math-geometry  .view-header { border-left: 4px solid #E67E22; background: rgba(230,126,34,0.06); }
.math-stats     .view-header { border-left: 4px solid #8E44AD; background: rgba(142,68,173,0.06); }
.math-calculus  .view-header { border-left: 4px solid #E74C3C; background: rgba(231,76,60,0.06); }
.math-paper1    .view-header { border-left: 4px solid #F1C40F; background: rgba(241,196,15,0.06); }
.math-paper2    .view-header { border-left: 4px solid #1ABC9C; background: rgba(26,188,156,0.06); }
.math-paper3    .view-header { border-left: 4px solid #E84393; background: rgba(232,67,147,0.06); }

/* --- Reading view: subtle background tint --- */
.math-algebra   .markdown-preview-view { background: rgba(74,144,217,0.03); }
.math-functions .markdown-preview-view { background: rgba(39,174,96,0.03); }
.math-geometry  .markdown-preview-view { background: rgba(230,126,34,0.03); }
.math-stats     .markdown-preview-view { background: rgba(142,68,173,0.03); }
.math-calculus  .markdown-preview-view { background: rgba(231,76,60,0.03); }
.math-paper1    .markdown-preview-view { background: rgba(241,196,15,0.03); }
.math-paper2    .markdown-preview-view { background: rgba(26,188,156,0.03); }
.math-paper3    .markdown-preview-view { background: rgba(232,67,147,0.03); }

/* --- Tag pills: color the topic tag by value --- */
a.tag[href="#t1"], .tag[data-tag="t1"] { background: rgba(74,144,217,0.2)  !important; color: #4A90D9 !important; }
a.tag[href="#t2"], .tag[data-tag="t2"] { background: rgba(39,174,96,0.2)   !important; color: #27AE60 !important; }
a.tag[href="#t3"], .tag[data-tag="t3"] { background: rgba(230,126,34,0.2)  !important; color: #E67E22 !important; }
a.tag[href="#t4"], .tag[data-tag="t4"] { background: rgba(142,68,173,0.2)  !important; color: #8E44AD !important; }
a.tag[href="#t5"], .tag[data-tag="t5"] { background: rgba(231,76,60,0.2)   !important; color: #E74C3C !important; }
a.tag[href="#p1"], .tag[data-tag="p1"] { background: rgba(241,196,15,0.2)  !important; color: #c9a800 !important; }
a.tag[href="#p2"], .tag[data-tag="p2"] { background: rgba(26,188,156,0.2)  !important; color: #1ABC9C !important; }
a.tag[href="#p3"], .tag[data-tag="p3"] { background: rgba(232,67,147,0.2)  !important; color: #E84393 !important; }

/* --- Source/Live preview view: left border accent --- */
.math-algebra   .cm-editor { border-left: 4px solid #4A90D9; }
.math-functions .cm-editor { border-left: 4px solid #27AE60; }
.math-geometry  .cm-editor { border-left: 4px solid #E67E22; }
.math-stats     .cm-editor { border-left: 4px solid #8E44AD; }
.math-calculus  .cm-editor { border-left: 4px solid #E74C3C; }
"""


def main():
    jsons = sorted(PAPERS_DIR.glob("*.json"))
    if not jsons:
        print(f"No JSONs in {PAPERS_DIR}")
        return

    # Accumulators
    subtopic_questions: dict[str, list[str]] = defaultdict(list)  # code → [link lines]
    paper_questions: dict[int, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    by_topic: dict[str, int]  = defaultdict(int)
    by_paper: dict[int, int]  = defaultdict(int)
    by_year:  dict[int, int]  = defaultdict(int)
    total_q = 0

    for jf in jsons:
        data = json.loads(jf.read_text(encoding='utf-8'))
        year   = data['year']
        session = data['session']
        paper  = data['paper']
        tz     = data.get('tz', 0)

        for q in data.get('questions', []):
            note_name = q['note_name']
            code      = q.get('subtopic_code', '5.1')
            main      = q.get('main_topic', sub_to_main(code))
            sub_name  = SUBTOPICS.get(code, code)
            marks     = q['marks']
            q_num     = q['q_num']

            # Write question note
            note_path = VAULT / "Questions" / "Past Papers" / f"{note_name}.md"
            write(note_path, question_note(q, data))

            # Accumulate for hub notes
            tz_str   = f" · TZ{tz}" if tz else ""
            link_line = (f"- [[Questions/Past Papers/{note_name}]] — "
                         f"{year} {session} P{paper}{tz_str} Q{q_num} · {marks} marks")
            subtopic_questions[code].append(link_line)
            paper_questions[paper][year].append(
                f"- [[Questions/Past Papers/{note_name}]] — {main} · {marks} marks")

            by_topic[main] += 1
            by_paper[paper] += 1
            by_year[year]   += 1
            total_q += 1

    print(f"Wrote {total_q} question notes")

    # Write subtopic hub notes
    sub_written = 0
    for code, name in SUBTOPICS.items():
        main      = sub_to_main(code)
        main_name = MAIN_TOPICS.get(main, main)
        entries   = sorted(subtopic_questions.get(code, []))
        path = VAULT / "Topics" / f"{main} - {main_name}" / f"{code} - {name}.md"
        write(path, subtopic_note(code, name, main, main_name, entries))
        sub_written += 1
    print(f"Wrote {sub_written} subtopic notes")

    # Write paper hub notes
    for p_num, year_data in paper_questions.items():
        path = VAULT / "Papers" / f"Paper {p_num}.md"
        write(path, paper_hub_note(p_num, year_data))
    print(f"Wrote {len(paper_questions)} paper hub notes")

    # Write main topic hub notes (simple)
    for code, name in MAIN_TOPICS.items():
        subs = sorted(k for k in SUBTOPICS if k.startswith(code[1] + "."))
        sub_links = "\n".join(
            f"- [[Topics/{code} - {name}/{s} - {SUBTOPICS[s]}]]"
            for s in subs
        )
        css = CSS_CLASSES.get(code, 'math-algebra')
        content = f"""---
tags: [math-aa, main-topic, {code.lower()}]
cssclasses: [{css}]
topic_code: {code}
topic_name: {name}
---

# {code} — {name}

> [!info] IB Math AA HL — Main Topic

## Subtopics

{sub_links}
"""
        path = VAULT / "Topics" / f"{code} - {name}.md"
        write(path, content)
    print(f"Wrote {len(MAIN_TOPICS)} main topic notes")

    # Dashboard
    write(VAULT / "00 - Dashboard" / "Dashboard.md",
          dashboard_note(total_q, by_topic, by_paper, by_year))
    print("Wrote Dashboard")

    print(f"\nBuild complete: {total_q} questions · {sub_written} subtopics")


if __name__ == "__main__":
    main()
