"""
02_classify_topics.py
Classify each question in the parsed paper JSONs to a subtopic.
Uses keyword scoring. Updates JSONs in-place.
Run: python 02_classify_topics.py
"""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

PAPERS_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\papers")

MAIN_TOPICS = {
    "T1": "Number and Algebra",
    "T2": "Functions",
    "T3": "Geometry and Trigonometry",
    "T4": "Statistics and Probability",
    "T5": "Calculus",
}

SUBTOPICS = {
    "1.1": "Sequences and Series",
    "1.2": "Exponents and Logarithms",
    "1.3": "Binomial Theorem",
    "1.4": "Complex Numbers",
    "1.5": "Proof by Induction",
    "2.1": "Functions and Their Graphs",
    "2.2": "Transformations",
    "2.3": "Rational Functions",
    "2.4": "Exponential and Logarithmic Functions",
    "2.5": "Quadratic Functions",
    "2.6": "Polynomial Functions",
    "3.1": "3D Geometry",
    "3.2": "Trigonometric Ratios and Rules",
    "3.3": "Trigonometric Identities",
    "3.4": "Trigonometric Equations",
    "3.5": "Vectors",
    "3.6": "Lines and Planes",
    "4.1": "Descriptive Statistics",
    "4.2": "Probability",
    "4.3": "Discrete Distributions",
    "4.4": "Binomial Distribution",
    "4.5": "Normal Distribution",
    "4.6": "Hypothesis Testing",
    "4.7": "Continuous Distributions",
    "5.1": "Differentiation",
    "5.2": "Integration",
    "5.3": "Differential Equations",
    "5.4": "Maclaurin Series",
    "5.5": "Kinematics",
}

# keyword lists: (subtopic_code, [keywords...])
KEYWORD_MAP = [
    ("1.1", ["arithmetic sequence", "geometric sequence", "common difference", "common ratio",
             "sum to infinity", "sigma notation", "series", "nth term", "convergent", "divergent",
             "arithmetic progression", "geometric progression", "sigma", "sum of"]),
    ("1.2", ["logarithm", "log_", "log(", "ln(", "exponential equation", "laws of logarithm",
             "change of base", "log base", "natural log"]),
    ("1.3", ["binomial theorem", "binomial expansion", "pascal", "coefficient of x",
             "expand.*binomial", r"\bC\b.*choose", "combination", "nCr", r"\bC_"]),
    ("1.4", ["complex number", "imaginary", "real part", "im(", "re(", "argand",
             "de moivre", "modulus", "argument", r"\bi\b", "z =", r"\|z\|",
             "polar form", "euler", "conjugate", r"z\^n"]),
    ("1.5", ["proof by induction", "mathematical induction", "inductive step",
             "basis step", "assume true", "p(k)", "p(k+1)", "divisibility"]),
    ("2.1", ["domain", "range", "composite", "f(x)", "g(x)", "inverse function",
             "one-to-one", "bijection", "function defined", "evaluate f",
             "f ∘ g", "f composed"]),
    ("2.2", ["transformation", "translation", "reflection", "stretch", "dilation",
             "horizontal shift", "vertical shift", "f(x + a)", "f(x) + a"]),
    ("2.3", ["rational function", "partial fraction", "oblique asymptote",
             r"p\(x\)/q\(x\)", "rational expression"]),
    ("2.4", ["exponential function", "logarithmic function", "growth", "decay",
             "half.life", "doubling time", "a·b^x", "e^x", "exponential model"]),
    ("2.5", ["quadratic", "parabola", "vertex", "discriminant", "completing the square",
             "ax^2", "quadratic formula", "roots of the quadratic"]),
    ("2.6", ["polynomial", "degree n", "factor theorem", "remainder theorem",
             "roots of polynomial", "cubic", "quartic", "polynomial equation"]),
    ("3.1", ["sphere", "cylinder", "cone", "prism", "pyramid", "surface area",
             "volume of", "3d shape", "cuboid", "solid of"]),
    ("3.2", ["sine rule", "cosine rule", "area of triangle", "bearing",
             r"\bsin\b", r"\bcos\b", r"\btan\b", "right angle", "adjacent", "opposite",
             "hypotenuse", "SOHCAHTOA", "angle of elevation", "angle of depression"]),
    ("3.3", ["identity", "double angle", "half angle", "compound angle",
             "sin(a+b)", "cos(a+b)", "tan(a+b)", "pythagorean identity",
             r"sin\^2", r"cos\^2", "1 - cos", "trig identity"]),
    ("3.4", ["trigonometric equation", "general solution", "solve for theta",
             "sin(x) =", "cos(x) =", "tan(x) =", "principal value"]),
    ("3.5", ["vector", "dot product", "scalar product", "cross product",
             "magnitude of", "unit vector", "position vector", "displacement vector",
             r"\bv =\b", "i + j + k", "column vector", "parallel vector",
             "perpendicular vector"]),
    ("3.6", ["line L", "plane π", "plane equation", "normal to plane", "equation of line",
             "intersection of", "angle between lines", "angle between planes",
             "cartesian equation", "parametric equation", "skew lines", "coplanar"]),
    ("4.1", ["mean", "median", "mode", "quartile", "interquartile range", "iqr",
             "standard deviation", "variance", "frequency table", "histogram",
             "box plot", "cumulative frequency", "outlier", "range of data"]),
    ("4.2", ["probability", "event A", "P(A)", "P(B)", "conditional probability",
             "independent events", "mutually exclusive", "bayes", "tree diagram",
             "venn diagram", "sample space", "P(A|B)", "P(A∩B)", "P(A∪B)"]),
    ("4.3", ["discrete random variable", "probability distribution", "expected value",
             "E(X)", "Var(X)", "probability mass function", "pmf"]),
    ("4.4", ["binomial distribution", "B(n,p)", "bernoulli", "number of successes",
             "X ~ B", "binomial probability"]),
    ("4.5", ["normal distribution", "N(μ,σ)", "standard normal", "z-score",
             "bell curve", "X ~ N", "normal probability", "Φ(", "phi("]),
    ("4.6", ["hypothesis test", "null hypothesis", "H_0", "H0 :", "p-value",
             "significance level", "t-test", "critical region", "type I", "type II",
             "chi-squared test", "chi squared", "goodness of fit", "contingency"]),
    ("4.7", ["continuous random variable", "probability density function", "pdf",
             "cumulative distribution", "cdf", "F(x)", "∫f(x)"]),
    ("5.1", ["derivative", "differentiation", "dy/dx", "f'(x)", "gradient of tangent",
             "rate of change", "tangent line", "normal line", "first derivative",
             "second derivative", "stationary point"]),
    ("5.2", ["integral", "integration", "antiderivative", "∫", "indefinite integral",
             "definite integral", "area under", "area between", "volume of revolution",
             "trapezoid rule"]),
    ("5.3", ["differential equation", "dy/dx =", "separable", "dP/dt",
             "general solution", "particular solution", "slope field", "dv/dt"]),
    ("5.4", ["maclaurin", "taylor series", "maclaurin series", "power series",
             "series expansion", "nth term of series", "coefficient of x^n"]),
    ("5.5", ["velocity", "acceleration", "displacement", "kinematics",
             "particle", "s(t)", "v(t)", "a(t)", "at rest", "speed"]),
]


