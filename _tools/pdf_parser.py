import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json
import re
from pathlib import Path

import fitz  # PyMuPDF

PDF_ROOT   = Path(r"C:\Users\rober\math-brain-pdfs")
OUTPUT_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\parsed")
IMAGE_OUT  = Path(r"C:\Users\rober\math-AA-brain\Questions\Topic Exercises\images")

_SOURCE_DIRS = ("christos", "desktop")

_TOPIC_HINT_RE = re.compile(r'(\d+\.\d+)', re.IGNORECASE)
_EXERCISE_SPLIT_RE = re.compile(r'(?m)^\s*(\d+)\.\s')


def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def extract_title(first_page_text: str) -> str:
    for line in first_page_text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def parse_topic_hint(filename: str) -> str:
    m = _TOPIC_HINT_RE.search(filename)
    return m.group(1) if m else ""


def split_exercises(full_text: str) -> list[dict]:
    segments = _EXERCISE_SPLIT_RE.split(full_text)
    # segments: [preamble, num1, body1, num2, body2, ...]
    exercises = []
    i = 1
    while i < len(segments) - 1:
        num_str = segments[i].strip()
        body    = segments[i + 1]
        try:
            num = int(num_str)
        except ValueError:
            i += 2
            continue
        text = clean_text(body)
        if text:
            exercises.append({"number": num, "text": text})
        i += 2
    return exercises


def render_pages(doc: fitz.Document, pdf_stem: str) -> list[str]:
    IMAGE_OUT.mkdir(parents=True, exist_ok=True)
    names = []
    for i, page in enumerate(doc):
        name = f"{pdf_stem}_p{i+1:03d}.png"
        out = IMAGE_OUT / name
        if not out.exists():
            pix = page.get_pixmap(dpi=150)
            pix.save(str(out))
        names.append(name)
    return names


def parse_pdf(pdf_path: Path, source_dir: str) -> dict:
    doc = fitz.open(str(pdf_path))

    text_by_page = [page.get_text("text") for page in doc]
    pages        = len(text_by_page)
    title        = extract_title(text_by_page[0]) if text_by_page else ""
    full_text    = "\n\n".join(clean_text(t) for t in text_by_page)
    page_images  = render_pages(doc, pdf_path.stem)

    doc.close()

    filename    = pdf_path.name
    topic_hint  = parse_topic_hint(filename)
    is_solutions = bool(re.search(r'solutions', filename, re.IGNORECASE))
    exercises   = split_exercises(full_text)

    return {
        "filename":     filename,
        "source_dir":   source_dir,
        "title":        title,
        "topic_hint":   topic_hint,
        "is_solutions": is_solutions,
        "pages":        pages,
        "text_by_page": [clean_text(t) for t in text_by_page],
        "full_text":    full_text,
        "exercises":    exercises,
        "page_images":  page_images,
    }


def iter_pdfs():
    for src in _SOURCE_DIRS:
        subdir = PDF_ROOT / src
        if not subdir.exists():
            continue
        for pdf_path in sorted(subdir.rglob("*.pdf")):
            yield pdf_path, src


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not PDF_ROOT.exists():
        print(f"PDF root not found: {PDF_ROOT}")
        return

    parsed = 0
    skipped = 0

    for pdf_path, source_dir in iter_pdfs():
        out_file = OUTPUT_DIR / f"{pdf_path.stem}.json"
        if out_file.exists():
            skipped += 1
            continue

        try:
            data = parse_pdf(pdf_path, source_dir)
        except Exception as exc:
            print(f"  ERROR {pdf_path.name}: {exc}")
            continue

        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        parsed += 1

    total = parsed + skipped
    print(f"Parsed {parsed} PDFs → database/parsed/  ({skipped} already existed, {total} total)")


if __name__ == "__main__":
    main()
