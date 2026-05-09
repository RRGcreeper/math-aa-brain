"""
03_render_questions.py
Render question and mark scheme PNGs from IB Math AA HL past papers.
Uses PyMuPDF with clip rectangles for precise question images.
Saves to Questions/Past Papers/images/.
Run: python 03_render_questions.py [--year YYYY] [--paper N]
"""
import sys, io, json, re, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path
import fitz  # PyMuPDF

PAPERS_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")
IMG_OUT    = Path(r"C:\Users\rober\math-AA-brain\Questions\Past Papers\images")
DPI        = 200

PAGE_MARGIN_TOP    = 55.0   # skip IB header
PAGE_MARGIN_BOTTOM = 40.0   # skip footer / page number
PAGE_WIDTH         = 595.28  # A4


def render_pages(doc, start_page: int, end_page: int,
                 start_y: float = None, end_y: float = None) -> list:
    """
    Render pages [start_page..end_page] and return list of pixmap bytes.
    Applies clip: top margin on first page uses start_y, bottom margin on
    last page uses end_y (if provided), otherwise page margins.
    """
    pixmaps = []
    ph = doc[start_page].rect.height

    for pi in range(start_page, end_page + 1):
        page = doc[pi]
        h = page.rect.height
        w = page.rect.width

        if start_page == end_page:
            y0 = (start_y - 8) if start_y is not None else PAGE_MARGIN_TOP
            y1 = end_y if (end_y is not None and end_y > 0) else (h - PAGE_MARGIN_BOTTOM)
        elif pi == start_page:
            y0 = (start_y - 8) if start_y is not None else PAGE_MARGIN_TOP
            y1 = h - PAGE_MARGIN_BOTTOM
        elif pi == end_page:
            y0 = PAGE_MARGIN_TOP
            y1 = end_y if (end_y is not None and end_y > 0) else (h - PAGE_MARGIN_BOTTOM)
        else:
            y0 = PAGE_MARGIN_TOP
            y1 = h - PAGE_MARGIN_BOTTOM

        y0 = max(0, y0)
        y1 = min(h, max(y1, y0 + 50))

        clip = fitz.Rect(0, y0, w, y1)
        pix = page.get_pixmap(clip=clip, dpi=DPI)
        pixmaps.append(pix)

    return pixmaps


def stitch_pixmaps(pixmaps: list) -> fitz.Pixmap:
    """Vertically stitch multiple pixmaps into one."""
    if len(pixmaps) == 1:
        return pixmaps[0]
    total_h = sum(p.height for p in pixmaps)
    w = max(p.width for p in pixmaps)
    combined = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, w, total_h), False)
    combined.set_rect(combined.irect, (255, 255, 255))  # white background
    y_offset = 0
    for pix in pixmaps:
        combined.copy(pix, fitz.IRect(0, y_offset, pix.width, y_offset + pix.height))
        y_offset += pix.height
    return combined


def render_question(doc, q: dict, out_dir: Path, note_name: str) -> list[str]:
    """Render one question to PNG(s). Returns list of image filenames."""
    start_page = q['start_page']
    end_page   = q['end_page']
    start_y    = q.get('start_y')
    end_y      = q.get('end_y', -1)
    if end_y == -1:
        end_y = None

    pixmaps = render_pages(doc, start_page, end_page, start_y, end_y)
    combined = stitch_pixmaps(pixmaps)

    fname = f"{note_name}.png"
    out_path = out_dir / fname
    if not out_path.exists():
        combined.save(str(out_path))
    return [fname]


def find_ms_q_pages(ms_questions: list, q_num: int) -> tuple[int, int] | None:
    for msq in ms_questions:
        if msq['q_num'] == q_num:
            return msq['start_page'], msq['end_page']
    return None


def render_ms_question(ms_doc, ms_qs: list, q_num: int,
                       out_dir: Path, note_name: str) -> list[str]:
    """Render mark scheme for one question. Returns list of image filenames."""
    pages = find_ms_q_pages(ms_qs, q_num)
    if pages is None:
        return []
    start_page, end_page = pages
    pixmaps = render_pages(ms_doc, start_page, end_page)
    combined = stitch_pixmaps(pixmaps)

    fname = f"{note_name}-ms.png"
    out_path = out_dir / fname
    if not out_path.exists():
        combined.save(str(out_path))
    return [fname]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=0)
    parser.add_argument("--paper", type=int, default=0)
    args = parser.parse_args()

    IMG_OUT.mkdir(parents=True, exist_ok=True)

    jsons = sorted(PAPERS_DIR.glob("*.json"))
    rendered_q = rendered_ms = skipped = errors = 0

    for jf in jsons:
        data = json.loads(jf.read_text(encoding='utf-8'))

        if args.year and data.get('year') != args.year:
            continue
        if args.paper and data.get('paper') != args.paper:
            continue

        pdf_path = Path(data.get('pdf_path', ''))
        if not pdf_path.exists():
            print(f"  MISSING PDF: {pdf_path}")
            errors += 1
            continue

        try:
            doc = fitz.open(str(pdf_path))
        except Exception as e:
            print(f"  ERROR opening {pdf_path.name}: {e}")
            errors += 1
            continue

        ms_doc = None
        ms_qs  = data.get('ms_questions', [])
        ms_pdf = data.get('ms_pdf_path', '')
        if ms_pdf and Path(ms_pdf).exists() and ms_qs:
            try:
                ms_doc = fitz.open(ms_pdf)
            except Exception:
                ms_doc = None

        print(f"  Rendering {jf.stem} ({len(data['questions'])} questions)...")
        changed = False

        for q in data['questions']:
            note_name = q['note_name']

            # Question image
            q_img_key = 'question_images'
            if not q.get(q_img_key) or not all((IMG_OUT / f).exists() for f in q[q_img_key]):
                try:
                    imgs = render_question(doc, q, IMG_OUT, note_name)
                    q[q_img_key] = imgs
                    rendered_q += 1
                    changed = True
                except Exception as e:
                    print(f"    ERROR Q{q['q_num']}: {e}")
                    errors += 1
            else:
                skipped += 1

            # MS image
            ms_img_key = 'ms_images'
            if ms_doc and not q.get(ms_img_key):
                try:
                    ms_imgs = render_ms_question(ms_doc, ms_qs, q['q_num'], IMG_OUT, note_name)
                    q[ms_img_key] = ms_imgs
                    if ms_imgs:
                        rendered_ms += 1
                    changed = True
                except Exception as e:
                    print(f"    MS ERROR Q{q['q_num']}: {e}")

        doc.close()
        if ms_doc:
            ms_doc.close()

        if changed:
            jf.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"\nDone: {rendered_q} question PNGs, {rendered_ms} MS PNGs, "
          f"{skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
