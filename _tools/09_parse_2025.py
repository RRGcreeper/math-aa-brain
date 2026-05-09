"""
09_parse_2025.py
Parse the 2025 IB Math AA HL May papers (no mark schemes, no TZ variants).
Writes 3 JSONs to _tools/database/papers/.
Run: python 09_parse_2025.py
"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import fitz  # PyMuPDF

OUT_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")

PDFS = [
    (Path(r"C:\Users\rober\OneDrive\Desktop\Math AA HL\IB_exams\extracted\AA HL M25\AA HL May 25 Paper 1.pdf"), 1),
    (Path(r"C:\Users\rober\OneDrive\Desktop\Math AA HL\IB_exams\extracted\AA HL M25\AA HL May 25 Paper 2.pdf"), 2),
    (Path(r"C:\Users\rober\OneDrive\Desktop\Math AA HL\IB_exams\extracted\AA HL M25\AA HL May 2025 Paper 3.pdf"), 3),
]

Q_PAT = re.compile(r'(\d+)\.\s+\[Maximum mark:\s*(\d+)\]')


# --- copied verbatim from 01_parse_papers.py ---

def find_questions(doc) -> list:
    questions = []
    for pi, page in enumerate(doc):
        text = page.get_text()
        blocks = page.get_text("blocks")
        for m in Q_PAT.finditer(text):
            q_num, marks = int(m.group(1)), int(m.group(2))
            marker = m.group(0)[:20]
            # Find y-coord by matching block text
            start_y = 50.0
            for b in blocks:
                if marker in b[4]:
                    start_y = float(b[1])
                    break
            questions.append({
                'q_num': q_num, 'marks': marks,
                'start_page': pi, 'start_y': start_y,
                'text': ''
            })
    questions.sort(key=lambda q: (q['start_page'], q['start_y']))
    return questions


def assign_end_pages(questions: list, total_pages: int) -> None:
    for i, q in enumerate(questions):
        if i + 1 < len(questions):
            nq = questions[i + 1]
            if nq['start_page'] == q['start_page']:
                q['end_page'] = q['start_page']
                q['end_y'] = nq['start_y'] - 5
            else:
                q['end_page'] = nq['start_page'] - 1
                q['end_y'] = -1  # use full page bottom
        else:
            q['end_page'] = total_pages - 1
            q['end_y'] = -1


def extract_q_text(doc, start_page: int, start_y: float, end_page: int) -> str:
    chunks = []
    for pi in range(start_page, min(end_page + 1, len(doc))):
        page = doc[pi]
        blocks = page.get_text("blocks")
        for b in blocks:
            if pi == start_page and float(b[1]) < start_y - 5:
                continue
            txt = b[4].replace('\n', ' ').strip()
            if txt and not all(c in '–—-=~*. ' for c in txt):
                chunks.append(txt)
    return ' '.join(chunks)[:4000]

# --- end copied functions ---


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for pdf_path, paper_num in PDFS:
        note_prefix = f"2025-May-P{paper_num}-HL"

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            print(f"ERROR opening {pdf_path.name}: {e}")
            continue

        questions = find_questions(doc)
        if not questions:
            doc.close()
            print(f"NO QUESTIONS found in {pdf_path.name}")
            continue

        assign_end_pages(questions, len(doc))

        for q in questions:
            q['text'] = extract_q_text(doc, q['start_page'], q['start_y'], q['end_page'])
            q['note_name'] = f"{note_prefix}-Q{q['q_num']:02d}"

        doc.close()

        result = {
            'filename': pdf_path.name,
            'folder': 'AA HL M25',
            'pdf_path': str(pdf_path),
            'year': 2025,
            'session': 'May',
            'paper': paper_num,
            'tz': 0,
            'is_ms': False,
            'note_prefix': note_prefix,
            'questions': questions,
            'ms_pdf_path': '',
            'ms_filename': '',
            'ms_questions': [],
        }

        out = OUT_DIR / f"{note_prefix}.json"
        out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"{note_prefix}: {len(questions)} questions")


if __name__ == "__main__":
    main()
