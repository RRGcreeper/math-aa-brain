"""
12_classify_vision.py
Vision-based subtopic reclassification for all Math-AA-Brain Past Paper notes.
Processes one image at a time to avoid the 2000px multi-image API limit.
Outputs: _tools/database/vision_classifications.json

Run: python 12_classify_vision.py [--dry-run] [--start N] [--limit N]
"""
import sys, io, json, base64, re, time, argparse
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import anthropic

VAULT      = Path(r"C:\Users\rober\math-AA-brain")
NOTES_DIR  = VAULT / "Questions" / "Past Papers"
IMAGES_DIR = VAULT / "Questions" / "Past Papers" / "images"
OUTPUT     = VAULT / "_tools" / "database" / "vision_classifications.json"

# ── subtopic schema (vault's schema) ──────────────────────────────────────────
SUBTOPICS = {
    "1.1": ("T1", "Number and Algebra",      "Sequences and Series"),
    "1.2": ("T1", "Number and Algebra",      "Exponents and Logarithms"),
    "1.3": ("T1", "Number and Algebra",      "Binomial Theorem"),
    "1.4": ("T1", "Number and Algebra",      "Complex Numbers"),
    "1.5": ("T1", "Number and Algebra",      "Proof and Induction"),
    "2.1": ("T2", "Functions",               "Lines and Quadratics"),
    "2.2": ("T2", "Functions",               "Functions"),
    "2.3": ("T2", "Functions",               "Rational Functions"),
    "2.4": ("T2", "Functions",               "Exponential and Log Functions"),
    "3.1": ("T3", "Geometry and Trigonometry","3D Geometry"),
    "3.2": ("T3", "Geometry and Trigonometry","Trigonometric Ratios"),
    "3.3": ("T3", "Geometry and Trigonometry","Trigonometric Identities"),
    "3.4": ("T3", "Geometry and Trigonometry","Trigonometric Equations"),
    "3.5": ("T3", "Geometry and Trigonometry","Vectors"),
    "3.6": ("T3", "Geometry and Trigonometry","Lines and Planes"),
    "4.1": ("T4", "Statistics and Probability","Descriptive Statistics"),
    "4.2": ("T4", "Statistics and Probability","Probability"),
    "4.3": ("T4", "Statistics and Probability","Discrete Distributions"),
    "4.4": ("T4", "Statistics and Probability","Normal Distribution"),
    "4.5": ("T4", "Statistics and Probability","Correlation and Regression"),
    "5.1": ("T5", "Calculus",                "Differentiation"),
    "5.2": ("T5", "Calculus",                "Integration"),
    "5.3": ("T5", "Calculus",                "Differential Equations"),
    "5.4": ("T5", "Calculus",                "Maclaurin Series"),
    "5.5": ("T5", "Calculus",                "Kinematics"),
}

