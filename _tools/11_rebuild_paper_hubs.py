"""
11_rebuild_paper_hubs.py
Rebuild Papers/Paper 1.md, Paper 2.md, Paper 3.md with Year -> TZ subheading structure.
Reads from the papers JSON database to build accurate question lists.
"""
import json, sys, io
from pathlib import Path
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VAULT     = Path(r"C:\Users\rober\math-AA-brain")
PAPERS_DB = VAULT / "_tools" / "database" / "papers"
PAPERS_DIR = VAULT / "Papers"


def load_all_papers():
    """Return dict: {paper_num: [(year, session, tz, [q_dict, ...])]}, sorted."""
    papers = defaultdict(list)
    for jf in sorted(PAPERS_DB.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        p_num = data.get("paper")
        if p_num is None:
            continue
        year    = data.get("year")
        session = data.get("session", "May")
        tz      = data.get("tz", 0)
        qs      = data.get("questions", [])
        papers[p_num].append((year, session, tz, qs))

    # Sort each paper's entries: year asc, then May before Nov, then TZ asc
    session_order = {"May": 0, "Nov": 1}
    for p in papers:
        papers[p].sort(key=lambda x: (x[0], session_order.get(x[1], 2), x[2]))
    return papers


def tz_label(session, tz):
    if tz == 0:
        return session  # "May" or "Nov" with no TZ suffix
    return f"{session} · TZ{tz}"


def ms_note(year):
    return " *(mark scheme not yet available)*" if year == 2025 else ""


def build_hub(paper_num, entries):
    """Build markdown content for one hub note."""
    lines = [
        f"---",
        f"tags: [math-aa, paper-hub, P{paper_num}]",
        f"cssclasses: [math-paper{paper_num}]",
        f"---",
        f"",
        f"# Paper {paper_num} — All Questions",
        f"",
    ]

    # Group by year
    by_year = defaultdict(list)
    for year, session, tz, qs in entries:
        by_year[year].append((session, tz, qs))

    for year in sorted(by_year.keys()):
        lines.append(f"## {year}")
        for session, tz, qs in by_year[year]:
            label = tz_label(session, tz)
            lines.append(f"")
            lines.append(f"### {label}{ms_note(year)}")
            for q in qs:
                nn    = q["note_name"]
                main  = q.get("main_topic", "T1")
                marks = q.get("marks", 0)
                lines.append(f"- [[Questions/Past Papers/{nn}]] — {main} · {marks} marks")
        lines.append("")

    return "\n".join(lines)


def main():
    papers = load_all_papers()
    PAPERS_DIR.mkdir(parents=True, exist_ok=True)

    for p_num in sorted(papers.keys()):
        content = build_hub(p_num, papers[p_num])
        out = PAPERS_DIR / f"Paper {p_num}.md"
        out.write_text(content, encoding="utf-8")
        total_q = sum(len(qs) for _, _, _, qs in papers[p_num])
        print(f"Written: Paper {p_num}.md ({len(papers[p_num])} exam sets, {total_q} questions)")

    print("\n✓ WS4 COMPLETE")


if __name__ == "__main__":
    main()
