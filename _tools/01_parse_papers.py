"""
01_parse_papers.py
Parse all IB Math AA HL past paper PDFs, detect question boundaries,
and output one JSON per paper to _tools/database/papers/.
Run: python 01_parse_papers.py
"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import fitz  # PyMuPDF

PDF_ROOT = Path(r"C:\Users\rober\OneDrive\Desktop\Math AA HL\IB_exams\extracted")
OUT_DIR  = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")

Q_PAT    = re.compile(r'(\d+)\.\s+\[Maximum mark:\s*(\d+)\]')
MS_Q_PAT = re.compile(r'^\s*(\d+)\.\s+[\(\[]', re.MULTILINE)


def parse_meta(stem: str, folder: str) -> dict:
    f = folder.upper()
    if ' M' in f:
        session = 'May'
        m = re.search(r'M(\d{2})$', f)
    else:
        session = 'Nov'
        m = re.search(r'N(\d{2})$', f)
    year = (2000 + int(m.group(1))) if m else 0

    up = stem.upper()
    pm = re.search(r'[_\-\s]P(\d)', up)
    paper = int(pm.group(1)) if pm else 0
    if not paper:
        pm2 = re.search(r'PAPER[_\s]*(\d)', up)
        paper = int(pm2.group(1)) if pm2 else 0

    tz_m = re.search(r'TZ(\d)', up)
    tz = int(tz_m.group(1)) if tz_m else 0

    is_ms = any(x in up for x in ('MARKSCHEME', '-MS', '_MS', 'MARK_SCHEME'))
    if up.endswith('-MS') or '-MS.' in up:
        is_ms = True

    return {'year': year, 'session': session, 'paper': paper, 'tz': tz, 'is_ms': is_ms}


def note_prefix(meta: dict) -> str:
    tz_part = f"-TZ{meta['tz']}" if meta['tz'] else ""
    return f"{meta['year']}-{meta['session']}-P{meta['paper']}{tz_part}-HL"


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


def find_ms_questions(doc) -> list:
    seen = set()
    ms_qs = []
    for pi, page in enumerate(doc):
        text = page.get_text()
        for m in MS_Q_PAT.finditer(text):
            q_num = int(m.group(1))
            if q_num not in seen:
                seen.add(q_num)
                ms_qs.append({'q_num': q_num, 'start_page': pi})
    ms_qs.sort(key=lambda q: (q['start_page'], q['q_num']))
    for i, q in enumerate(ms_qs):
        q['end_page'] = ms_qs[i + 1]['start_page'] - 1 if i + 1 < len(ms_qs) else len(doc) - 1
        q['end_page'] = max(q['end_page'], q['start_page'])
    return ms_qs


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


def process_paper(pdf_path: Path, folder: str) -> dict | None:
    meta = parse_meta(pdf_path.stem, folder)
    if meta['is_ms'] or not meta['year'] or not meta['paper']:
        return None
    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        print(f"  ERROR opening {pdf_path.name}: {e}")
        return None

    questions = find_questions(doc)
    if not questions:
        doc.close()
        print(f"  NO QUESTIONS: {pdf_path.name}")
        return None

    assign_end_pages(questions, len(doc))

    prefix = note_prefix(meta)
    for q in questions:
        q['text'] = extract_q_text(doc, q['start_page'], q['start_y'], q['end_page'])
        q['note_name'] = f"{prefix}-Q{q['q_num']:02d}"

    doc.close()
    return {
        'filename': pdf_path.name,
        'folder': folder,
        'pdf_path': str(pdf_path),
        **meta,
        'note_prefix': prefix,
        'questions': questions,
        'ms_filename': '',
        'ms_questions': [],
    }


def build_ms_lookup(pdf_root: Path) -> dict:
    lookup = {}
    for folder_path in sorted(pdf_root.iterdir()):
        if not folder_path.is_dir():
            continue
        folder = folder_path.name
        for pdf in sorted(folder_path.glob("*.pdf")):
            meta = parse_meta(pdf.stem, folder)
            if meta['is_ms'] and meta['year'] and meta['paper']:
                key = (meta['year'], meta['session'], meta['paper'], meta['tz'])
                lookup[key] = pdf
    return lookup


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ms_lookup = build_ms_lookup(PDF_ROOT)
    print(f"Found {len(ms_lookup)} mark scheme PDFs")

    total_q = 0
    for folder_path in sorted(PDF_ROOT.iterdir()):
        if not folder_path.is_dir():
            continue
        folder = folder_path.name
        for pdf in sorted(folder_path.glob("*.pdf")):
            meta = parse_meta(pdf.stem, folder)
            if meta['is_ms']:
                continue
            result = process_paper(pdf, folder)
            if result is None:
                continue

            # Link MS
            key = (result['year'], result['session'], result['paper'], result['tz'])
            ms_path = ms_lookup.get(key)
            if ms_path:
                result['ms_filename'] = ms_path.name
                result['ms_pdf_path'] = str(ms_path)
                try:
                    ms_doc = fitz.open(str(ms_path))
                    result['ms_questions'] = find_ms_questions(ms_doc)
                    ms_doc.close()
                except Exception as e:
                    print(f"  MS ERROR {ms_path.name}: {e}")
            else:
                print(f"  NO MS for: {result['note_prefix']}")

            out = OUT_DIR / f"{result['note_prefix']}.json"
            out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
            n = len(result['questions'])
            total_q += n
            ms_info = f"+ MS({len(result['ms_questions'])}q)" if result['ms_questions'] else "no MS"
            print(f"  {result['note_prefix']}: {n} questions {ms_info}")

    print(f"\nDone: {total_q} total questions across all papers")


if __name__ == "__main__":
    main()
