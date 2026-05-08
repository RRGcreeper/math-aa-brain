# IB Math AA Brain

A complete Obsidian vault with **4,000+ IB Math AA HL past paper questions** (2014–2025), Christos Nikolaidis practice exams, topic notes, formula booklet, and lecture notes.

No Python. No setup. Just download, add images, and open.

---

## What's inside

| Folder | Contents |
|--------|----------|
| `Questions/Past Papers/` | Question notes — P1, P2, P3, TZ1 + TZ2, 2014–2025 |
| `Questions/Christos-Practice/` | Christos Nikolaidis practice exam questions per subtopic |
| `Topics/` | 5 topic folders (T1–T5) each with subtopic hub notes |
| `Papers/` | Paper 1, Paper 2, Paper 3 hub notes — all questions by year and timezone |
| `Formulas/` | Formula sheets per topic + full IB formula booklet embedded |
| `Notes/Christos-Notes/` | Christos Nikolaidis lecture notes per topic |
| `Weak Areas/` | Auto-updated from low self-ratings |
| `00 - Dashboard.md` | Overview note |

---

## Setup

### Step 1 — Get the vault

**Option A — Download ZIP** (easiest, no git needed):

Click the green **Code** button above → **Download ZIP** → extract the folder anywhere.

**Option B — Clone**:

```
git clone https://github.com/RRGcreeper/math-aa-brain.git
```

---

### Step 2 — Download the question images

Go to the **[Releases page](https://github.com/RRGcreeper/math-aa-brain/releases/latest)** and download **`question-images.zip`**.

Extract it directly into the `math-aa-brain` folder. It will place images into `Questions/Past Papers/` alongside the notes.

> Without this ZIP, question diagrams and mark scheme images will not appear in notes.

---

### Step 3 — (Optional) Download Christos Nikolaidis images

From the same Releases page, download **`christos-images.zip`** and extract it into the `math-aa-brain` folder. It will place images into `Questions/Christos-Practice/` and `Notes/Christos-Notes/`.

---

### Step 4 — Open in Obsidian

1. Open [Obsidian](https://obsidian.md) (free download)
2. Click **Open folder as vault**
3. Select the `math-aa-brain` folder

That's it. No plugins required.

---

## How to use it

**Browse by topic** — open any folder in `Topics/` then open a subtopic note to see all past paper questions and Christos practice questions linked to that subtopic.

**Browse by paper** — open `Papers/Paper 1.md`, `Paper 2.md`, or `Paper 3.md` to see every question from that paper type organized by year and timezone.

**Study a question** — each question note has:
- The question image embedded directly
- A collapsible mark scheme (click to expand)
- A `self_rating` field — fill in 1–5 after attempting it
- Wikilinks to its subtopic and paper hub

**Graph view** — open the graph (left sidebar icon) to see the full topic map. Each topic is color coded:

| Color | Topic |
|-------|-------|
| Blue | T1 — Number and Algebra |
| Green | T2 — Functions |
| Orange | T3 — Geometry and Trigonometry |
| Purple | T4 — Statistics and Probability |
| Red | T5 — Calculus |
| Yellow | Paper 1 |
| Teal | Paper 2 |
| Pink | Paper 3 |

**Search** — use Ctrl+Shift+F to search across all questions by keyword, subtopic code, year, timezone, or paper type.

---

## Folder structure

```
math-aa-brain/
  Questions/
    Past Papers/          <- question notes + images (after ZIP extract)
    Christos-Practice/    <- Christos Nikolaidis practice questions + images
  Topics/
    T1 - Number and Algebra/
      1.1 - Sequences and Series.md
      1.2 - Exponents and Logarithms.md
      ...
    T2 - Functions/
    T3 - Geometry and Trigonometry/
    T4 - Statistics and Probability/
    T5 - Calculus/
  Papers/
    Paper 1.md            <- all P1 questions by year then timezone
    Paper 2.md
    Paper 3.md
  Formulas/
    00-Full-Booklet.md    <- full IB formula booklet embedded
    T1 Formulas.md
    ...
  Notes/
    Christos-Notes/       <- lecture note images per topic
  Weak Areas/
  Templates/
  00 - Dashboard.md
  _tools/                 <- ingestion pipeline scripts (ignore this folder)
```

---

## 2025 papers

2025 exam questions are included. Mark schemes are not yet available and will be added when released.

---

## Issues or questions

Open an issue at [github.com/RRGcreeper/math-aa-brain/issues](https://github.com/RRGcreeper/math-aa-brain/issues).
