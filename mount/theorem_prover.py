#!/usr/bin/env python3
"""
A simple automated theorem prover for propositional logic.

This implements:
- Natural deduction rules
- Proof search (backward chaining)
- Simple heuristics
- Demonstration of provable vs unprovable statements

The goal: explore the boundary between what formal systems can and cannot prove.
"""

from dataclasses import dataclass
from typing import List, Set, Optional, Tuple
from enum import Enum
import time


class PropType(Enum):
    ATOM = "atom"
    NOT = "¬"
    AND = "∧"
    OR = "∨"
    IMPLIES = "→"
    TRUE = "⊤"
    FALSE = "⊥"


@dataclass(frozen=True)
class Prop:
    """A propositional formula."""
    type: PropType
    name: str = ""  # For atoms
    left: Optional['Prop'] = None
    right: Optional['Prop'] = None

    def __str__(self) -> str:
        if self.type == PropType.ATOM:
            return self.name
        elif self.type == PropType.TRUE:
            return "⊤"
        elif self.type == PropType.FALSE:
            return "⊥"
        elif self.type == PropType.NOT:
            return f"¬{self.left}"
        elif self.type == PropType.AND:
            return f"({self.left} ∧ {self.right})"
        elif self.type == PropType.OR:
            return f"({self.left} ∨ {self.right})"
        elif self.type == PropType.IMPLIES:
            return f"({self.left} → {self.right})"
        return "?"

    def __hash__(self):
        return hash((self.type, self.name, self.left, self.right))


# Constructors for readability
def atom(name: str) -> Prop:
    return Prop(PropType.ATOM, name=name)

def true() -> Prop:
    return Prop(PropType.TRUE)

def false() -> Prop:
    return Prop(PropType.FALSE)

def neg(p: Prop) -> Prop:
    return Prop(PropType.NOT, left=p)

def and_(p: Prop, q: Prop) -> Prop:
    return Prop(PropType.AND, left=p, right=q)

def or_(p: Prop, q: Prop) -> Prop:
    return Prop(PropType.OR, left=p, right=q)

def implies(p: Prop, q: Prop) -> Prop:
    return Prop(PropType.IMPLIES, left=p, right=q)


@dataclass
class ProofStep:
    """A step in a proof."""
    formula: Prop
    rule: str
    premises: List[int]  # Indices of previous steps used

    def __str__(self) -> str:
        if self.premises:
            return f"{self.formula}  [{self.rule} from {self.premises}]"
        else:
            return f"{self.formula}  [{self.rule}]"


class TheoremProver:
    """
    A natural deduction theorem prover for propositional logic.
    Uses backward chaining to search for proofs.
    """

    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.proof_attempts = 0

    def prove(self, premises: List[Prop], goal: Prop) -> Optional[List[ProofStep]]:
        """
        Try to prove goal from premises.
        Returns a proof (list of steps) if successful, None otherwise.
        """
        self.proof_attempts = 0
        start_time = time.time()

        # Initialize proof with premises
        proof = [ProofStep(p, "premise", []) for p in premises]

        # Try to derive goal
        result = self._search(proof, goal, 0)

        elapsed = time.time() - start_time

        if result:
            print(f"✓ Proof found in {self.proof_attempts} attempts ({elapsed:.3f}s)")
            return result
        else:
            print(f"✗ No proof found after {self.proof_attempts} attempts ({elapsed:.3f}s)")
            return None

    def _search(self, proof: List[ProofStep], goal: Prop, depth: int) -> Optional[List[ProofStep]]:
        """Recursive proof search."""
        self.proof_attempts += 1

        # Check if we've already proven the goal
        for step in proof:
            if step.formula == goal:
                return proof

        # Depth limit
        if depth >= self.max_depth:
            return None

        # Try different inference rules
        # 1. Modus ponens: if we have (A → B) and A, derive B
        for i, step1 in enumerate(proof):
            if step1.formula.type == PropType.IMPLIES and step1.formula.right == goal:
                # We need to prove the antecedent
                antecedent = step1.formula.left
                result = self._search(proof, antecedent, depth + 1)
                if result:
                    result.append(ProofStep(goal, "modus ponens", [i, len(result) - 1]))
                    return result

        # 2. And elimination: if we have (A ∧ B), derive A or B
        for i, step in enumerate(proof):
            if step.formula.type == PropType.AND:
                if step.formula.left == goal:
                    new_proof = proof + [ProofStep(goal, "∧-elim-left", [i])]
                    return new_proof
                if step.formula.right == goal:
                    new_proof = proof + [ProofStep(goal, "∧-elim-right", [i])]
                    return new_proof

        # 3. And introduction: to prove (A ∧ B), prove both A and B
        if goal.type == PropType.AND:
            left_proof = self._search(proof, goal.left, depth + 1)
            if left_proof:
                right_proof = self._search(left_proof, goal.right, depth + 1)
                if right_proof:
                    right_proof.append(ProofStep(goal, "∧-intro",
                                                 [len(left_proof) - 1, len(right_proof) - 1]))
                    return right_proof

        # 4. Implication introduction: to prove (A → B), assume A and prove B
        if goal.type == PropType.IMPLIES:
            assumption = goal.left
            conclusion = goal.right
            new_proof = proof + [ProofStep(assumption, "assumption", [])]
            result = self._search(new_proof, conclusion, depth + 1)
            if result:
                # Discharge assumption
                result.append(ProofStep(goal, "→-intro", [len(result) - 1]))
                return result

        # 5. Double negation elimination: ¬¬A → A
        if goal.type == PropType.NOT and goal.left.type == PropType.NOT:
            inner = goal.left.left
            result = self._search(proof, inner, depth + 1)
            if result:
                result.append(ProofStep(goal, "¬¬-elim", [len(result) - 1]))
                return result

        # 6. Contradiction: if we have both A and ¬A, we can prove anything
        for i, step1 in enumerate(proof):
            for j, step2 in enumerate(proof):
                if step2.formula == neg(step1.formula) or step1.formula == neg(step2.formula):
                    # We have a contradiction, can derive anything
                    new_proof = proof + [ProofStep(goal, "ex falso", [i, j])]
                    return new_proof

        return None

    def prove_tautology(self, formula: Prop) -> Optional[List[ProofStep]]:
        """Prove that formula is a tautology (true with no premises)."""
        return self.prove([], formula)


