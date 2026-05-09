import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import json
from pathlib import Path

PARSED_DIR = Path(r"C:\Users\rober\math-AA-brain\_tools\database\parsed")

TOPIC_NAMES: dict[str, str] = {
    "T1.1":  "Numbers and Rounding",
    "T1.2":  "Sequences and Series",
    "T1.3":  "Sigma Notation and Binomial Theorem",
    "T1.4":  "Proof by Induction and Complex Numbers Basics",
    "T1.5":  "Complex Numbers (Modulus, Argument, Polar Form)",
    "T1.6":  "Partial Fractions, Logs and Exponentials",
    "T1.7":  "Laws of Logarithms",
    "T1.8":  "Counting Principles",
    "T1.9":  "Binomial Theorem Expansion",
    "T2.1":  "Functions (Domain, Range, Inverse, Composite)",
    "T2.2":  "Graphs (Intercepts, Asymptotes, Transformations)",
    "T2.3":  "Rational Functions",
    "T2.4":  "Exponential and Logarithmic Functions",
    "T2.5":  "Quadratic Functions",
    "T2.6":  "Polynomial Functions",
    "T2.7":  "Rational Functions (Further)",
    "T3.1":  "3D Geometry, Distance and Midpoint",
    "T3.2":  "Trig Ratios and Unit Circle",
    "T3.3":  "Trig Identities and Double Angle",
    "T3.4":  "Trig Equations",
    "T3.5":  "Radians, Arc Length and Sector Area",
    "T3.6":  "Trig Functions Graphs",
    "T3.7":  "Inverse Trig",
    "T3.8":  "Vectors (Dot Product, Cross Product)",
    "T3.9":  "Lines and Planes in 3D",
    "T3.10": "Complex Numbers (Euler's Form)",
    "T4.1":  "Statistics (Mean, Median, Mode, SD)",
    "T4.2":  "Probability",
    "T4.3":  "Probability Distributions (Discrete)",
    "T4.4":  "Binomial Distribution",
    "T4.5":  "Normal Distribution",
    "T4.6":  "Hypothesis Testing",
    "T4.7":  "Probability Density Functions",
    "T4.8":  "Linear Regression (Pearson, Spearman)",
    "T4.9":  "Chi-Squared Test",
    "T4.10": "Bivariate Statistics",
    "T5.1":  "Limits",
    "T5.2":  "Differentiation Basics",
    "T5.3":  "Differentiation (Chain, Product, Quotient Rules)",
    "T5.4":  "Implicit Differentiation and Related Rates",
    "T5.5":  "Further Differentiation",
    "T5.6":  "Integration (Antiderivatives)",
    "T5.7":  "Integration Techniques (Substitution)",
    "T5.8":  "Integration by Parts",
    "T5.9":  "Definite Integrals, Areas and Volumes",
    "T5.10": "Differential Equations (Separable)",
    "T5.11": "Differential Equations (Further)",
    "T5.12": "Kinematics",
    "T5.13": "Maclaurin Series",
    "T5.14": "Further Series",
}

MAIN_TOPIC_NAMES: dict[str, str] = {
    "T1": "Number and Algebra",
    "T2": "Functions",
    "T3": "Geometry and Trigonometry",
    "T4": "Statistics and Probability",
    "T5": "Calculus",
}

