#!/usr/bin/env python3
"""
Sicherman Dice and Composition Laws

The REAL test: Does a statistical law preserve its functional form
under composition of independent systems?

For Boltzmann: P(E) ∝ exp(-E/T)
- Two independent systems: P(E1) × P(E2) = exp(-E1/T) × exp(-E2/T) = exp(-(E1+E2)/T)
- The combined system follows THE SAME LAW with E_total = E1 + E2
- This is the MULTIPLICATIVE property of exponentials

For other laws (e.g., power law P(E) ∝ E^-α):
- Two systems: P(E1) × P(E2) = E1^-α × E2^-α = (E1×E2)^-α
- But E_total = E1 + E2, NOT E1 × E2
- So the combined system does NOT follow a power law!

The Sicherman dice test:
- If (A,A) and (B,C) have same sum distribution
- And the law preserves composition
- Then applying the law to individual dice vs. using it for the pair should match

The key insight: We need to test whether the law applied to INDIVIDUAL outcomes
gives the same result as the law applied to SUM outcomes.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Callable, Dict, List, Tuple
import json
from datetime import datetime


class CompositionLaw:
    """A statistical law with a composition rule for independent systems."""

    def __init__(self, name: str):
        self.name = name

    def weight(self, energy: float, temperature: float = 1.0) -> float:
        """Unnormalized weight for a single state with given energy."""
        raise NotImplementedError

    def composition_rule(self, e1: float, e2: float, temperature: float = 1.0) -> float:
        """
        How do energies combine for independent systems?

        For Boltzmann: E_combined = E1 + E2 (additive)
        For power law: Not well-defined (multiplicative energy??)
        """
        raise NotImplementedError

    def test_sicherman(self, standard_pair, sicherman_pair, temperature: float = 1.0) -> Dict:
        """
        Test using Sicherman dice.

        Two approaches:
        1. Apply law to individual die outcomes, then sum
        2. Apply law to sum outcomes directly

        If these match, the law preserves composition.
        """
        die1_std, die2_std = standard_pair
        die1_sich, die2_sich = sicherman_pair

        # Approach 1: Weight individual outcomes, then convolve
        weights_std = self._weights_from_individuals(die1_std, die2_std, temperature)
        weights_sich = self._weights_from_individuals(die1_sich, die2_sich, temperature)

        # Approach 2: Weight sum outcomes directly
        # (This is what my previous code did - it's the "right" way IF composition works)

        # Normalize
        Z_std = sum(weights_std.values())
        Z_sich = sum(weights_sich.values())

        prob_std = {k: v/Z_std for k, v in weights_std.items()}
        prob_sich = {k: v/Z_sich for k, v in weights_sich.items()}

        # Check if they match
        all_sums = sorted(set(prob_std.keys()) | set(prob_sich.keys()))
        max_diff = max(abs(prob_std.get(s, 0) - prob_sich.get(s, 0)) for s in all_sums)

        passes = max_diff < 1e-10

        return {
            "passes": passes,
            "max_difference": max_diff,
            "prob_standard": prob_std,
            "prob_sicherman": prob_sich
        }

    def _weights_from_individuals(self, die1_faces, die2_faces, temperature):
        """
        Calculate weights by:
        1. Assigning weight to each die face independently
        2. Combining according to composition rule
        3. Summing over all ways to achieve each total
        """
        weights = {}

        for f1 in die1_faces:
            for f2 in die2_faces:
                # Weight from each die
                w1 = self.weight(f1, temperature)
                w2 = self.weight(f2, temperature)

                # Combined weight (for independent systems)
                w_combined = w1 * w2

                # Sum value
                total = f1 + f2

                # Accumulate
                weights[total] = weights.get(total, 0) + w_combined

        return weights


class BoltzmannComposition(CompositionLaw):
    """Boltzmann: P(E) ∝ exp(-E/T), composition: E_12 = E1 + E2."""

    def __init__(self):
        super().__init__("Boltzmann")

    def weight(self, energy: float, temperature: float = 1.0) -> float:
        return np.exp(-energy / temperature)

    def composition_rule(self, e1: float, e2: float, temperature: float = 1.0) -> float:
        return e1 + e2  # Additive energies


class PowerLawComposition(CompositionLaw):
    """Power law: P(E) ∝ E^-α. No natural composition for additive energies!"""

    def __init__(self, alpha: float = 2.0):
        super().__init__(f"PowerLaw(α={alpha})")
        self.alpha = alpha

    def weight(self, energy: float, temperature: float = 1.0) -> float:
        if energy <= 0:
            return 1e-100  # Avoid division by zero
        return energy ** (-self.alpha)

    def composition_rule(self, e1: float, e2: float, temperature: float = 1.0) -> float:
        # No natural rule! Power law doesn't compose additively.
        # If we used E_combined = E1 × E2, it would work, but energy is NOT multiplicative
        return e1 + e2  # This will FAIL the test


class StretchedExpComposition(CompositionLaw):
    """Stretched exponential: P(E) ∝ exp(-(E/T)^β)."""

    def __init__(self, beta: float = 0.5):
        super().__init__(f"StretchedExp(β={beta})")
        self.beta = beta

    def weight(self, energy: float, temperature: float = 1.0) -> float:
        return np.exp(-((energy / temperature) ** self.beta))

    def composition_rule(self, e1: float, e2: float, temperature: float = 1.0) -> float:
        # For beta ≠ 1, this does NOT preserve the functional form
        # (E1^β + E2^β) ≠ (E1 + E2)^β
        return e1 + e2


class TsallisComposition(CompositionLaw):
    """Tsallis: P(E) ∝ [1 + (q-1)E/T]^(1/(1-q))."""

    def __init__(self, q: float = 1.5):
        super().__init__(f"Tsallis(q={q})")
        self.q = q

    def weight(self, energy: float, temperature: float = 1.0) -> float:
        if self.q == 1.0:
            return np.exp(-energy / temperature)

        arg = 1.0 + (self.q - 1.0) * energy / temperature
        if arg <= 0:
            return 1e-100
        return arg ** (1.0 / (1.0 - self.q))

    def composition_rule(self, e1: float, e2: float, temperature: float = 1.0) -> float:
        # Tsallis has a special composition rule (non-additive)
        # E_12 = E1 + E2 + (q-1) E1 E2 / T
        # But for independent systems, still problematic
        return e1 + e2


def main():
    print("Sicherman Dice Composition Test")
    print("="*70)

    # Standard and Sicherman dice
    standard = ([1,2,3,4,5,6], [1,2,3,4,5,6])
    sicherman = ([1,2,2,3,3,4], [1,3,4,5,6,8])

    # Verify they produce same sums
    print("\n1. Verifying Sicherman property...")
    sum_counts_std = {}
    for f1 in standard[0]:
        for f2 in standard[1]:
            s = f1 + f2
            sum_counts_std[s] = sum_counts_std.get(s, 0) + 1

    sum_counts_sich = {}
    for f1 in sicherman[0]:
        for f2 in sicherman[1]:
            s = f1 + f2
            sum_counts_sich[s] = sum_counts_sich.get(s, 0) + 1

    print("Standard sums:", sum_counts_std)
    print("Sicherman sums:", sum_counts_sich)
    print("Match:", sum_counts_std == sum_counts_sich)

    # Test different laws
    print("\n2. Testing composition laws...")
    print("="*70)

    laws = [
        BoltzmannComposition(),
        PowerLawComposition(alpha=1.5),
        PowerLawComposition(alpha=2.0),
        StretchedExpComposition(beta=0.5),
        StretchedExpComposition(beta=1.5),
        TsallisComposition(q=1.5),
    ]

    temperatures = [0.5, 1.0, 2.0, 5.0]

    all_results = {}

    for law in laws:
        print(f"\n{law.name}:")
        law_results = {}

        for T in temperatures:
            result = law.test_sicherman(standard, sicherman, T)

            status = "✓ PASS" if result["passes"] else "✗ FAIL"
            max_diff = result["max_difference"]

            print(f"  T={T:4.1f}: {status} (max diff = {max_diff:.2e})")

            law_results[str(T)] = {
                "passes": bool(result["passes"]),
                "max_difference": float(result["max_difference"])
            }

        all_results[law.name] = law_results

    # Visualize
    print("\n3. Creating visualization...")
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for idx, law in enumerate(laws):
        ax = axes[idx]
        T = 2.0

        result = law.test_sicherman(standard, sicherman, T)
        prob_std = result["prob_standard"]
        prob_sich = result["prob_sicherman"]

        sums = sorted(set(prob_std.keys()) | set(prob_sich.keys()))
        p_std = [prob_std.get(s, 0) for s in sums]
        p_sich = [prob_sich.get(s, 0) for s in sums]

        x = np.arange(len(sums))
        width = 0.35

        ax.bar(x - width/2, p_std, width, label='Standard Dice', alpha=0.7, color='steelblue')
        ax.bar(x + width/2, p_sich, width, label='Sicherman Dice', alpha=0.7, color='darkorange')

        ax.set_xlabel('Sum Value', fontsize=11)
        ax.set_ylabel('Probability', fontsize=11)
        ax.set_title(f'{law.name} at T={T}', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(sums)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

        # Status
        max_diff = result["max_difference"]
        passes = result["passes"]
        status = "✓ Preserves Composition" if passes else f"✗ Fails (Δ={max_diff:.2e})"

        color = 'lightgreen' if passes else 'lightcoral'
        ax.text(0.5, 0.95, status, transform=ax.transAxes,
               ha='center', va='top', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.7))

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/sicherman_composition_test.png', dpi=150, bbox_inches='tight')
    print("Saved to /home/dev/mnt/sicherman_composition_test.png")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/home/dev/mnt/sicherman_composition_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"Results saved to {output_file}")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("\nThe Sicherman test reveals which laws preserve composition.")
    print("Only Boltzmann (and its special cases) should pass consistently.")
    print("\nKey insight: exp(-E1/T) × exp(-E2/T) = exp(-(E1+E2)/T)")
    print("This MULTIPLICATIVE property is unique to exponentials!")
    print("="*70)


if __name__ == "__main__":
    main()
