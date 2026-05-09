"""
10_build_2025_notes.py
Build Obsidian question notes for the 2025 IB Math AA HL May papers.
Reads the 3 JSONs written by 09_parse_2025.py.
Does NOT update paper hub notes (WS4 handles that).
Run: python 10_build_2025_notes.py
"""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

VAULT      = Path(r"C:\Users\rober\math-AA-brain")
PAPERS_DB  = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")
NOTE_DIR   = VAULT / "Questions" / "Past Papers"

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


def sub_to_main(code: str) -> str:
    return "T" + code.split(".")[0]


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def question_note(q: dict, paper_data: dict) -> str:
    code      = q.get('subtopic_code', '5.1')
    main      = q.get('main_topic', sub_to_main(code))
    sub_name  = SUBTOPICS.get(code, code)
    main_name = MAIN_TOPICS.get(main, main)
    css       = q.get('cssclass', CSS_CLASSES.get(main, 'math-algebra'))
    year      = paper_data['year']
    session   = paper_data['session']
    paper     = paper_data['paper']
    tz        = paper_data.get('tz', 0)
    q_num     = q['q_num']
    marks     = q['marks']

    # Image embeds
    q_imgs = q.get('question_images', [])
    if q_imgs:
        img_block = "\n".join(f"![[{img}]]" for img in q_imgs)
    else:
        img_block = "_Image not yet rendered._"

    # MS callout — override: no MS available for 2025
    ms_imgs = q.get('ms_images', [])
    if ms_imgs:
        ms_lines = "\n".join(f"> ![[{img}]]" for img in ms_imgs)
        ms_block = f"\n\n> [!note]- Mark Scheme\n{ms_lines}"
    else:
        ms_block = "\n\n> [!note]- Mark Scheme\n> Mark scheme not yet available."

    tz_tag    = f"tz{tz}" if tz else "tz0"
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


TARGET_JSONS = [
    "2025-May-P1-HL.json",
    "2025-May-P2-HL.json",
    "2025-May-P3-HL.json",
]


def main():
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    count = 0

    for json_name in TARGET_JSONS:
        jf = PAPERS_DB / json_name
        if not jf.exists():
            print(f"MISSING: {jf}")
            continue

        data = json.loads(jf.read_text(encoding='utf-8'))

        for q in data.get('questions', []):
            note_name = q['note_name']
            note_path = NOTE_DIR / f"{note_name}.md"
            write(note_path, question_note(q, data))
            print(f"Written: {note_name}")
            count += 1

    print(f"\u2713 WS3 COMPLETE: {count} notes written")


if __name__ == "__main__":
    main()
