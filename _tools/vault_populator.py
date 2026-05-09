import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json
import re
from pathlib import Path

import httpx

BASE    = "https://localhost:27124"
KEY     = "cbf804a679588148efac0b9f91f1e658fa46ec7269eeb62175ccd3ae513d6614"
HEADERS = {"Authorization": f"Bearer {KEY}"}

client = httpx.Client(verify=False, headers=HEADERS, timeout=15)

PARSED_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\parsed")

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

# Derive subtopic → main topic mapping
SUBTOPIC_TO_MAIN = {k: k.split(".")[0] for k in SUBTOPIC_NAMES}


def safe_title(title: str) -> str:
    """Strip characters illegal in Obsidian note filenames."""
    title = re.sub(r'[\\/:*?"<>|#^[\]]', "", title)
    title = re.sub(r'\s+', " ", title).strip()
    return title[:80]


def topic_code_from_hint(topic_hint: str) -> str:
    """Convert a raw topic_hint like '1.3' to 'T1.3'."""
    if not topic_hint:
        return ""
    hint = topic_hint.strip()
    if hint.upper().startswith("T"):
        return hint.upper()
    return "T" + hint


def put_note(vault_path: str, content: str) -> int:
    r = client.put(
        f"{BASE}/vault/{vault_path}",
        content=content.encode("utf-8"),
        headers={**HEADERS, "Content-Type": "text/markdown"},
    )
    return r.status_code


def note_exists(vault_path: str) -> bool:
    r = client.get(f"{BASE}/vault/{vault_path}", headers=HEADERS)
    return r.status_code == 200


def make_exercise_note(data: dict, topic_code: str) -> str:
    topic_name  = SUBTOPIC_NAMES.get(topic_code, topic_code)
    main_code   = SUBTOPIC_TO_MAIN.get(topic_code, topic_code)
    main_name   = MAIN_TOPICS.get(main_code, main_code)
    source      = data.get("source_dir", "christos")
    pages       = data.get("pages", 0)
    is_sol      = data.get("is_solutions", False)
    imgs = data.get("page_images", [])
    text_block = "\n".join(f"![[{img}]]" for img in imgs) or "_Images not yet rendered._"

    source_label = source.capitalize()

    main_note_title   = f"{main_code} - {main_name}"
    sub_note_title    = f"{topic_code} - {topic_name}"

    note = f"""---
topic: {topic_code}
topic_name: {topic_name}
main_topic: {main_code}
source: {source}
is_solutions: {str(is_sol).lower()}
pages: {pages}
---

# {topic_code} — {topic_name}

> [!info] Source
> {source_label} Nikolaidis — Math AA HL Topic Exercises

## Exercises

{text_block}

## See Also
- [[Topics/{main_note_title}]]
- [[Topics/{sub_note_title}]]
"""
    return note


def make_main_topic_note(code: str, name: str, subtopics: list[str]) -> str:
    subtopic_links = "\n".join(
        f"- [[Topics/{st} - {SUBTOPIC_NAMES[st]}]]"
        for st in sorted(subtopics)
        if st in SUBTOPIC_NAMES
    )
    note = f"""---
topic_code: {code}
topic_name: {name}
type: main-topic
---

# {code} — {name}

> [!info] IB Math AA HL — Main Topic

## Subtopics

{subtopic_links}

## Notes
- Use this note as a hub for all {name} material.
"""
    return note


def make_subtopic_note(code: str, name: str, main_code: str, main_name: str) -> str:
    note = f"""---
topic_code: {code}
topic_name: {name}
main_topic: {main_code}
type: subtopic
---

# {code} — {name}

> [!info] IB Math AA HL — Subtopic of [[Topics/{main_code} - {main_name}]]

## Key Concepts

_Add key concepts and formulas here._

## Exercises
- [[Questions/Topic Exercises/{code} - {name}]]

## Weak Areas
- [[Weak Areas/{code} - {name}]]
"""
    return note