CLASSIFICATION_PROMPT = """You are classifying an IB Mathematics Analysis and Approaches HL exam question into its correct subtopic.

Look at the question image carefully and identify the PRIMARY mathematical topic being tested.

Choose EXACTLY ONE code from this list:
1.1 - Sequences and Series (arithmetic/geometric sequences, sigma notation, sum to infinity, nth term, common difference/ratio)
1.2 - Exponents and Logarithms (log equations, ln, laws of logarithms, change of base, exponential equations)
1.3 - Binomial Theorem (binomial expansion, Pascal's triangle, nCr, binomial coefficients, (a+b)^n)
1.4 - Complex Numbers (imaginary numbers, i, modulus, argument, Argand diagram, polar form, De Moivre's theorem, e^(iθ))
1.5 - Proof and Induction (proof by induction, mathematical induction, prove that, show that using induction)
2.1 - Lines and Quadratics (linear equations, gradient, y-intercept, quadratic, discriminant, vertex, completing the square)
2.2 - Functions (domain, range, inverse function, composite function, transformations, reflections, translations, stretches)
2.3 - Rational Functions (rational function, asymptotes, hyperbola, partial fractions)
2.4 - Exponential and Log Functions (exponential growth/decay, e^x, natural logarithm, doubling time, half-life, modelling)
3.1 - 3D Geometry (volume, surface area, sphere, cone, cylinder, pyramid, prism, cross-section, 3D shapes)
3.2 - Trigonometric Ratios (sine rule, cosine rule, SOHCAHTOA, right-angled triangle, bearing, area = ½ab sinC, arc length, sector area)
3.3 - Trigonometric Identities (Pythagorean identity, double angle formula, compound angle, sin²+cos²=1, reciprocal trig functions)
3.4 - Trigonometric Equations (solve trig equation, general solution, principal value, period, amplitude, graph of sin/cos/tan)
3.5 - Vectors (vector, scalar/dot product, cross product, magnitude, unit vector, angle between vectors, vector equation of line)
3.6 - Lines and Planes (line in 3D, plane equation, distance from point to plane, intersection of line and plane)
4.1 - Descriptive Statistics (mean, median, mode, quartile, IQR, standard deviation, frequency table, histogram, box plot)
4.2 - Probability (P(A), conditional probability P(A|B), mutually exclusive, independent events, Venn diagram, tree diagram)
4.3 - Discrete Distributions (binomial B(n,p), Poisson, expected value E(X), Var(X), discrete random variable, probability table)
4.4 - Normal Distribution (N(μ,σ²), z-score, standard normal, P(X<x), bell curve, standardisation, inverse normal)
4.5 - Correlation and Regression (regression line, correlation coefficient r, least squares, scatter diagram, line of best fit)
5.1 - Differentiation (derivative, f'(x), dy/dx, chain rule, product rule, quotient rule, implicit differentiation, tangent line, normal line)
5.2 - Integration (integral, antiderivative, indefinite/definite integral, area under curve, integration by parts, substitution, volume of revolution)
5.3 - Differential Equations (dy/dx = f(x)g(y), separable equation, slope field, Euler's method, general/particular solution)
5.4 - Maclaurin Series (Maclaurin series, Taylor series, power series expansion, radius of convergence)
5.5 - Kinematics (velocity, acceleration, displacement, speed, distance, v=ds/dt, a=dv/dt, particle motion, projectile — NOTE: this is physical motion, not just calculus)

IMPORTANT DISAMBIGUATION RULES:
- If the question shows VELOCITY, ACCELERATION, or DISPLACEMENT with physical motion → 5.5 Kinematics
- If the question shows integration or differentiation WITHOUT motion context → 5.1 or 5.2
- If there is an integral AND a motion context → 5.5 Kinematics
- Binomial distribution B(n,p) → 4.3 (NOT 1.3 Binomial Theorem)
- Sector area or arc length (2D circle) → 3.2 (NOT 3.1 3D Geometry)
- Cross product or dot product → 3.5 Vectors
- Maximizing/minimizing with derivatives (optimization) → 5.1 Differentiation

Respond in this EXACT format (JSON, nothing else):
{"code": "X.X", "confidence": 0-100, "reasoning": "one sentence"}"""


def load_note_frontmatter(note_path: Path) -> dict:
    """Extract frontmatter fields from a note file."""
    text = note_path.read_text(encoding="utf-8")
    fm = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


def find_question_images(note_path: Path) -> list[Path]:
    """Find question image embeds (not MS images) in a note, return existing paths."""
    text = note_path.read_text(encoding="utf-8")
    images = []
    for m in re.finditer(r"!\[\[([^\]]+\.png)\]\]", text):
        img_name = m.group(1)
        # Skip mark scheme images
        if "-ms.png" in img_name:
            continue
        # Images live in the images/ subdirectory
        img_path = IMAGES_DIR / img_name
        if img_path.exists():
            images.append(img_path)
    return images


def encode_image(img_path: Path) -> str:
    return base64.standard_b64encode(img_path.read_bytes()).decode("utf-8")