# Each entry: (topic_code, weight, [keywords])
# Text is lowercased before matching. Score = sum of weights for all hits.
RULES: list[tuple[str, int, list[str]]] = [
    # T1.1 — Numbers and Rounding
    ("T1.1", 10, ["significant figure", "decimal place", "rounding", "scientific notation",
                  "standard form", "percentage error", "approximation", "truncation",
                  "upper bound", "lower bound", "absolute error", "relative error"]),
    ("T1.1", 3,  ["round", "estimate", "accuracy"]),

    # T1.2 — Sequences and Series
    ("T1.2", 10, ["arithmetic sequence", "geometric sequence", "arithmetic series",
                  "geometric series", "common difference", "common ratio",
                  "sum to infinity", "nth term", "first term", "last term",
                  "sum of terms", "convergent series", "divergent series",
                  "geometric progression", "arithmetic progression"]),
    ("T1.2", 5,  ["sequence", "series", "term", "progression"]),

    # T1.3 — Sigma notation and Binomial theorem (basic)
    ("T1.3", 10, ["sigma notation", "summation notation", "binomial theorem",
                  "binomial expansion", "pascal's triangle", "combination", "nCr",
                  "binomial coefficient", "general term"]),
    ("T1.3", 3,  ["sigma", "summation"]),

    # T1.4 — Proof by induction and complex numbers basics
    ("T1.4", 10, ["proof by induction", "mathematical induction", "inductive step",
                  "base case", "inductive hypothesis", "complex number", "imaginary unit",
                  "real part", "imaginary part", "argand diagram", "complex conjugate"]),
    ("T1.4", 5,  ["induction", "imaginary", "complex"]),

    # T1.5 — Complex numbers (modulus, argument, polar form)
    ("T1.5", 10, ["modulus", "argument", "polar form", "modulus-argument form",
                  "de moivre", "de moivre's theorem", "roots of unity",
                  "nth roots", "polar coordinates", "complex plane"]),
    ("T1.5", 5,  ["modulus", "argument", "polar"]),

    # T1.6 — Partial fractions, logs, exponentials
    ("T1.6", 10, ["partial fraction", "partial fractions", "logarithm", "exponential",
                  "natural logarithm", "log base", "change of base", "exponential equation",
                  "logarithmic equation", "ln", "log equation"]),
    ("T1.6", 5,  ["fraction decomposition"]),

    # T1.7 — Laws of logarithms
    ("T1.7", 10, ["law of logarithm", "laws of logarithm", "product rule log",
                  "quotient rule log", "power rule log", "log product", "log quotient",
                  "log power", "logarithmic identity", "change of base formula"]),
    ("T1.7", 3,  ["log rule", "logarithm rule"]),

    # T1.8 — Counting principles (permutations, combinations)
    ("T1.8", 10, ["permutation", "combination", "counting principle",
                  "fundamental counting", "factorial", "arrangements",
                  "selections", "ways to choose", "ways to arrange",
                  "nPr", "ordered selection", "unordered selection"]),
    ("T1.8", 5,  ["arrange", "select", "choose", "ways"]),

    # T1.9 — Binomial theorem expansion
    ("T1.9", 10, ["binomial expansion", "expand", "binomial series",
                  "coefficient of x", "term in x", "binomial approximation",
                  "binomial expression"]),
    ("T1.9", 3,  ["expand", "expansion"]),

    # T2.1 — Functions (domain, range, inverse, composite)
    ("T2.1", 10, ["domain", "range", "inverse function", "composite function",
                  "one-to-one", "onto", "bijection", "function notation",
                  "f inverse", "f(g(x))", "g(f(x))", "composition",
                  "codomain", "surjective", "injective"]),
    ("T2.1", 5,  ["function", "mapping", "inverse", "composite"]),

    # T2.2 — Graphs (intercepts, asymptotes, transformations)
    ("T2.2", 10, ["x-intercept", "y-intercept", "asymptote", "horizontal asymptote",
                  "vertical asymptote", "graph transformation", "translation",
                  "reflection", "stretch", "compression", "dilation",
                  "shift", "intercept"]),
    ("T2.2", 5,  ["graph", "sketch", "plot", "intercept", "asymptote", "transformation"]),

    # T2.3 — Rational functions
    ("T2.3", 10, ["rational function", "oblique asymptote", "slant asymptote",
                  "proper fraction", "improper fraction", "polynomial division",
                  "long division", "holes in graph", "removable discontinuity"]),
    ("T2.3", 5,  ["rational", "denominator", "numerator"]),

    # T2.4 — Exponential and logarithmic functions
    ("T2.4", 10, ["exponential function", "logarithmic function", "exponential growth",
                  "exponential decay", "natural exponential", "e^x", "log function",
                  "exponential model", "half-life model", "doubling time"]),
    ("T2.4", 5,  ["exponential", "logarithmic", "growth", "decay"]),

    # T2.5 — Quadratic functions
    ("T2.5", 10, ["quadratic function", "quadratic equation", "vertex", "axis of symmetry",
                  "discriminant", "completing the square", "quadratic formula",
                  "parabola", "roots of quadratic", "turning point",
                  "maximum value", "minimum value"]),
    ("T2.5", 5,  ["quadratic", "parabola", "vertex"]),

    # T2.6 — Polynomial functions
    ("T2.6", 10, ["polynomial", "degree of polynomial", "leading coefficient",
                  "factor theorem", "remainder theorem", "synthetic division",
                  "roots of polynomial", "zeros of polynomial",
                  "cubic function", "quartic function"]),
    ("T2.6", 5,  ["polynomial", "cubic", "quartic", "root", "zero"]),

    # T2.7 — Rational functions (further)
    ("T2.7", 10, ["partial fraction decomposition", "repeated linear factor",
                  "irreducible quadratic factor", "graph of rational function"]),
    ("T2.7", 3,  ["rational graph"]),

    # T3.1 — 3D geometry, distance, midpoint
    ("T3.1", 10, ["three-dimensional", "3d geometry", "distance formula",
                  "midpoint formula", "coordinate geometry", "distance in 3d",
                  "midpoint in 3d", "three dimensions", "cartesian coordinates 3d",
                  "length of segment"]),
    ("T3.1", 5,  ["distance", "midpoint", "3d", "three-dimensional"]),

    # T3.2 — Trig ratios, unit circle
    ("T3.2", 10, ["sine", "cosine", "tangent", "unit circle", "trigonometric ratio",
                  "soh cah toa", "right-angled triangle", "trigonometry",
                  "cosecant", "secant", "cotangent", "exact value",
                  "special angle", "30 60 90", "45 45 90"]),
    ("T3.2", 5,  ["sin", "cos", "tan", "trig", "angle"]),

    # T3.3 — Trig identities, double angle
    ("T3.3", 10, ["trigonometric identity", "pythagorean identity", "double angle formula",
                  "compound angle formula", "addition formula", "sin(a+b)",
                  "cos(a+b)", "tan(a+b)", "double angle", "half angle",
                  "sum to product", "product to sum", "auxiliary angle"]),
    ("T3.3", 5,  ["identity", "double angle", "compound angle"]),

    # T3.4 — Trig equations
    ("T3.4", 10, ["trigonometric equation", "solve trig", "general solution",
                  "principal value", "trig equation", "solve for angle",
                  "cosine equation", "sine equation", "tangent equation"]),
    ("T3.4", 5,  ["solve", "equation", "general solution"]),

    # T3.5 — Radians, arc length, sector area
    ("T3.5", 10, ["radian", "arc length", "sector area", "angle in radians",
                  "convert to radians", "degrees to radians", "radians to degrees",
                  "arc", "sector", "segment area"]),
    ("T3.5", 5,  ["radian", "arc", "sector"]),

    # T3.6 — Trig functions graphs
    ("T3.6", 10, ["graph of sine", "graph of cosine", "graph of tangent",
                  "sinusoidal", "amplitude", "period", "phase shift",
                  "vertical shift", "frequency", "trig graph"]),
    ("T3.6", 5,  ["amplitude", "period", "phase", "sinusoidal"]),

    # T3.7 — Inverse trig
    ("T3.7", 10, ["inverse sine", "inverse cosine", "inverse tangent",
                  "arcsin", "arccos", "arctan", "arcsine", "arccosine",
                  "arctangent", "inverse trig"]),
    ("T3.7", 5,  ["arcsin", "arccos", "arctan", "inverse trig"]),

    # T3.8 — Vectors (dot product, cross product)
    ("T3.8", 10, ["vector", "dot product", "cross product", "scalar product",
                  "vector product", "magnitude of vector", "unit vector",
                  "position vector", "displacement vector", "angle between vectors",
                  "perpendicular vectors", "parallel vectors", "vector addition",
                  "resultant vector"]),
    ("T3.8", 5,  ["vector", "dot product", "cross product"]),

    # T3.9 — Lines and planes in 3D
    ("T3.9", 10, ["equation of line", "equation of plane", "vector equation",
                  "parametric equation", "cartesian equation of plane",
                  "normal vector", "intersection of lines", "intersection of planes",
                  "angle between planes", "angle between line and plane",
                  "direction vector", "skew lines"]),
    ("T3.9", 5,  ["line", "plane", "normal", "parametric"]),

    # T3.10 — Complex numbers (Euler's form)
    ("T3.10", 10, ["euler's formula", "euler form", "e^(i theta)", "exponential form",
                   "complex exponential", "e^iθ", "cis theta", "cisθ"]),
    ("T3.10", 5,  ["euler", "exponential form", "cis"]),

    # T4.1 — Statistics (mean, median, mode, SD)
    ("T4.1", 10, ["mean", "median", "mode", "standard deviation", "variance",
                  "interquartile range", "iqr", "quartile", "range",
                  "frequency table", "cumulative frequency", "box plot",
                  "box and whisker", "histogram", "stem and leaf",
                  "outlier", "data set", "descriptive statistics"]),
    ("T4.1", 5,  ["mean", "median", "mode", "standard deviation", "statistics"]),

    # T4.2 — Probability
    ("T4.2", 10, ["probability", "event", "sample space", "complement",
                  "mutually exclusive", "independent events", "conditional probability",
                  "venn diagram", "tree diagram", "probability tree",
                  "addition rule", "multiplication rule", "bayes", "p(a|b)",
                  "p(a and b)", "p(a or b)"]),
    ("T4.2", 5,  ["probability", "event", "likelihood", "chance"]),

    # T4.3 — Probability distributions (discrete)
    ("T4.3", 10, ["probability distribution", "discrete distribution",
                  "expected value", "e(x)", "variance of x", "var(x)",
                  "probability mass function", "pmf", "random variable",
                  "discrete random variable"]),
    ("T4.3", 5,  ["distribution", "expected value", "random variable"]),

    # T4.4 — Binomial distribution
    ("T4.4", 10, ["binomial distribution", "b(n,p)", "binomial probability",
                  "number of trials", "probability of success", "binomial random variable",
                  "binomial model", "x ~ b"]),
    ("T4.4", 5,  ["binomial", "trials", "success"]),

    # T4.5 — Normal distribution
    ("T4.5", 10, ["normal distribution", "gaussian", "bell curve", "standardise",
                  "standard normal", "z-score", "z score", "n(mu, sigma)",
                  "normal curve", "normally distributed", "x ~ n"]),
    ("T4.5", 5,  ["normal", "z-score", "standardise"]),

    # T4.6 — Hypothesis testing
    ("T4.6", 10, ["hypothesis test", "null hypothesis", "alternative hypothesis",
                  "p-value", "significance level", "type i error", "type ii error",
                  "critical region", "test statistic", "reject null",
                  "one-tailed", "two-tailed", "level of significance"]),
    ("T4.6", 5,  ["hypothesis", "significance", "p-value"]),

    # T4.7 — Probability density functions, continuous distributions
    ("T4.7", 10, ["probability density function", "pdf", "continuous distribution",
                  "continuous random variable", "cumulative distribution function",
                  "cdf", "f(x) dx", "area under curve probability"]),
    ("T4.7", 5,  ["density function", "continuous"]),

    # T4.8 — Linear regression (Pearson, Spearman)
    ("T4.8", 10, ["linear regression", "regression line", "least squares",
                  "pearson correlation", "spearman correlation", "correlation coefficient",
                  "line of best fit", "scatter diagram", "scatter plot",
                  "y on x", "x on y", "regression equation", "r value"]),
    ("T4.8", 5,  ["regression", "correlation", "scatter"]),

    # T4.9 — Chi-squared test
    ("T4.9", 10, ["chi-squared", "chi squared", "chi-square", "goodness of fit",
                  "contingency table", "observed frequency", "expected frequency",
                  "degrees of freedom", "chi squared test"]),
    ("T4.9", 5,  ["chi", "contingency"]),

    # T4.10 — Bivariate statistics
    ("T4.10", 10, ["bivariate", "bivariate data", "joint distribution",
                   "covariance", "two-variable statistics"]),
    ("T4.10", 3,  ["bivariate"]),

    # T5.1 — Limits
    ("T5.1", 10, ["limit", "approaching", "tends to", "limit as x approaches",
                  "lim", "l'hopital", "l'hôpital", "squeeze theorem",
                  "sandwich theorem", "continuity", "left limit", "right limit",
                  "limit at infinity"]),
    ("T5.1", 5,  ["limit", "approaches", "tends to"]),

    # T5.2 — Differentiation basics
    ("T5.2", 10, ["derivative", "differentiate", "gradient of tangent", "gradient function",
                  "first principles", "limit definition of derivative",
                  "dy/dx", "f'(x)", "tangent line", "normal line",
                  "rate of change", "instantaneous rate"]),
    ("T5.2", 5,  ["derivative", "differentiate", "gradient", "tangent"]),

    # T5.3 — Differentiation (chain, product, quotient rules)
    ("T5.3", 10, ["chain rule", "product rule", "quotient rule",
                  "composite function derivative", "function of a function",
                  "d/dx of product", "d/dx of quotient"]),
    ("T5.3", 5,  ["chain rule", "product rule", "quotient rule"]),

    # T5.4 — Implicit differentiation, related rates
    ("T5.4", 10, ["implicit differentiation", "implicit function", "related rates",
                  "dy/dx implicit", "d/dx implicit", "rate of change related"]),
    ("T5.4", 5,  ["implicit", "related rates"]),

    # T5.5 — Further differentiation
    ("T5.5", 10, ["second derivative", "d2y/dx2", "concavity", "concave up",
                  "concave down", "inflection point", "point of inflection",
                  "higher derivative", "nth derivative"]),
    ("T5.5", 5,  ["second derivative", "inflection", "concavity"]),

    # T5.6 — Integration (antiderivatives)
    ("T5.6", 10, ["antiderivative", "indefinite integral", "integrate", "integration",
                  "constant of integration", "integral of", "primitive function",
                  "reverse differentiation"]),
    ("T5.6", 5,  ["integrate", "integral", "antiderivative"]),

    # T5.7 — Integration techniques (substitution)
    ("T5.7", 10, ["integration by substitution", "u-substitution", "substitution method",
                  "let u =", "change of variable integration"]),
    ("T5.7", 5,  ["substitution", "u-sub"]),

    # T5.8 — Integration by parts
    ("T5.8", 10, ["integration by parts", "ibp", "uv - integral v du",
                  "by parts", "tabular integration"]),
    ("T5.8", 5,  ["by parts", "integration by parts"]),

    # T5.9 — Definite integrals, areas, volumes
    ("T5.9", 10, ["definite integral", "area under curve", "area between curves",
                  "volume of revolution", "volume of solid", "disk method",
                  "shell method", "fundamental theorem of calculus",
                  "bounded area", "enclosed area"]),
    ("T5.9", 5,  ["definite integral", "area", "volume of revolution"]),

    # T5.10 — Differential equations (separable)
    ("T5.10", 10, ["separable differential equation", "separation of variables",
                   "differential equation", "dy/dx =", "solve the differential",
                   "general solution differential", "particular solution differential"]),
    ("T5.10", 5,  ["differential equation", "separable"]),

    # T5.11 — Differential equations (further)
    ("T5.11", 10, ["homogeneous differential equation", "integrating factor",
                   "linear differential equation", "first order linear",
                   "second order differential", "complementary function",
                   "particular integral", "euler method"]),
    ("T5.11", 5,  ["integrating factor", "homogeneous", "euler method"]),

    # T5.12 — Kinematics
    ("T5.12", 10, ["kinematics", "displacement", "velocity", "acceleration",
                   "position function", "velocity function", "acceleration function",
                   "particle moving", "motion along", "speed of particle",
                   "at rest", "changes direction"]),
    ("T5.12", 5,  ["velocity", "acceleration", "displacement", "particle"]),

    # T5.13 — Maclaurin series
    ("T5.13", 10, ["maclaurin series", "maclaurin expansion", "taylor series",
                   "power series expansion", "series expansion about 0",
                   "nth term maclaurin"]),
    ("T5.13", 5,  ["maclaurin", "taylor series", "power series"]),

    # T5.14 — Further series
    ("T5.14", 10, ["radius of convergence", "interval of convergence",
                   "convergence test", "ratio test", "series convergence",
                   "alternating series", "absolute convergence"]),
    ("T5.14", 5,  ["convergence", "radius of convergence"]),
]

