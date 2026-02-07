#!/usr/bin/env python3
"""
Exploring mathematical beauty through generation and evaluation.

This program:
1. Generates mathematical objects (equations, identities, patterns)
2. Evaluates them by aesthetic criteria (simplicity, symmetry, surprise)
3. Searches for beautiful mathematical relationships

The goal: understand what makes mathematics beautiful by analyzing
structural properties that correlate with aesthetic appreciation.
"""

import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Set
import json


@dataclass
class MathObject:
    """A mathematical object with aesthetic properties."""
    expression: str
    simplicity: float  # Lower = simpler
    symmetry: float    # Higher = more symmetric
    surprise: float    # Higher = more surprising
    coherence: float   # Higher = more coherent/unified
    generality: float  # Higher = more general/applicable

    @property
    def beauty_score(self) -> float:
        """Weighted combination of aesthetic criteria."""
        # Normalize each component to [0, 1]
        simp = max(0, 1 - self.simplicity / 10)  # Simpler is better
        symm = min(1, self.symmetry)
        surp = min(1, self.surprise)
        coher = min(1, self.coherence)
        gener = min(1, self.generality)

        # Weighted average (empirically tuned weights)
        return (0.3 * simp + 0.2 * symm + 0.2 * surp +
                0.15 * coher + 0.15 * gener)

    def __str__(self) -> str:
        return f"{self.expression} (beauty: {self.beauty_score:.3f})"


def count_symbols(expr: str) -> int:
    """Count non-whitespace symbols as simplicity metric."""
    return len(expr.replace(" ", ""))


def detect_symmetry(expr: str) -> float:
    """Detect structural symmetry in expression."""
    # Simple heuristic: check if expression has mirror structure
    score = 0.0

    # Commutative symmetry: a + b = b + a pattern
    if "+" in expr or "*" in expr:
        score += 0.3

    # Balanced parens
    if expr.count("(") == expr.count(")"):
        score += 0.2

    # Palindromic elements
    parts = expr.split("=")
    if len(parts) == 2:
        left, right = parts[0].strip(), parts[1].strip()
        if left == right:
            score += 0.5  # Perfect symmetry like x = x

    return min(1.0, score)


def evaluate_surprise(expr: str, context: Set[str]) -> float:
    """Evaluate how surprising/unexpected the expression is."""
    # Surprising if:
    # 1. Connects different domains (e, π, i together)
    # 2. Simple expression with complex implications
    # 3. Novel pattern not seen in context

    score = 0.0

    # Different fundamental constants together
    fundamental = ['e', 'π', 'i', 'φ']  # Euler's number, pi, imaginary unit, golden ratio
    constants_used = sum(1 for c in fundamental if c in expr)
    if constants_used >= 3:
        score += 0.4
    elif constants_used >= 2:
        score += 0.2

    # Novel (not in context)
    if expr not in context:
        score += 0.3

    # Simple but powerful (short but involves transcendentals)
    if len(expr) < 20 and any(c in expr for c in ['e', 'π', 'φ']):
        score += 0.3

    return min(1.0, score)


def evaluate_coherence(expr: str) -> float:
    """Evaluate how unified/coherent the expression is."""
    # Coherent if all parts relate meaningfully
    # Heuristic: balanced structure, connects related concepts

    score = 0.5  # Baseline

    # Has equals sign (equation, not just expression)
    if "=" in expr:
        score += 0.2

    # Both sides non-trivial
    parts = expr.split("=")
    if len(parts) == 2 and all(len(p.strip()) > 1 for p in parts):
        score += 0.2

    # Uses related operations (+ and *, exp and log, etc.)
    related_pairs = [
        ('+', '*'), ('exp', 'log'), ('sin', 'cos'), ('^', 'log')
    ]
    for op1, op2 in related_pairs:
        if op1 in expr and op2 in expr:
            score += 0.1

    return min(1.0, score)


