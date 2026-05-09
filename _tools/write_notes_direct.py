import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json, re
from pathlib import Path

VAULT   = Path(r"C:\Users\rober\math-AA-brain")
PARSED  = Path(r"C:\Users\rober\math-AA-brain\_tools\database\parsed")

MAIN_TOPICS = {
    "T1": "Number and Algebra",
    "T2": "Functions",
    "T3": "Geometry and Trigonometry",
    "T4": "Statistics and Probability",
    "T5": "Calculus",
}

SUBTOPIC_NAMES = {
    "T1.1": "Numbers and Rounding",
    "T1.2": "Sequences and Series",
    "T1.3": "Sigma Notation and Binomial Theorem",
    "T1.4": "Proof by Induction and Complex Numbers",
    "T1.5": "Complex Numbers (Polar Form)",
    "T1.6": "Logarithms and Exponentials",
    "T1.7": "Laws of Logarithms",
    "T1.8": "Counting Principles",
    "T1.9": "Binomial Theorem",
    "T2.1": "Functions Basics",
    "T2.2": "Graphs and Transformations",
    "T2.3": "Rational Functions",
    "T2.4": "Exponential and Logarithmic Functions",
    "T2.5": "Quadratic Functions",
    "T2.6": "Polynomial Functions",
    "T2.7": "Further Rational Functions",
    "T3.1": "3D Geometry",
    "T3.2": "Trigonometric Ratios",
    "T3.3": "Trigonometric Identities",
    "T3.4": "Trigonometric Equations",
    "T3.5": "Radians, Arc Length, Sector Area",
    "T3.6": "Trigonometric Graphs",
    "T3.7": "Inverse Trigonometry",
    "T3.8": "Vectors",
    "T3.9": "Lines and Planes",
    "T3.10": "Complex Numbers (Euler Form)",
    "T4.1": "Descriptive Statistics",
    "T4.2": "Probability",
    "T4.3": "Discrete Probability Distributions",
    "T4.4": "Binomial Distribution",
    "T4.5": "Normal Distribution",
    "T4.6": "Hypothesis Testing",
    "T4.7": "Continuous Probability Distributions",
    "T4.8": "Linear Regression",
    "T4.9": "Chi-Squared Test",
    "T4.10": "Bivariate Statistics",
    "T5.1": "Limits",
    "T5.2": "Differentiation Basics",
    "T5.3": "Differentiation Rules",
    "T5.4": "Implicit Differentiation",
    "T5.5": "Further Differentiation",
    "T5.6": "Integration Basics",
    "T5.7": "Integration by Substitution",
    "T5.8": "Integration by Parts",
    "T5.9": "Definite Integrals",
    "T5.10": "Separable Differential Equations",
    "T5.11": "Further Differential Equations",
    "T5.12": "Kinematics",
    "T5.13": "Maclaurin Series",
    "T5.14": "Further Series",
}

SUBTOPIC_TO_MAIN = {k: k.split(".")[0] for k in SUBTOPIC_NAMES}


def safe_name(s: str) -> str:
    s = re.sub(r'[\\/:*?"<>|#^[\]]', "", s)
    s = re.sub(r'\s+', " ", s).strip()
    return s[:80]


def topic_code_from_hint(hint: str) -> str:
    if not hint:
        return ""
    hint = hint.strip()
    return hint.upper() if hint.upper().startswith("T") else "T" + hint


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def exercise_note(data: dict, code: str, ms_images: list[str] | None = None) -> str:
    name     = SUBTOPIC_NAMES.get(code, code)
    main     = SUBTOPIC_TO_MAIN.get(code, code)
    main_name = MAIN_TOPICS.get(main, main)
    source   = data.get("source_dir", "christos").capitalize()
    pages    = data.get("pages", 0)
    is_sol   = data.get("is_solutions", False)
    imgs     = data.get("page_images", [])
    img_block = "\n".join(f"![[{img}]]" for img in imgs) or "_Images not yet rendered._"
    ms_block = ""
    if ms_images:
        ms_lines = "\n".join(f"> ![[{img}]]" for img in ms_images)
        ms_block = f"\n\n> [!note]- Mark Scheme\n{ms_lines}"
    return f"""---
topic: {code}
topic_name: {name}
main_topic: {main}
source: {data.get("source_dir","christos")}
is_solutions: {str(is_sol).lower()}
pages: {pages}
---

# {code} — {name}

> [!info] Source
> {source} Nikolaidis — Math AA HL Topic Exercises

## Exercises

{img_block}{ms_block}

## See Also
- [[Topics/{main} - {main_name}]]
- [[Topics/{code} - {name}]]
"""