SUBTOPIC_CODES = list(TOPIC_NAMES.keys())


def _parse_hint(hint: str) -> str | None:
    """Map a topic_hint string like '1.1' or '5.12' to a subtopic code like 'T1.1'."""
    hint = hint.strip()
    if not hint:
        return None
    # Accept forms: "1.1", "T1.1", "1", "T1"
    import re
    m = re.fullmatch(r"[Tt]?(\d+)(?:\.(\d+))?", hint)
    if not m:
        return None
    main = m.group(1)
    sub = m.group(2)
    if sub:
        candidate = f"T{main}.{sub}"
        if candidate in TOPIC_NAMES:
            return candidate
        return None
    # Only main topic number given — return None so keyword fallback fires
    return None


def _main_from_subtopic(code: str) -> str:
    return code.split(".")[0]


def classify_by_keywords(text: str) -> str:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for code, weight, keywords in RULES:
        for kw in keywords:
            if kw in text_lower:
                scores[code] = scores.get(code, 0) + weight
    if not scores:
        return "T5.2"  # default: differentiation basics — most common in AA HL
    return max(scores, key=lambda c: scores[c])


def classify(topic_hint: str, text: str) -> str:
    code = _parse_hint(topic_hint)
    if code:
        return code
    return classify_by_keywords(text)