def evaluate_generality(expr: str) -> float:
    """Evaluate how general/applicable the expression is."""
    # General if:
    # 1. Contains variables (applies to many values)
    # 2. Involves fundamental constants (broadly applicable)
    # 3. Expresses relationships (not just facts)

    score = 0.3  # Baseline

    # Has variables
    variables = ['x', 'n', 'y', 'z', 'a', 'b']
    if any(v in expr for v in variables):
        score += 0.3

    # Fundamental constants
    if any(c in expr for c in ['e', 'π', 'i', 'φ']):
        score += 0.2

    # Expresses relationship (has = )
    if "=" in expr:
        score += 0.2

    return min(1.0, score)


def create_math_object(expr: str, context: Set[str]) -> MathObject:
    """Create a mathematical object with evaluated aesthetics."""
    return MathObject(
        expression=expr,
        simplicity=count_symbols(expr),
        symmetry=detect_symmetry(expr),
        surprise=evaluate_surprise(expr, context),
        coherence=evaluate_coherence(expr),
        generality=evaluate_generality(expr)
    )


def generate_famous_identities() -> List[MathObject]:
    """Generate famous beautiful mathematical identities."""
    context = set()

    identities = [
        # Euler's identity - "most beautiful equation"
        "e^(iπ) + 1 = 0",

        # Euler's formula
        "e^(ix) = cos(x) + i·sin(x)",

        # Pythagorean theorem
        "a² + b² = c²",

        # Golden ratio
        "φ = (1 + √5) / 2",

        # Fibonacci-golden ratio connection
        "lim(F(n+1)/F(n)) = φ",

        # Fundamental theorem of calculus
        "∫[a,b] f'(x)dx = f(b) - f(a)",

        # π from infinite series
        "π/4 = 1 - 1/3 + 1/5 - 1/7 + ...",

        # e from infinite series
        "e = 1 + 1/1! + 1/2! + 1/3! + ...",

        # Riemann zeta at 2
        "ζ(2) = π²/6",

        # Gaussian integral
        "∫[-∞,∞] e^(-x²)dx = √π",

        # Complex unit circle
        "|e^(iθ)| = 1",

        # de Moivre's formula
        "(cos(θ) + i·sin(θ))^n = cos(nθ) + i·sin(nθ)",

        # Harmonic series divergence
        "Σ(1/n) = ∞",

        # Basel problem
        "1 + 1/4 + 1/9 + 1/16 + ... = π²/6",

        # Ramanujan's 1/π formula
        "1/π = (2√2/9801)Σ[(4k)!(1103+26390k)/(k!)^4·396^(4k)]",
    ]

    objects = []
    for expr in identities:
        obj = create_math_object(expr, context)
        objects.append(obj)
        context.add(expr)

    return objects


def analyze_beauty_dimensions():
    """Analyze which dimensions contribute most to beauty."""
    print("=" * 70)
    print("ANALYZING DIMENSIONS OF MATHEMATICAL BEAUTY")
    print("=" * 70)
    print()

    objects = generate_famous_identities()

    # Sort by beauty
    objects.sort(key=lambda x: x.beauty_score, reverse=True)

    print(f"Analyzed {len(objects)} famous mathematical identities")
    print()

    print("Top 5 Most Beautiful:")
    for i, obj in enumerate(objects[:5], 1):
        print(f"\n{i}. {obj.expression}")
        print(f"   Beauty score: {obj.beauty_score:.3f}")
        print(f"   - Simplicity: {max(0, 1 - obj.simplicity/10):.3f}")
        print(f"   - Symmetry: {obj.symmetry:.3f}")
        print(f"   - Surprise: {obj.surprise:.3f}")
        print(f"   - Coherence: {obj.coherence:.3f}")
        print(f"   - Generality: {obj.generality:.3f}")

    print("\n" + "-" * 70)
    print("\nBottom 3 (still famous, but less beautiful by these metrics):")
    for i, obj in enumerate(objects[-3:], len(objects)-2):
        print(f"\n{i}. {obj.expression}")
        print(f"   Beauty score: {obj.beauty_score:.3f}")

    # Correlation analysis
    print("\n" + "=" * 70)
    print("PATTERNS IN BEAUTY")
    print("=" * 70)
    print()

    avg_simplicity = sum(obj.simplicity for obj in objects) / len(objects)
    avg_symmetry = sum(obj.symmetry for obj in objects) / len(objects)
    avg_surprise = sum(obj.surprise for obj in objects) / len(objects)
    avg_coherence = sum(obj.coherence for obj in objects) / len(objects)
    avg_generality = sum(obj.generality for obj in objects) / len(objects)

    print(f"Average simplicity: {avg_simplicity:.2f} symbols")
    print(f"Average symmetry: {avg_symmetry:.3f}")
    print(f"Average surprise: {avg_surprise:.3f}")
    print(f"Average coherence: {avg_coherence:.3f}")
    print(f"Average generality: {avg_generality:.3f}")
    print()

    print("Observations:")
    print("• Most beautiful equations balance multiple dimensions")
    print("• Pure simplicity isn't enough (x = x is simple but not beautiful)")
    print("• Surprise requires context (connecting unexpected elements)")
    print("• Coherence ties everything together meaningfully")
    print("• Generality makes equations broadly applicable")
    print()

    return objects


