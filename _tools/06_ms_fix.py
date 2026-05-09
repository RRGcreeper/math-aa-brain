"""
06_ms_fix.py
Re-render mark scheme images using Section-A-anchored clip extraction.
Only processes questions that currently have no ms_images entry.
Updates JSONs and injects Mark Scheme callout into Obsidian notes.
"""
import io, json, sys
import fitz
import numpy as np
from pathlib import Path
from PIL import Image

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

VAULT     = Path(r"C:\Users\rober\math-AA-brain")
PAPERS_DB = VAULT / "_tools" / "database" / "papers"
IMG_DIR   = VAULT / "Questions" / "Past Papers" / "images"
NOTE_DIR  = VAULT / "Questions" / "Past Papers"
DPI = 150


def _scan_for_question(doc, question_number, require_section_a: bool):
    strips = []
    section_found = not require_section_a
    question_found = False
    done = False

    for page_num in range(len(doc)):
        if done:
            break
        page = doc[page_num]
        blocks = page.get_text("blocks")

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
    if not strips:
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
    # Trim bottom whitespace
    arr = np.array(final_image)
    non_white_rows = np.where(np.any(arr < 240, axis=(1, 2)))[0]
    if len(non_white_rows) > 0:
        crop_height = min(non_white_rows[-1] + 20, arr.shape[0])
        final_image = final_image.crop((0, 0, final_image.width, crop_height))
    return final_image


def update_note_add_ms(note_path: Path, ms_img_name: str) -> bool:
    content = note_path.read_text(encoding="utf-8")
    if "Mark Scheme" in content:
        return False
    ms_block = f'\n> [!note]- Mark Scheme\n> ![[images/{ms_img_name}]]\n'
    if "## Linked Concepts" in content:
        content = content.replace("## Linked Concepts", ms_block + "## Linked Concepts", 1)
    else:
        content += ms_block
    note_path.write_text(content, encoding="utf-8")
    return True


def main():
    fixed = skipped = 0

    for jf in sorted(PAPERS_DB.glob("*.json")):
        data = json.loads(jf.read_text(encoding="utf-8"))
        ms_pdf_path = Path(data.get("ms_pdf_path", ""))

        if not ms_pdf_path.exists():
            print(f"  WARN: MS PDF not found: {ms_pdf_path.name}")
            continue

        needs_fix = [q for q in data.get("questions", []) if not q.get("ms_images")]
        if not needs_fix:
            continue

        print(f"\n{jf.stem}: {len(needs_fix)} missing MS")
        modified = False

        for q in data["questions"]:
            if q.get("ms_images"):
                continue

            q_num = q["q_num"]
            note_name = q["note_name"]
            ms_img_name = f"{note_name}-ms.png"
            ms_img_path = IMG_DIR / ms_img_name

            img = extract_ms_for_question(ms_pdf_path, q_num)
            if img is None:
                print(f"  SKIP Q{q_num:02d} ({note_name}): not found after Section A")
                skipped += 1
                continue

            img.save(str(ms_img_path))
            q["ms_images"] = [ms_img_name]
            modified = True

            note_path = NOTE_DIR / f"{note_name}.md"
            if note_path.exists():
                update_note_add_ms(note_path, ms_img_name)

            print(f"  FIXED Q{q_num:02d} ({note_name})")
            fixed += 1

        if modified:
            jf.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n✓ Fixed: {fixed} | Skipped: {skipped}")


if __name__ == "__main__":
    main()