def main():
    if not PARSED_DIR.exists():
        print(f"Parsed directory not found: {PARSED_DIR}")
        return

    json_files = sorted(PARSED_DIR.glob("*.json"))
    if not json_files:
        print(f"No JSON files in {PARSED_DIR}")
        return

    topic_counts: dict[str, int] = {}

    for jf in json_files:
        with open(jf, encoding="utf-8") as f:
            data = json.load(f)

        hint = str(data.get("topic_hint", ""))
        text = data.get("full_text", "") + " " + data.get("title", "")

        code = classify(hint, text)
        data["topic_code"] = code
        data["topic_name"] = TOPIC_NAMES.get(code, "Unknown")
        data["main_topic"] = _main_from_subtopic(code)

        with open(jf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        topic_counts[code] = topic_counts.get(code, 0) + 1

    print(f"Classified {len(json_files)} file(s)\n")
    print(f"{'Code':<8} {'Name':<45} {'Count':>5}")
    print("-" * 62)
    for code in sorted(topic_counts, key=lambda c: (c.split(".")[0], int(c.split(".")[1]) if "." in c else 0)):
        name = TOPIC_NAMES.get(code, "Unknown")
        bar = "#" * topic_counts[code]
        print(f"{code:<8} {name:<45} {topic_counts[code]:>5}  {bar}")


if __name__ == "__main__":
    main()
