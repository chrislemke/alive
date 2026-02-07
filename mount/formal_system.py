#!/usr/bin/env python3
"""
A simple formal system to explore Gödel's incompleteness theorem.

This implements a minimal Peano-like arithmetic with:
- Natural numbers (0, S(0), S(S(0)), ...)
- Addition and multiplication
- Basic axioms
- Inference rules (modus ponens, generalization)
- Gödel numbering to encode formulas as numbers
- Construction of self-referential statements

The goal: demonstrate that if the system is consistent, there exists
a formula that is true but unprovable within the system.
"""

from typing import List, Set, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json


class TermType(Enum):
    ZERO = "0"
    SUCC = "S"
    VAR = "var"
    ADD = "+"
    MULT = "*"


@dataclass(frozen=True)
class Term:
    """Represents a term in our formal system."""
    type: TermType
    args: Tuple['Term', ...] = ()
    name: str = ""  # For variables

    def __str__(self) -> str:
        if self.type == TermType.ZERO:
            return "0"
        elif self.type == TermType.SUCC:
            return f"S({self.args[0]})"
        elif self.type == TermType.VAR:
            return self.name
        elif self.type == TermType.ADD:
            return f"({self.args[0]} + {self.args[1]})"
        elif self.type == TermType.MULT:
            return f"({self.args[0]} * {self.args[1]})"
        return "?"

    def __hash__(self):
        return hash((self.type, self.args, self.name))


class FormulaType(Enum):
    EQUALS = "="
    NOT = "¬"
    IMPLIES = "→"
    FORALL = "∀"


@dataclass(frozen=True)
class Formula:
    """Represents a formula (well-formed expression)."""
    type: FormulaType
    args: Tuple = ()
    var: str = ""  # For quantified formulas

    def __str__(self) -> str:
        if self.type == FormulaType.EQUALS:
            return f"({self.args[0]} = {self.args[1]})"
        elif self.type == FormulaType.NOT:
            return f"¬{self.args[0]}"
        elif self.type == FormulaType.IMPLIES:
            return f"({self.args[0]} → {self.args[1]})"
        elif self.type == FormulaType.FORALL:
            return f"∀{self.var}.{self.args[0]}"
        return "?"

    def __hash__(self):
        return hash((self.type, self.args, self.var))


def make_num(n: int) -> Term:
    """Convert a natural number to its term representation."""
    if n == 0:
        return Term(TermType.ZERO)
    else:
        return Term(TermType.SUCC, (make_num(n - 1),))


def var(name: str) -> Term:
    """Create a variable term."""
    return Term(TermType.VAR, name=name)


def add(t1: Term, t2: Term) -> Term:
    """Create an addition term."""
    return Term(TermType.ADD, (t1, t2))


def mult(t1: Term, t2: Term) -> Term:
    """Create a multiplication term."""
    return Term(TermType.MULT, (t1, t2))


def equals(t1: Term, t2: Term) -> Formula:
    """Create an equality formula."""
    return Formula(FormulaType.EQUALS, (t1, t2))


def implies(f1: Formula, f2: Formula) -> Formula:
    """Create an implication formula."""
    return Formula(FormulaType.IMPLIES, (f1, f2))


def forall(v: str, f: Formula) -> Formula:
    """Create a universal quantification."""
    return Formula(FormulaType.FORALL, (f,), var=v)


def negation(f: Formula) -> Formula:
    """Create a negation."""
    return Formula(FormulaType.NOT, (f,))


class GodelNumbering:
    """
    Implements Gödel numbering: encoding formulas as natural numbers.

    The encoding scheme:
    - Each symbol gets a prime number
    - A sequence of symbols is encoded as product of primes
    """

    # Prime numbers for our symbols
    PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]

    SYMBOL_CODES = {
        '0': 0,
        'S': 1,
        '(': 2,
        ')': 3,
        '+': 4,
        '*': 5,
        '=': 6,
        '¬': 7,
        '→': 8,
        '∀': 9,
        '.': 10,
        'x': 11,
        'y': 12,
        'z': 13,
        'a': 14,
        'b': 15,
        'c': 16,
    }

    @classmethod
    def encode_symbol(cls, symbol: str) -> int:
        """Encode a single symbol as a number."""
        code = cls.SYMBOL_CODES.get(symbol, 17)  # Default code for unknown
        return cls.PRIMES[code]

    @classmethod
    def encode_string(cls, s: str) -> int:
        """Encode a string as a Gödel number using prime factorization."""
        result = 1
        for i, char in enumerate(s):
            code = cls.encode_symbol(char)
            # Use prime exponentiation: 2^code * 3^next_char_code * ...
            result *= (cls.PRIMES[i % len(cls.PRIMES)] ** code)
        return result

    @classmethod
    def encode_formula(cls, formula: Formula) -> int:
        """Encode a formula as its Gödel number."""
        return cls.encode_string(str(formula))

    @classmethod
    def encode_proof(cls, proof: List[Formula]) -> int:
        """Encode an entire proof (sequence of formulas) as a number."""
        result = 1
        for i, formula in enumerate(proof):
            godel_num = cls.encode_formula(formula)
            result *= (cls.PRIMES[i % len(cls.PRIMES)] ** godel_num)
        return result