def make_dashboard(topic_counts: dict[str, int]) -> str:
    rows = []
    for code in sorted(MAIN_TOPICS):
        name  = MAIN_TOPICS[code]
        count = topic_counts.get(code, 0)
        rows.append(f"| [[Topics/{code} - {name}]] | {count} |")
    table = "\n".join(rows)

    total = sum(topic_counts.values())

    subtopic_links = "\n".join(
        f"- [[Topics/{code} - {name}]]"
        for code, name in sorted(SUBTOPIC_NAMES.items())
    )

    note = f"""---
type: dashboard
---

# Math Brain — Dashboard

> IB Math AA HL study vault

## Topic Overview

| Topic | Exercise Sets |
|-------|--------------|
{table}

**Total exercise sets loaded:** {total}

## All Subtopics

{subtopic_links}
"""
    return note


def main():
    json_files = sorted(PARSED_DIR.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {PARSED_DIR}")
        return

    exercise_created  = 0
    exercise_skipped  = 0
    topic_created     = 0
    topic_skipped     = 0
    subtopic_created  = 0
    subtopic_skipped  = 0

    # Track which main topics have exercise sets, keyed by main_code
    main_topic_counts: dict[str, int] = {k: 0 for k in MAIN_TOPICS}
    # Subtopics seen across exercise files
    seen_subtopics: set[str] = set()

    for jf in json_files:
        data = json.loads(jf.read_text(encoding="utf-8"))

        if data.get("is_solutions", False):
            continue

        topic_hint  = data.get("topic_hint", "")
        topic_code  = topic_code_from_hint(topic_hint)

        # If we can't resolve a subtopic code, skip creating an exercise note
        # but still record we saw the file
        if not topic_code or topic_code not in SUBTOPIC_NAMES:
            # Attempt to match by filename
            stem = jf.stem
            m = re.search(r'[Tt](\d+)\.(\d+)', stem)
            if m:
                topic_code = f"T{m.group(1)}.{m.group(2)}"

        title      = data.get("title", "") or jf.stem
        safe_t     = safe_title(title)
        note_title = f"{topic_code} - {safe_t}" if topic_code else safe_t
        vault_path = f"Questions/Topic Exercises/{note_title}.md"

        if note_exists(vault_path):
            exercise_skipped += 1
        else:
            content = make_exercise_note(data, topic_code)
            status  = put_note(vault_path, content)
            if status in (200, 201, 204):
                exercise_created += 1
            elif status == 409:
                exercise_skipped += 1
            else:
                print(f"  ERROR {status}: {vault_path}")

        if topic_code and topic_code in SUBTOPIC_NAMES:
            seen_subtopics.add(topic_code)
            main_code = SUBTOPIC_TO_MAIN.get(topic_code, "")
            if main_code in main_topic_counts:
                main_topic_counts[main_code] += 1

    # Create main topic notes (T1–T5)
    for code, name in MAIN_TOPICS.items():
        subtopics_for_main = [s for s in SUBTOPIC_NAMES if s.startswith(code + ".")]
        vault_path = f"Topics/{code} - {name}.md"
        if note_exists(vault_path):
            topic_skipped += 1
        else:
            content = make_main_topic_note(code, name, subtopics_for_main)
            status  = put_note(vault_path, content)
            if status in (200, 201, 204):
                topic_created += 1
            elif status == 409:
                topic_skipped += 1
            else:
                print(f"  ERROR {status}: {vault_path}")

    # Create subtopic notes (all defined subtopics, not just seen ones)
    for code, name in SUBTOPIC_NAMES.items():
        main_code = SUBTOPIC_TO_MAIN[code]
        main_name = MAIN_TOPICS.get(main_code, main_code)
        vault_path = f"Topics/{code} - {name}.md"
        if note_exists(vault_path):
            subtopic_skipped += 1
        else:
            content = make_subtopic_note(code, name, main_code, main_name)
            status  = put_note(vault_path, content)
            if status in (200, 201, 204):
                subtopic_created += 1
            elif status == 409:
                subtopic_skipped += 1
            else:
                print(f"  ERROR {status}: {vault_path}")

    # Create dashboard
    dash_path    = "00 - Dashboard/Dashboard.md"
    dash_content = make_dashboard(main_topic_counts)
    put_note(dash_path, dash_content)

    print(
        f"Created {exercise_created} exercise notes, "
        f"{topic_created} topic notes, "
        f"{subtopic_created} subtopic notes"
    )
    if exercise_skipped or topic_skipped or subtopic_skipped:
        print(
            f"Skipped (already existed): {exercise_skipped} exercises, "
            f"{topic_skipped} topics, {subtopic_skipped} subtopics"
        )


if __name__ == "__main__":
    main()