def classify_images(client: anthropic.Anthropic, images: list[Path], note_name: str) -> dict:
    """Send up to 3 images to the API (one message, separate content blocks if small enough)."""
    if not images:
        return {"code": None, "confidence": 0, "reasoning": "no images found"}

    content = [{"type": "text", "text": CLASSIFICATION_PROMPT}]

    # Add each image as a separate content block (max 3 to avoid token limits)
    for img in images[:3]:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": encode_image(img),
            }
        })

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": content}]
        )
        raw = response.content[0].text.strip()
        # Parse JSON response
        result = json.loads(raw)
        return result
    except json.JSONDecodeError:
        # Try to extract JSON from response
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return {"code": None, "confidence": 0, "reasoning": f"parse error: {raw[:100]}"}
    except anthropic.BadRequestError as e:
        # Image too large even for single-image call → try first image only
        if len(images) > 1:
            return classify_images(client, images[:1], note_name)
        return {"code": None, "confidence": 0, "reasoning": f"api error: {str(e)[:100]}"}
    except Exception as e:
        return {"code": None, "confidence": 0, "reasoning": f"error: {str(e)[:100]}"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done, no API calls")
    parser.add_argument("--start", type=int, default=0, help="Skip first N notes")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N notes (0=all)")
    args = parser.parse_args()

    # Load existing results to resume
    results = {}
    if OUTPUT.exists():
        results = json.loads(OUTPUT.read_text(encoding="utf-8"))
        print(f"Resuming: {len(results)} already classified")

    client = anthropic.Anthropic()

    note_files = sorted(NOTES_DIR.glob("*.md"))
    if args.start:
        note_files = note_files[args.start:]
    if args.limit:
        note_files = note_files[:args.limit]

    total = len(note_files)
    skipped = 0
    errors = 0
    processed = 0

    for i, note_path in enumerate(note_files):
        note_name = note_path.stem

        # Skip if already classified
        if note_name in results:
            skipped += 1
            continue

        fm = load_note_frontmatter(note_path)
        current_code = fm.get("subtopic", "").strip('"')
        current_topic = fm.get("topic", "").strip()

        images = find_question_images(note_path)

        if args.dry_run:
            print(f"[{i+1}/{total}] {note_name}: current={current_code}, images={len(images)}")
            continue

        result = classify_images(client, images, note_name)
        new_code = result.get("code")
        confidence = result.get("confidence", 0)
        reasoning = result.get("reasoning", "")

        # Validate code
        if new_code and new_code not in SUBTOPICS:
            new_code = None
            confidence = 0
            reasoning = f"invalid code returned: {new_code}"

        changed = new_code and new_code != current_code and confidence >= 90
        needs_review = confidence < 90

        entry = {
            "note_name": note_name,
            "current_code": current_code,
            "current_topic": current_topic,
            "new_code": new_code,
            "confidence": confidence,
            "reasoning": reasoning,
            "changed": changed,
            "needs_review": needs_review,
            "images_found": len(images),
        }
        results[note_name] = entry

        status = "CHANGE" if changed else ("REVIEW" if needs_review else "OK")
        print(f"[{i+1-skipped}/{total-skipped}] {note_name}: {current_code} → {new_code} ({confidence}%) [{status}] — {reasoning[:60]}")

        processed += 1

        # Save checkpoint every 10 notes
        if processed % 10 == 0:
            OUTPUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  → checkpoint saved ({len(results)} total)")

        # Brief pause to avoid rate limits
        time.sleep(0.3)

    # Final save
    OUTPUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")

    # Summary
    all_entries = list(results.values())
    n_changed   = sum(1 for e in all_entries if e.get("changed"))
    n_review    = sum(1 for e in all_entries if e.get("needs_review"))
    n_no_image  = sum(1 for e in all_entries if e.get("images_found", 0) == 0)

    print(f"\n{'='*60}")
    print(f"Total notes: {len(all_entries)}")
    print(f"Reclassify (≥90% confidence, changed): {n_changed}")
    print(f"Needs review (<90% confidence): {n_review}")
    print(f"No images found: {n_no_image}")
    print(f"Errors: {errors}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
