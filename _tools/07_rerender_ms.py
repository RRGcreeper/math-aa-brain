"""
07_rerender_ms.py
Re-render ALL mark scheme images for a given topic shard using Section-A-anchored
clip extraction. Overwrites existing PNGs. Does NOT write back to JSON (parallel-safe).
Run with: python 07_rerender_ms.py --topic T1   (or T2/T3/T4/T5/ALL)
JSON sync happens in a separate single-threaded pass after all shards complete.
"""
import argparse, io, json, sys
import fitz
import numpy as np
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VAULT     = Path(r"C:\Users\rober\math-AA-brain")
PAPERS_DB = VAULT / "_tools" / "database" / "papers"
IMG_DIR   = VAULT / "Questions" / "Past Papers" / "images"
DPI = 150


def _scan_for_question(doc, question_number, require_section_a: bool):
    """Shared scan logic. If require_section_a=False, skip Section A gating."""
    strips = []
    section_found = not require_section_a
    question_found = False
    done = False

    for page_num in range(len(doc)):
        if done:
            break
        page = doc[page_num]
        blocks = page.get_text("blocks")

        # Continuation page: question already found — process once at page level
        if question_found:
            end_y = page.rect.height
            for next_block in blocks:
                next_first = next_block[4].strip().split('\n')[0].strip()
                if (next_first.startswith(f"Question {question_number+1}") or
                        next_first == f"{question_number+1}."):
                    end_y = next_block[1]
                    break
            if page.rotation == 90:
                clip = fitz.Rect(page.mediabox.height - end_y, 0,
                                 page.mediabox.height, page.mediabox.width)
            else:
                clip = fitz.Rect(0, 0, page.rect.width, end_y)
            pixmap = page.get_pixmap(clip=clip, dpi=DPI)
            strips.append(Image.open(io.BytesIO(pixmap.tobytes("png"))))
            if end_y < page.rect.height:
                done = True
            continue

        # Block scan: find Section A boundary then question header
        for i, block in enumerate(blocks):
            text = block[4].strip()
            first_line = text.split('\n')[0].strip()
            if not section_found:
                if "section a" in text.lower():
                    section_found = True
                continue
            is_question_header = (
                first_line.startswith(f"Question {question_number}") or
                first_line == f"{question_number}." or
                first_line.startswith(f"{question_number}. ") or
                first_line == f"Q{question_number}" or
                first_line == str(question_number)
            )
            if is_question_header:
                question_found = True
                start_y = block[1]
                end_y = page.rect.height
                for next_block in blocks[i+1:]:
                    next_first = next_block[4].strip().split('\n')[0].strip()
                    if (next_first.startswith(f"Question {question_number+1}") or
                            next_first == f"{question_number+1}." or
                            next_first.startswith(f"{question_number+1}. ") or
                            next_first == str(question_number+1)):
                        end_y = next_block[1]
                        break
                if page.rotation == 90:
                    x0 = page.mediabox.height - end_y
                    x1 = page.mediabox.height - start_y
                    clip = fitz.Rect(x0, 0, x1, page.mediabox.width)
                else:
                    clip = fitz.Rect(0, start_y, page.rect.width, end_y)
                pixmap = page.get_pixmap(clip=clip, dpi=DPI)
                strips.append(Image.open(io.BytesIO(pixmap.tobytes("png"))))
                if end_y < page.rect.height:
                    done = True
                break

    return strips


def extract_ms_for_question(ms_pdf_path, question_number):
    doc = fitz.open(str(ms_pdf_path))
    strips = _scan_for_question(doc, question_number, require_section_a=True)
    # Fallback for P3/papers with no Section A structure
    if not strips:
        doc.seek(0) if hasattr(doc, 'seek') else None
        doc2 = fitz.open(str(ms_pdf_path))
        strips = _scan_for_question(doc2, question_number, require_section_a=False)
        doc2.close()
    doc.close()
    if not strips:
        return None
    if len(strips) == 1:
        final_image = strips[0]
    else:
        total_height = sum(img.height for img in strips)
        combined = Image.new("RGB", (strips[0].width, total_height), "white")
        y_offset = 0
        for strip in strips:
            combined.paste(strip, (0, y_offset))
            y_offset += strip.height
        final_image = combined
    arr = np.array(final_image)
    non_white_rows = np.where(np.any(arr < 240, axis=(1, 2)))[0]
    if len(non_white_rows) > 0:
        crop_height = min(non_white_rows[-1] + 20, arr.shape[0])
        final_image = final_image.crop((0, 0, final_image.width, crop_height))
    return final_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True,
                        help="Topic shard: T1, T2, T3, T4, T5, or ALL")
    args = parser.parse_args()
    topic_filter = args.topic.upper()
    valid = {"T1", "T2", "T3", "T4", "T5", "ALL"}
    if topic_filter not in valid:
        print(f"ERROR: --topic must be one of {valid}")
        sys.exit(1)

    rendered = skipped = 0

    for jf in sorted(PAPERS_DB.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        ms_pdf_path = Path(data.get("ms_pdf_path", ""))

        if not ms_pdf_path.exists():
            continue

        questions = data.get("questions", [])
        if topic_filter != "ALL":
            questions = [q for q in questions if q.get("main_topic") == topic_filter]
        if not questions:
            continue

        print(f"\n{jf.stem} ({topic_filter}): {len(questions)} questions")

        for q in questions:
            q_num = q["q_num"]
            note_name = q["note_name"]
            ms_img_path = IMG_DIR / f"{note_name}-ms.png"

            try:
                img = extract_ms_for_question(ms_pdf_path, q_num)
                if img is None:
                    print(f"  SKIP Q{q_num:02d} ({note_name}): not found after Section A")
                    skipped += 1
                    continue
                img.save(str(ms_img_path))
                print(f"  OK   Q{q_num:02d} ({note_name}): {img.width}x{img.height}")
                rendered += 1
            except Exception as e:
                print(f"  ERR  Q{q_num:02d} ({note_name}): {e}")
                skipped += 1

    print(f"\n✓ {topic_filter}: Rendered={rendered} | Skipped={skipped}")


if __name__ == "__main__":
    main()