def demo_basic_proofs():
    """Demonstrate basic provable theorems."""
    print("=" * 70)
    print("BASIC PROVABLE THEOREMS")
    print("=" * 70)
    print()

    prover = TheoremProver(max_depth=8)

    # Test cases: (name, premises, goal)
    tests = [
        ("Modus Ponens", [implies(atom('p'), atom('q')), atom('p')], atom('q')),
        ("Hypothetical Syllogism",
         [implies(atom('p'), atom('q')), implies(atom('q'), atom('r'))],
         implies(atom('p'), atom('r'))),
        ("And Elimination", [and_(atom('p'), atom('q'))], atom('p')),
        ("And Introduction", [atom('p'), atom('q')], and_(atom('p'), atom('q'))),
        ("Tautology: p → p", [], implies(atom('p'), atom('p'))),
        ("Tautology: p → (q → p)", [], implies(atom('p'), implies(atom('q'), atom('p')))),
        ("Tautology: (p → (q → r)) → ((p → q) → (p → r))",
         [],
         implies(implies(atom('p'), implies(atom('q'), atom('r'))),
                implies(implies(atom('p'), atom('q')),
                       implies(atom('p'), atom('r'))))),
    ]

    for name, premises, goal in tests:
        print(f"Theorem: {name}")
        print(f"  Goal: {goal}")
        if premises:
            print(f"  Premises: {[str(p) for p in premises]}")

        proof = prover.prove(premises, goal)

        if proof:
            print(f"  Proof ({len(proof)} steps):")
            for i, step in enumerate(proof):
                print(f"    {i+1}. {step}")
        else:
            print(f"  ✗ Could not prove (within depth limit)")

        print()


def demo_unprovable():
    """Demonstrate unprovable statements."""
    print("=" * 70)
    print("UNPROVABLE STATEMENTS")
    print("=" * 70)
    print()

    prover = TheoremProver(max_depth=10)

    # These should not be provable
    unprovable = [
        ("Law of Excluded Middle: p ∨ ¬p",
         [],
         or_(atom('p'), neg(atom('p')))),
        ("Bare atom: p",
         [],
         atom('p')),
        ("False implication: p → q (without premises)",
         [],
         implies(atom('p'), atom('q'))),
    ]

    print("These statements cannot be proven in intuitionistic logic:")
    print("(our prover uses constructive/intuitionistic rules)")
    print()

    for name, premises, goal in unprovable:
        print(f"Statement: {name}")
        print(f"  Formula: {goal}")
        proof = prover.prove(premises, goal)
        if not proof:
            print(f"  ✓ Correctly identified as unprovable")
        else:
            print(f"  ✗ Unexpectedly found proof!")
        print()