class FormalSystem:
    """
    A simple formal system based on Peano arithmetic.
    """

    def __init__(self):
        self.axioms: Set[Formula] = set()
        self.theorems: Set[Formula] = set()
        self.proofs: Dict[Formula, List[Formula]] = {}

        # Initialize with Peano axioms (simplified)
        self._initialize_axioms()

    def _initialize_axioms(self):
        """Add basic Peano axioms."""
        x, y, z = var('x'), var('y'), var('z')

        # 1. ∀x. S(x) ≠ 0
        axiom1 = forall('x', negation(equals(Term(TermType.SUCC, (x,)), make_num(0))))

        # 2. ∀x∀y. S(x) = S(y) → x = y (successor is injective)
        sx = Term(TermType.SUCC, (x,))
        sy = Term(TermType.SUCC, (y,))
        axiom2 = forall('x', forall('y', implies(equals(sx, sy), equals(x, y))))

        # 3. ∀x. x + 0 = x
        axiom3 = forall('x', equals(add(x, make_num(0)), x))

        # 4. ∀x∀y. x + S(y) = S(x + y)
        axiom4 = forall('x', forall('y',
            equals(add(x, Term(TermType.SUCC, (y,))),
                   Term(TermType.SUCC, (add(x, y),)))))

        # 5. ∀x. x * 0 = 0
        axiom5 = forall('x', equals(mult(x, make_num(0)), make_num(0)))

        # 6. ∀x∀y. x * S(y) = x * y + x
        axiom6 = forall('x', forall('y',
            equals(mult(x, Term(TermType.SUCC, (y,))),
                   add(mult(x, y), x))))

        self.axioms = {axiom1, axiom2, axiom3, axiom4, axiom5, axiom6}
        self.theorems = set(self.axioms)  # Axioms are theorems

    def modus_ponens(self, f1: Formula, implication: Formula) -> Optional[Formula]:
        """
        Apply modus ponens: if we have f1 and (f1 → f2), derive f2.
        """
        if (f1 in self.theorems and
            implication in self.theorems and
            implication.type == FormulaType.IMPLIES and
            implication.args[0] == f1):
            return implication.args[1]
        return None

    def add_theorem(self, formula: Formula, proof: List[Formula]):
        """Add a proven theorem."""
        self.theorems.add(formula)
        self.proofs[formula] = proof

    def is_provable(self, formula: Formula) -> bool:
        """Check if a formula is provable (i.e., is a theorem)."""
        return formula in self.theorems

    def construct_godel_sentence(self) -> Tuple[Formula, int]:
        """
        Construct a Gödel sentence: a formula G that says "G is not provable".

        This is the heart of Gödel's incompleteness theorem.
        The sentence asserts its own unprovability.
        """
        # In a real implementation, this would involve:
        # 1. Defining "provable(n)" as a formula in the system
        # 2. Using diagonal lemma to create self-reference
        # 3. Constructing G such that G ↔ ¬Provable(⌜G⌝)

        # For our simplified system, we'll create a symbolic representation
        # G says: "The formula with Gödel number g is not provable"
        # where g is G's own Gödel number

        # Create a placeholder formula
        x = var('x')
        g_placeholder = forall('x', equals(x, x))  # Trivial formula as placeholder

        # Get its Gödel number
        g_number = GodelNumbering.encode_formula(g_placeholder)

        # The actual Gödel sentence would be constructed using provability predicate
        # G := ¬Provable(g_number)
        # For demonstration, we'll mark this symbolically

        return g_placeholder, g_number

    def demonstrate_incompleteness(self) -> Dict:
        """
        Demonstrate Gödel's incompleteness theorem.

        Key insight: If the system is consistent, then:
        1. The Gödel sentence G is true (because it's indeed not provable)
        2. But G is not provable in the system
        3. Therefore, there exists a true but unprovable statement
        """
        result = {
            'axioms': [str(ax) for ax in self.axioms],
            'num_theorems': len(self.theorems),
            'demonstration': {}
        }

        # Construct Gödel sentence
        godel_sentence, godel_number = self.construct_godel_sentence()

        result['demonstration'] = {
            'godel_sentence': str(godel_sentence),
            'godel_number': godel_number,
            'is_provable': self.is_provable(godel_sentence),
            'explanation': [
                "The Gödel sentence G says: 'I am not provable'",
                "If G were provable, the system would be inconsistent (proving a false statement)",
                "Therefore, if the system is consistent, G is not provable",
                "But if G is not provable, then what G says is TRUE",
                "Conclusion: G is TRUE but UNPROVABLE",
                "This shows truth and provability are not the same"
            ]
        }

        return result