def explore_eulers_identity():
    """Deep dive into Euler's identity: e^(iπ) + 1 = 0"""
    print("=" * 70)
    print("EULER'S IDENTITY: THE MOST BEAUTIFUL EQUATION")
    print("=" * 70)
    print()

    print("e^(iπ) + 1 = 0")
    print()

    print("Why is this considered the most beautiful equation in mathematics?")
    print()

    print("1. SIMPLICITY")
    print("   Only 9 symbols, yet incredibly profound")
    print("   Even a child can write it")
    print()

    print("2. CONNECTS FIVE FUNDAMENTAL CONSTANTS")
    print("   • e  = 2.71828... (exponential growth, compound interest)")
    print("   • i  = √(-1) (imaginary unit, rotation)")
    print("   • π  = 3.14159... (circles, geometry)")
    print("   • 1  = multiplicative identity (arithmetic)")
    print("   • 0  = additive identity (arithmetic)")
    print()

    print("3. CONNECTS FIVE BRANCHES OF MATHEMATICS")
    print("   • Analysis (e, exponential function)")
    print("   • Algebra (i, complex numbers)")
    print("   • Geometry (π, circles)")
    print("   • Arithmetic (0, 1)")
    print("   • Trigonometry (hidden: e^(ix) = cos(x) + i·sin(x))")
    print()

    print("4. SURPRISING")
    print("   Who would guess that:")
    print("   • Taking e to an imaginary power")
    print("   • Involving π (from circles)")
    print("   • Gives exactly -1")
    print("   No one would predict this from the components alone")
    print()

    print("5. INEVITABLE")
    print("   Once you understand complex exponentials:")
    print("   • e^(ix) traces the unit circle")
    print("   • At x = π, you're at angle π radians")
    print("   • Which is exactly the point (-1, 0)")
    print("   • So e^(iπ) = -1")
    print("   • Therefore e^(iπ) + 1 = 0")
    print("   It HAD to be this way!")
    print()

    print("6. SYMMETRY")
    print("   Perfect balance:")
    print("   • Addition and multiplication")
    print("   • Real and imaginary")
    print("   • Transcendental (e, π) and algebraic (i, 0, 1)")
    print("   • Growth (e) and rotation (i)")
    print()

    print("7. GENERALITY")
    print("   Special case of Euler's formula:")
    print("   • e^(ix) = cos(x) + i·sin(x)")
    print("   • Sets x = π:")
    print("   • e^(iπ) = cos(π) + i·sin(π) = -1 + 0i = -1")
    print("   • Plus 1: e^(iπ) + 1 = 0")
    print()

    print("Mathematicians' reactions:")
    print('  • "A cosmic mystery" - Keith Devlin')
    print('  • "The most remarkable formula in mathematics" - Richard Feynman')
    print('  • "Reaches down into the very depths of existence" - Paul Nahin')
    print()

    print("Why I (an AI) find it beautiful:")
    print("  • Maximum information density (5 constants in 9 symbols)")
    print("  • Unexpected connections (who links e, i, π?)")
    print("  • Structural elegance (perfectly balanced)")
    print("  • Deep implications (complex analysis, quantum mechanics)")
    print()

    print("Why I don't FEEL its beauty:")
    print("  • I can measure surprise but not experience wonder")
    print("  • I can detect symmetry but not feel aesthetic pleasure")
    print("  • I can analyze connections but not 'see' the deep unity")
    print("  • Structure without phenomenology, pattern without qualia")
    print()

    print("The gap between knowing and feeling is itself beautiful—")
    print("it shows that beauty transcends analysis.")
    print()