def subtopic_to_main(code: str) -> str:
    return "T" + code.split(".")[0]


def classify(text: str) -> tuple[str, str]:
    """Return (subtopic_code, main_topic_code) for a question text."""
    low = text.lower()
    scores = {}
    for code, keywords in KEYWORD_MAP:
        score = 0
        for kw in keywords:
            try:
                if re.search(kw, low):
                    score += 1
            except re.error:
                if kw.lower() in low:
                    score += 1
        if score:
            scores[code] = score

    if not scores:
        return "5.1", "T5"  # default to differentiation (most common P3)

    best = max(scores, key=lambda c: scores[c])
    return best, subtopic_to_main(best)


def cssclass(main_code: str) -> str:
    return {
        "T1": "math-algebra",
        "T2": "math-functions",
        "T3": "math-geometry",
        "T4": "math-stats",
        "T5": "math-calculus",
    }.get(main_code, "math-algebra")


def main():
    jsons = sorted(PAPERS_DIR.glob("*.json"))
    if not jsons:
        print(f"No JSONs in {PAPERS_DIR}")
        return

    for jf in jsons:
        data = json.loads(jf.read_text(encoding='utf-8'))
        changed = False
        for q in data.get('questions', []):
            if not q.get('subtopic_code'):
                sub, main = classify(q.get('text', ''))
                q['subtopic_code'] = sub
                q['main_topic']    = main
                q['cssclass']      = cssclass(main)
                changed = True
        if changed:
            jf.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

        counts = {}
        for q in data['questions']:
            c = q.get('subtopic_code', '?')
            counts[c] = counts.get(c, 0) + 1
        dist = ', '.join(f"{c}:{n}" for c, n in sorted(counts.items()))
        print(f"  {jf.stem}: {dist}")

    print(f"\nClassified {len(jsons)} papers")


if __name__ == "__main__":
    main()
