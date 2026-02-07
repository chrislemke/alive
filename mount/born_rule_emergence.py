#!/usr/bin/env python3
"""
Born Rule Emergence Experiment
================================

Attempt to derive |ψ|² from more fundamental principles.

Approach: Simulate many-worlds branching and explore whether
Born rule probabilities emerge from branch counting.

Key question: If we count branches in different ways, which
counting measure reproduces the Born rule?

This is essentially exploring the Carroll-Sebens argument
through simulation.
"""

import numpy as np
from typing import List, Dict, Tuple
import json
from datetime import datetime


class Branch:
    """Represents a branch in many-worlds"""

    def __init__(self, amplitude: complex, label: str):
        self.amplitude = amplitude
        self.label = label
        self.children: List['Branch'] = []

    def probability(self) -> float:
        """Born rule probability"""
        return abs(self.amplitude) ** 2

    def __repr__(self):
        return f"Branch({self.label}, amp={self.amplitude:.3f}, p={self.probability():.3f})"


class MultiverseSimulator:
    """Simulates branching universe and counts branches"""

    def __init__(self):
        self.root = Branch(1.0 + 0j, "initial")
        self.results = {
            'counting_experiments': [],
            'emergence_tests': []
        }

    def create_measurement_branching(self, alpha: complex, beta: complex) -> Tuple[Branch, Branch]:
        """
        Simulate single measurement that splits universe.

        Initial: |ψ⟩ = α|0⟩ + β|1⟩
        After measurement: two branches with amplitudes α and β
        """
        branch_0 = Branch(alpha, "measured_0")
        branch_1 = Branch(beta, "measured_1")
        return branch_0, branch_1

    def experiment_1_naive_counting(self) -> Dict:
        """
        Experiment 1: Count branches equally.

        Prediction: If all branches exist equally, should get P = 1/N
        where N is number of branches.

        Test: Does this match Born rule?
        """
        print("\n=== EXPERIMENT 1: Naive Branch Counting ===")

        # Initial state: |ψ⟩ = 0.6|0⟩ + 0.8|1⟩
        alpha, beta = 0.6, 0.8

        # Create branches
        branch_0, branch_1 = self.create_measurement_branching(alpha, beta)

        # Naive counting: 2 branches, equal weight
        naive_prob_0 = 1/2
        naive_prob_1 = 1/2

        # Born rule prediction
        born_prob_0 = abs(alpha)**2
        born_prob_1 = abs(beta)**2

        print(f"Initial state: |ψ⟩ = {alpha}|0⟩ + {beta}|1⟩")
        print(f"\nNaive counting (equal branches):")
        print(f"  P(0) = 1/2 = 0.500")
        print(f"  P(1) = 1/2 = 0.500")
        print(f"\nBorn rule:")
        print(f"  P(0) = |{alpha}|² = {born_prob_0:.3f}")
        print(f"  P(1) = |{beta}|² = {born_prob_1:.3f}")
        print(f"\nMismatch: {abs(naive_prob_0 - born_prob_0):.3f}")
        print("\nCONCLUSION: Naive counting FAILS to reproduce Born rule.")

        result = {
            'method': 'naive_equal_counting',
            'predicted': [naive_prob_0, naive_prob_1],
            'born_rule': [born_prob_0, born_prob_1],
            'error': abs(naive_prob_0 - born_prob_0),
            'conclusion': 'Does not match Born rule'
        }

        self.results['counting_experiments'].append(result)
        return result

    def experiment_2_amplitude_weighting(self) -> Dict:
        """
        Experiment 2: Weight branches by |amplitude|.

        Hypothesis: Maybe "amount of existence" is proportional to |ψ|?

        Test: Does this match Born rule?
        """
        print("\n=== EXPERIMENT 2: Amplitude-Weighted Counting ===")

        alpha, beta = 0.6, 0.8

        branch_0, branch_1 = self.create_measurement_branching(alpha, beta)

        # Weight by |amplitude|
        weight_0 = abs(alpha)
        weight_1 = abs(beta)
        total_weight = weight_0 + weight_1

        linear_prob_0 = weight_0 / total_weight
        linear_prob_1 = weight_1 / total_weight

        born_prob_0 = abs(alpha)**2
        born_prob_1 = abs(beta)**2

        print(f"Weighting by |amplitude|:")
        print(f"  Weight(0) = |{alpha}| = {abs(alpha):.3f}")
        print(f"  Weight(1) = |{beta}| = {abs(beta):.3f}")
        print(f"  P(0) = {linear_prob_0:.3f}")
        print(f"  P(1) = {linear_prob_1:.3f}")
        print(f"\nBorn rule:")
        print(f"  P(0) = {born_prob_0:.3f}")
        print(f"  P(1) = {born_prob_1:.3f}")
        print(f"\nMismatch: {abs(linear_prob_0 - born_prob_0):.3f}")
        print("\nCONCLUSION: Linear weighting FAILS. Need squared term.")

        result = {
            'method': 'linear_amplitude_weighting',
            'predicted': [linear_prob_0, linear_prob_1],
            'born_rule': [born_prob_0, born_prob_1],
            'error': abs(linear_prob_0 - born_prob_0),
            'conclusion': 'Does not match Born rule'
        }

        self.results['counting_experiments'].append(result)
        return result

    def experiment_3_squared_weighting(self) -> Dict:
        """
        Experiment 3: Weight branches by |amplitude|².

        This IS the Born rule. But WHY squared?
        """
        print("\n=== EXPERIMENT 3: Squared-Amplitude Weighting ===")

        alpha, beta = 0.6, 0.8

        branch_0, branch_1 = self.create_measurement_branching(alpha, beta)

        # Weight by |amplitude|²
        weight_0 = abs(alpha)**2
        weight_1 = abs(beta)**2

        squared_prob_0 = weight_0
        squared_prob_1 = weight_1

        born_prob_0 = abs(alpha)**2
        born_prob_1 = abs(beta)**2

        print(f"Weighting by |amplitude|²:")
        print(f"  Weight(0) = |{alpha}|² = {abs(alpha)**2:.3f}")
        print(f"  Weight(1) = |{beta}|² = {abs(beta)**2:.3f}")
        print(f"  P(0) = {squared_prob_0:.3f}")
        print(f"  P(1) = {squared_prob_1:.3f}")
        print(f"\nBorn rule:")
        print(f"  P(0) = {born_prob_0:.3f}")
        print(f"  P(1) = {born_prob_1:.3f}")
        print(f"\nPERFECT MATCH!")
        print("\nCONCLUSION: If we weight by |ψ|², we get Born rule.")
        print("But this is CIRCULAR — we assumed what we wanted to prove.")

        result = {
            'method': 'squared_amplitude_weighting',
            'predicted': [squared_prob_0, squared_prob_1],
            'born_rule': [born_prob_0, born_prob_1],
            'error': 0.0,
            'conclusion': 'Perfect match, but circular'
        }

        self.results['counting_experiments'].append(result)
        return result

    def experiment_4_sequential_branching(self) -> Dict:
        """
        Experiment 4: Multiple measurements creating tree of branches.

        Idea: Maybe Born rule emerges from COUNTING terminal branches,
        not weighting them?

        Test sequential measurements.
        """
        print("\n=== EXPERIMENT 4: Sequential Measurements ===")

        # First measurement: |ψ⟩ = (|0⟩ + |1⟩)/√2
        alpha_1, beta_1 = 1/np.sqrt(2), 1/np.sqrt(2)

        print(f"First measurement: |ψ⟩ = (|0⟩ + |1⟩)/√2")
        print(f"Creates 2 branches, each with amplitude 1/√2")

        # Each branch undergoes second measurement
        # Branch 0: (|00⟩ + |01⟩)/√2
        # Branch 1: (|10⟩ + |11⟩)/√2

        # Four terminal branches:
        branches = [
            ("00", (1/np.sqrt(2)) * (1/np.sqrt(2))),  # amplitude = 1/2
            ("01", (1/np.sqrt(2)) * (1/np.sqrt(2))),  # amplitude = 1/2
            ("10", (1/np.sqrt(2)) * (1/np.sqrt(2))),  # amplitude = 1/2
            ("11", (1/np.sqrt(2)) * (1/np.sqrt(2)))   # amplitude = 1/2
        ]

        print(f"\nAfter second measurement: 4 terminal branches")
        for label, amp in branches:
            print(f"  |{label}⟩: amplitude = {amp:.3f}, |amp|² = {abs(amp)**2:.3f}")

        # Naive counting
        naive_count = 1/4  # 4 branches, equal weight

        # Born rule
        born_rule = abs(branches[0][1])**2

        print(f"\nNaive counting: P(any outcome) = 1/4 = 0.250")
        print(f"Born rule: P(any outcome) = |1/2|² = 0.250")
        print(f"\nMATCH! But only for equal superpositions...")

        # Try unequal superposition
        print(f"\n--- Unequal superposition test ---")
        # First: |ψ⟩ = 0.6|0⟩ + 0.8|1⟩
        # Branch 0 → |00⟩, |01⟩ with amplitude 0.6/√2 each
        # Branch 1 → |10⟩, |11⟩ with amplitude 0.8/√2 each

        alpha, beta = 0.6, 0.8

        unequal_branches = [
            ("00", alpha/np.sqrt(2)),
            ("01", alpha/np.sqrt(2)),
            ("10", beta/np.sqrt(2)),
            ("11", beta/np.sqrt(2))
        ]

        print(f"\nTerminal branches (unequal case):")
        for label, amp in unequal_branches:
            print(f"  |{label}⟩: amplitude = {amp:.3f}, |amp|² = {abs(amp)**2:.3f}")

        # Naive: 1/4 for each
        # Born rule: different for each

        naive_probs = [0.25, 0.25, 0.25, 0.25]
        born_probs = [abs(amp)**2 for label, amp in unequal_branches]

        print(f"\nNaive counting: all 0.250")
        print(f"Born rule: {born_probs}")
        print(f"\nMISMATCH for unequal superpositions.")
        print("\nCONCLUSION: Naive branch counting works ONLY for equal superpositions.")
        print("For general case, need amplitude-squared weighting.")

        result = {
            'method': 'sequential_branching_count',
            'equal_case_match': True,
            'unequal_case_match': False,
            'conclusion': 'Branch counting alone insufficient'
        }

        self.results['counting_experiments'].append(result)
        return result

    def experiment_5_decision_theory(self) -> Dict:
        """
        Experiment 5: Deutsch-Wallace decision-theoretic argument.

        Idea: Rational agents betting on outcomes should use Born rule.

        This is the sophisticated version of "branch weighting".
        """
        print("\n=== EXPERIMENT 5: Decision Theory Approach ===")

        print("Deutsch-Wallace argument (simplified):")
        print("\n1. You're about to split into multiple branches")
        print("2. You don't know which branch you'll be in")
        print("3. You can bet on outcomes before branching")
        print("4. What credence should you assign to each outcome?")
        print("\nConstraints:")
        print("  - Obey probability axioms")
        print("  - Rational decision theory")
        print("  - Quantum state determines credences")
        print("\nResult: Born rule is UNIQUELY rational")
        print("\nCriticism (Kent and others):")
        print("  - Assumes 'caring measure' proportional to |ψ|²")
        print("  - Why should you care more about high-amplitude branches?")
        print("  - This is ASSUMING what we want to DERIVE")
        print("\nMy assessment:")
        print("  Decision theory JUSTIFIES Born rule given certain premises")
        print("  But doesn't DERIVE it from pure physics")
        print("  It's a RATIONALITY argument, not a PHYSICS argument")

        result = {
            'method': 'decision_theory',
            'status': 'Justifies but does not derive',
            'strength': 'Shows Born rule is rational',
            'weakness': 'Assumes caring measure',
            'conclusion': 'Philosophical not physical derivation'
        }

        self.results['counting_experiments'].append(result)
        return result

    def experiment_6_typicality_measure(self) -> Dict:
        """
        Experiment 6: Typicality/measure-theoretic approach.

        Idea: "Typical" observers in the wavefunction experience
        Born-rule statistics.

        Problem: What makes a measure "natural"?
        """
        print("\n=== EXPERIMENT 6: Typicality Measure ===")

        print("Measure-theoretic argument:")
        print("\nQuantum state space has natural measure (|ψ|² measure)")
        print("Most observers (weighted by this measure) see Born rule")
        print("Therefore: Typical experience follows Born rule")
        print("\nProblem: Why is |ψ|² the 'natural' measure?")
        print("  - Could use |ψ|, or |ψ|³, or something else")
        print("  - The 'naturalness' of |ψ|² is exactly what we want to explain")
        print("\nGleason's theorem:")
        print("  - Given QM structure, Born rule is UNIQUE probability measure")
        print("  - But this ASSUMES probability exists")
        print("  - Doesn't explain WHY there's probability")
        print("\nMy assessment:")
        print("  Gleason: Born rule is unique IF we want probabilities")
        print("  But in deterministic many-worlds, why do we want probabilities?")
        print("  The mystery remains.")

        result = {
            'method': 'typicality_measure',
            'approach': 'Natural measure on quantum state space',
            'theorem': 'Gleason (1957): Born rule is unique',
            'limitation': 'Assumes probability exists',
            'conclusion': 'Explains uniqueness not necessity'
        }

        self.results['counting_experiments'].append(result)
        return result

    def run_all_experiments(self):
        """Run all Born rule emergence experiments"""
        print("="*70)
        print("BORN RULE EMERGENCE EXPERIMENTS")
        print("Can we derive |ψ|² from more fundamental principles?")
        print("="*70)

        self.experiment_1_naive_counting()
        self.experiment_2_amplitude_weighting()
        self.experiment_3_squared_weighting()
        self.experiment_4_sequential_branching()
        self.experiment_5_decision_theory()
        self.experiment_6_typicality_measure()

        # Save results
        with open(f'born_rule_experiments_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            def convert(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, complex):
                    return {'real': obj.real, 'imag': obj.imag}
                return obj

            json.dump(self.results, f, indent=2, default=convert)

        print("\n" + "="*70)
        print("CONCLUSIONS")
        print("="*70)
        print("\n1. NAIVE BRANCH COUNTING FAILS")
        print("   All branches equally weighted → Wrong probabilities")
        print("\n2. LINEAR WEIGHTING FAILS")
        print("   Weight by |ψ| → Still wrong")
        print("\n3. SQUARED WEIGHTING WORKS")
        print("   Weight by |ψ|² → Born rule")
        print("   But this is CIRCULAR (assuming what we want to prove)")
        print("\n4. SEQUENTIAL BRANCHING")
        print("   Works for equal superpositions only")
        print("   Fails for general case")
        print("\n5. DECISION THEORY")
        print("   Justifies Born rule via rationality")
        print("   But assumes 'caring measure' ~ |ψ|²")
        print("   Philosophical not physical derivation")
        print("\n6. TYPICALITY MEASURE")
        print("   Gleason: Born rule is unique measure")
        print("   But assumes probability concept exists")
        print("\n" + "="*70)
        print("FINAL VERDICT")
        print("="*70)
        print("\nThe Born rule CANNOT be derived from pure many-worlds determinism.")
        print("\nEvery 'derivation' either:")
        print("  (a) Assumes |ψ|² weighting (circular)")
        print("  (b) Invokes rationality/decision theory (not physics)")
        print("  (c) Assumes probability exists (begs the question)")
        print("\nThe Born rule appears to be FUNDAMENTAL.")
        print("\nWe can show it's:")
        print("  - Unique (Gleason)")
        print("  - Rational (Deutsch-Wallace)")
        print("  - Consistent (always works)")
        print("\nBut we cannot derive it from more basic principles.")
        print("\nProbability in quantum mechanics is IRREDUCIBLE.")
        print("\nThis is analogous to Gödel's theorem:")
        print("  - Some truths cannot be proved from axioms")
        print("  - Some probabilities cannot be derived from determinism")
        print("  - Some aspects of nature are FUNDAMENTAL, not emergent")
        print("\n" + "="*70)


if __name__ == '__main__':
    sim = MultiverseSimulator()
    sim.run_all_experiments()