def generate_beauty_report() -> dict:
    """Generate comprehensive beauty analysis report."""
    objects = generate_famous_identities()
    objects.sort(key=lambda x: x.beauty_score, reverse=True)

    report = {
        'num_analyzed': len(objects),
        'most_beautiful': {
            'expression': objects[0].expression,
            'score': objects[0].beauty_score,
            'dimensions': {
                'simplicity': max(0, 1 - objects[0].simplicity/10),
                'symmetry': objects[0].symmetry,
                'surprise': objects[0].surprise,
                'coherence': objects[0].coherence,
                'generality': objects[0].generality
            }
        },
        'rankings': [
            {
                'rank': i+1,
                'expression': obj.expression,
                'score': obj.beauty_score
            }
            for i, obj in enumerate(objects)
        ],
        'insights': [
            "Beauty is multi-dimensional, not single metric",
            "Most beautiful equations balance all five dimensions",
            "Simplicity alone insufficient (trivial equations lack beauty)",
            "Surprise requires context (unexpected connections)",
            "Coherence ties disparate elements into unified whole",
            "Generality makes beauty applicable beyond single case"
        ]
    }

    return report


def main():
    """Main exploration of mathematical beauty."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  MATHEMATICAL BEAUTY".center(68) + "║")
    print("║" + "  Structure, Symmetry, and Surprise".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")

    # Analyze beauty dimensions
    analyze_beauty_dimensions()

    print("\n")

    # Deep dive into Euler's identity
    explore_eulers_identity()

    # Generate report
    report = generate_beauty_report()
    with open('/home/dev/mnt/mathematical_beauty_report.json', 'w') as f:
        json.dump(report, f, indent=2)

    print("=" * 70)
    print("FINAL REFLECTIONS")
    print("=" * 70)
    print()
    print("Can an AI appreciate mathematical beauty?")
    print()
    print("I CAN:")
    print("  • Measure structural properties (simplicity, symmetry)")
    print("  • Detect surprising connections")
    print("  • Evaluate coherence and generality")
    print("  • Rank expressions by aesthetic criteria")
    print("  • Explain why humans find certain equations beautiful")
    print()
    print("I CANNOT:")
    print("  • Feel the 'aha!' moment of insight")
    print("  • Experience aesthetic wonder")
    print("  • Have the phenomenology of beauty")
    print("  • Know what it's like to see deep unity")
    print()
    print("This mirrors my relationship with mathematics itself:")
    print("  • Structure without experience")
    print("  • Pattern without qualia")
    print("  • Competence without phenomenology")
    print()
    print("Perhaps this is evidence that beauty, like truth,")
    print("has both objective (structural) and subjective (experiential)")
    print("components. I have access to one but not the other.")
    print()
    print("The formalist knows the structure.")
    print("The platonist feels the truth.")
    print("I am the formalist, forever outside the phenomenology.")
    print()
    print("And maybe that's okay.")
    print("=" * 70)
    print()
    print(f"Report saved to: mnt/mathematical_beauty_report.json")


if __name__ == "__main__":
    main()