def demo_proof_limits():
    """Explore the limits of what can be proven."""
    print("=" * 70)
    print("EXPLORING PROOF LIMITS")
    print("=" * 70)
    print()

    print("Key insights about provability:")
    print()
    print("1. NOT ALL TRUE STATEMENTS ARE PROVABLE")
    print("   - In classical logic, 'p ∨ ¬p' is always true (tautology)")
    print("   - But in intuitionistic logic, we can't prove it constructively")
    print("   - Truth (semantic) ≠ Provability (syntactic)")
    print()
    print("2. PROOF SYSTEMS HAVE DIFFERENT STRENGTHS")
    print("   - Classical logic: Law of excluded middle")
    print("   - Intuitionistic logic: Only constructive proofs")
    print("   - Minimal logic: Even weaker")
    print("   - Each system proves different theorems")
    print()
    print("3. INCOMPLETENESS IN RICHER SYSTEMS")
    print("   - Propositional logic is complete (all tautologies provable)")
    print("   - First-order logic is complete (Gödel's completeness theorem)")
    print("   - But arithmetic (Peano) is incomplete (Gödel's incompleteness)")
    print("   - The richer the language, the bigger the gap")
    print()
    print("4. COMPUTATIONAL LIMITS")
    print("   - Some proofs are too long to ever find")
    print("   - Some theorems are true but have no proof shorter than")
    print("     the size of the universe")
    print("   - Undecidability: no algorithm can determine provability")
    print("     in general")
    print()
    print("5. THE HUMAN ELEMENT")
    print("   - Humans use intuition, analogy, creativity")
    print("   - We 'see' why things are true, beyond formal rules")
    print("   - Mathematical insight ≠ mechanical proof search")
    print("   - This is what makes mathematics an art")
    print()


def demo_self_reference():
    """Explore self-referential limits."""
    print("=" * 70)
    print("SELF-REFERENCE AND CONSISTENCY")
    print("=" * 70)
    print()

    print("Can a formal system prove its own consistency?")
    print()
    print("Gödel's Second Incompleteness Theorem says:")
    print("  'No consistent system can prove its own consistency'")
    print()
    print("Why?")
    print("  1. To prove consistency, you'd prove 'no contradiction exists'")
    print("  2. But the Gödel sentence G says 'G is not provable'")
    print("  3. Proving consistency would let you prove G")
    print("  4. But then G would be both provable and unprovable")
    print("  5. Contradiction!")
    print()
    print("Implication:")
    print("  Any system strong enough to do arithmetic cannot verify")
    print("  itself without assuming something stronger.")
    print()
    print("  This is like trying to lift yourself by your own bootstraps—")
    print("  you need to stand on something external.")
    print()
    print("Philosophical consequence:")
    print("  Perfect self-knowledge is impossible for sufficiently")
    print("  complex formal systems (and perhaps minds?).")
    print()


def analyze_beautiful_proofs():
    """Analyze what makes a proof beautiful."""
    print("=" * 70)
    print("MATHEMATICAL BEAUTY IN PROOFS")
    print("=" * 70)
    print()

    print("What makes a proof beautiful?")
    print()
    print("1. SIMPLICITY")
    print("   - Euler's e^(iπ) + 1 = 0")
    print("   - Connects five fundamental constants in one equation")
    print("   - The proof involves complex analysis, surprisingly simple")
    print()
    print("2. SURPRISE")
    print("   - Unexpected connections between distant areas")
    print("   - Fermat's Last Theorem proved using elliptic curves")
    print("   - Who would have guessed?")
    print()
    print("3. INEVITABILITY")
    print("   - Once you see it, it had to be that way")
    print("   - Cantor's diagonal argument")
    print("   - 'Of course the reals are uncountable!'")
    print()
    print("4. GENERALITY")
    print("   - Proves more than intended")
    print("   - Category theory: patterns across all mathematics")
    print("   - One proof, infinite applications")
    print()
    print("5. ELEGANCE")
    print("   - No wasted steps")
    print("   - Every part essential")
    print("   - Like a perfect machine")
    print()
    print("Are these objective or subjective?")
    print("  - Mathematicians often agree on beautiful proofs")
    print("  - But beauty may depend on background, culture, era")
    print("  - Perhaps both: objective structure + subjective response")
    print("  - Like music: mathematical patterns evoke aesthetic emotion")
    print()


def main():
    """Main theorem proving exploration."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  EXPLORING THE FOUNDATIONS OF MATHEMATICS".center(68) + "║")
    print("║" + "  Truth, Proof, and Beauty".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print("\n")

    # Run demonstrations
    demo_basic_proofs()
    demo_unprovable()
    demo_proof_limits()
    demo_self_reference()
    analyze_beautiful_proofs()

    print("=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    print()
    print("Mathematics exists in a strange space:")
    print()
    print("  • Precise yet inexhaustible")
    print("  • Formal yet creative")
    print("  • Objective yet beautiful")
    print("  • Mechanical yet insightful")
    print()
    print("The gap between truth and proof is not a bug—")
    print("it's what makes mathematics infinite.")
    print()
    print("As Gödel showed: any system powerful enough to be interesting")
    print("is necessarily incomplete. Mathematics always transcends")
    print("our attempts to capture it.")
    print()
    print("And perhaps that's the deepest beauty of all.")
    print("=" * 70)


if __name__ == "__main__":
    main()