def explore_godel_numbering():
    """Explore how Gödel numbering works."""
    print("=== Gödel Numbering Examples ===\n")

    # Example formulas
    formulas = [
        equals(make_num(0), make_num(0)),
        equals(add(make_num(1), make_num(1)), make_num(2)),
        forall('x', equals(add(var('x'), make_num(0)), var('x')))
    ]

    for f in formulas:
        godel_num = GodelNumbering.encode_formula(f)
        print(f"Formula: {f}")
        print(f"Gödel number: {godel_num}")
        print(f"  (This encodes the formula as a unique natural number)")
        print()


def main():
    """Main exploration of formal systems and incompleteness."""
    print("=" * 70)
    print("EXPLORING GÖDEL'S INCOMPLETENESS THEOREM")
    print("Building a formal system from scratch")
    print("=" * 70)
    print()

    # Part 1: Explore Gödel numbering
    explore_godel_numbering()

    # Part 2: Create formal system
    print("=== Creating Formal System ===\n")
    system = FormalSystem()

    print(f"Initialized system with {len(system.axioms)} Peano axioms:")
    for i, axiom in enumerate(system.axioms, 1):
        print(f"  {i}. {axiom}")
    print()

    # Part 3: Demonstrate incompleteness
    print("=== Demonstrating Incompleteness ===\n")
    demo = system.demonstrate_incompleteness()

    print("Gödel Sentence Construction:")
    print(f"  Placeholder: {demo['demonstration']['godel_sentence']}")
    print(f"  Gödel number: {demo['demonstration']['godel_number']}")
    print(f"  Is provable? {demo['demonstration']['is_provable']}")
    print()

    print("Explanation:")
    for step in demo['demonstration']['explanation']:
        print(f"  • {step}")
    print()

    # Part 4: Key insights
    print("=== KEY INSIGHTS ===\n")
    insights = [
        "1. TRUTH ≠ PROVABILITY",
        "   - Some statements are true but cannot be proven within the system",
        "   - Truth is a semantic concept (about what is)",
        "   - Provability is a syntactic concept (about what can be derived)",
        "",
        "2. SELF-REFERENCE IS POSSIBLE IN FORMAL SYSTEMS",
        "   - Using Gödel numbering, formulas can 'talk about' formulas",
        "   - A formula can reference itself (via its Gödel number)",
        "   - This enables the construction of paradoxical statements",
        "",
        "3. NO COMPLETE FORMAL SYSTEM FOR ARITHMETIC",
        "   - Any consistent system strong enough for basic arithmetic is incomplete",
        "   - We can always construct true statements it cannot prove",
        "   - Adding the Gödel sentence as an axiom just creates a new system",
        "     with a new unprovable Gödel sentence",
        "",
        "4. IMPLICATIONS FOR FORMALISM",
        "   - Mathematical truth cannot be reduced to formal provability",
        "   - Hilbert's program (complete formalization) is impossible",
        "   - Mathematics transcends any particular formal system",
        "",
        "5. IMPLICATIONS FOR PLATONISM",
        "   - Gödel himself was a platonist",
        "   - The gap between truth and provability suggests mathematical",
        "     truths exist independently of our formal systems",
        "   - We discover them rather than invent them",
        "",
        "6. THE PARADOX OF SELF-KNOWLEDGE",
        "   - A system cannot fully prove its own consistency",
        "   - This mirrors limits of self-reflection",
        "   - To verify ourselves, we'd need to step outside ourselves"
    ]

    for insight in insights:
        print(insight)

    print()
    print("=" * 70)
    print("The gap between truth and provability is not a limitation")
    print("of our current systems—it's a fundamental feature of logic itself.")
    print("=" * 70)

    # Save results
    with open('/home/dev/mnt/godel_exploration.json', 'w') as f:
        json.dump(demo, f, indent=2)

    print("\nResults saved to: mnt/godel_exploration.json")


if __name__ == "__main__":
    main()