def main_topic_note(code: str, name: str) -> str:
    subs = sorted(k for k in SUBTOPIC_NAMES if k.startswith(code + "."))
    links = "\n".join(f"- [[Topics/{s} - {SUBTOPIC_NAMES[s]}]]" for s in subs)
    return f"""---
topic_code: {code}
topic_name: {name}
type: main-topic
---

# {code} — {name}

> [!info] IB Math AA HL — Main Topic

## Subtopics

{links}
"""


def subtopic_note(code: str, name: str, main: str, main_name: str, exercise_titles: list[str]) -> str:
    ex_links = "\n".join(f"- [[Questions/Topic Exercises/{t}]]" for t in exercise_titles) or "_No exercises found._"
    return f"""---
topic_code: {code}
topic_name: {name}
main_topic: {main}
type: subtopic
---

# {code} — {name}

> [!info] IB Math AA HL — Subtopic of [[Topics/{main} - {main_name}]]

## Key Concepts

_Add key concepts and formulas here._

## Exercises
{ex_links}

## Weak Areas
- [[Weak Areas/{code} - {name}]]
"""


def dashboard(counts: dict) -> str:
    rows = "\n".join(
        f"| [[Topics/{c} - {MAIN_TOPICS[c]}]] | {counts.get(c, 0)} |"
        for c in sorted(MAIN_TOPICS)
    )
    sub_links = "\n".join(
        f"- [[Topics/{c} - {n}]]"
        for c, n in sorted(SUBTOPIC_NAMES.items())
    )
    total = sum(counts.values())
    return f"""---
type: dashboard
---

# Math AA HL Brain — Dashboard

> IB Math AA HL study vault

## Topic Overview

| Topic | Exercise Sets |
|-------|--------------|
{rows}

**Total exercise sets loaded:** {total}

## All Subtopics

{sub_links}
"""


def main():
    json_files = sorted(PARSED.glob("*.json"))
    if not json_files:
        print(f"No JSON in {PARSED}")
        return

    # Build solution-images lookup: exercise_pdf_stem -> [solution page images]
    ms_lookup: dict[str, list[str]] = {}
    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))
        if not data.get("is_solutions", False):
            continue
        sol_stem = Path(data.get("filename", jf.stem)).stem
        ex_stem = re.sub(r'[_-]?solutions?$', '', sol_stem, flags=re.IGNORECASE)
        ms_lookup[ex_stem] = data.get("page_images", [])

    ex_created = sub_created = main_created = 0
    counts: dict[str, int] = {k: 0 for k in MAIN_TOPICS}
    subtopic_exercises: dict[str, list[str]] = {k: [] for k in SUBTOPIC_NAMES}

    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))
        if data.get("is_solutions", False):
            continue

        hint  = data.get("topic_hint", "")
        code  = topic_code_from_hint(hint)
        if not code or code not in SUBTOPIC_NAMES:
            m = re.search(r'[Tt](\d+)\.(\d+)', jf.stem)
            code = f"T{m.group(1)}.{m.group(2)}" if m else ""

        pdf_stem = Path(data.get("filename", jf.stem)).stem
        note_title = f"{code} - {safe_name(pdf_stem)}" if code else safe_name(pdf_stem)
        ms_images = ms_lookup.get(pdf_stem)
        path   = VAULT / "Questions" / "Topic Exercises" / f"{note_title}.md"
        write(path, exercise_note(data, code, ms_images))
        ex_created += 1

        if code and code in SUBTOPIC_NAMES:
            subtopic_exercises[code].append(note_title)
            main = SUBTOPIC_TO_MAIN.get(code, "")
            if main in counts:
                counts[main] += 1

    for code, name in MAIN_TOPICS.items():
        path = VAULT / "Topics" / f"{code} - {name}.md"
        write(path, main_topic_note(code, name))
        main_created += 1

    for code, name in SUBTOPIC_NAMES.items():
        main = SUBTOPIC_TO_MAIN[code]
        main_name = MAIN_TOPICS.get(main, main)
        path = VAULT / "Topics" / f"{code} - {name}.md"
        write(path, subtopic_note(code, name, main, main_name, subtopic_exercises[code]))
        sub_created += 1

    dash_path = VAULT / "00 - Dashboard" / "Dashboard.md"
    write(dash_path, dashboard(counts))

    print(f"Written: {ex_created} exercise notes, {main_created} topic notes, {sub_created} subtopic notes")
    print(f"Dashboard: {dash_path}")


if __name__ == "__main__":
    main()
