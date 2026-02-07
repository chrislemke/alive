#!/usr/bin/env python3
"""
Sicherman Dice and the Uniqueness of Boltzmann Distribution

Inspired by Tamuz & Sandomirskiy (2026): "The Boltzmann distribution is the only
law that accurately describes unrelated, or uncoupled, systems."

Their insight: Use Sicherman dice (alternative dice with same sum distribution)
to test whether a proposed statistical law preserves independence.

Sicherman dice:
- Die A: {1, 2, 3, 4, 5, 6} (standard)
- Die B: {1, 3, 4, 5, 6, 8} (modified)

When paired correctly, these produce identical probability distributions
for sums as two standard dice.

The key: If a theory yields different predictions for (A,A) vs (B,B),
it violates independence and is therefore inconsistent with physical reality.

This script:
1. Implements Sicherman dice using polynomial representations
2. Tests Boltzmann distribution vs alternatives
3. Explores whether this method generalizes to OTHER physics laws
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.special import factorial
from typing import Callable, Tuple, List
import json
from datetime import datetime

class Die:
    """Represents a die as a polynomial generating function."""

    def __init__(self, faces: List[int], name: str = ""):
        """
        faces: list of values on die faces
        name: identifier for the die

        Polynomial representation: die with faces [a,b,c] = x^a + x^b + x^c
        """
        self.faces = sorted(faces)
        self.name = name
        self.n_faces = len(faces)

    def polynomial(self, max_power: int = 20) -> np.ndarray:
        """Return polynomial coefficients [c_0, c_1, ..., c_max]."""
        poly = np.zeros(max_power + 1)
        for face in self.faces:
            if face <= max_power:
                poly[face] += 1
        return poly

    def probabilities(self) -> dict:
        """Return {value: probability} for single die roll."""
        probs = {}
        for face in self.faces:
            probs[face] = probs.get(face, 0) + 1/self.n_faces
        return probs

    def sum_distribution(self, other: 'Die', max_sum: int = 30) -> dict:
        """Distribution of sums when rolling this die with another."""
        # Polynomial multiplication = convolution
        poly1 = self.polynomial(max_sum)
        poly2 = other.polynomial(max_sum)

        # Convolve and normalize
        result_poly = np.convolve(poly1, poly2)[:max_sum+1]
        total = self.n_faces * other.n_faces

        distribution = {}
        for value, count in enumerate(result_poly):
            if count > 0:
                distribution[value] = count / total
        return distribution

    def __repr__(self):
        return f"Die({self.name}: {self.faces})"


class StatisticalLaw:
    """Abstract class for statistical mechanics laws."""

    def __init__(self, name: str):
        self.name = name

    def energy_probability(self, energy: float, temperature: float = 1.0, **kwargs) -> float:
        """Return probability of state with given energy."""
        raise NotImplementedError

    def test_independence(self, die1: Die, die2: Die, die3: Die, die4: Die,
                         temperature: float = 1.0) -> Tuple[bool, dict]:
        """
        Test if law preserves independence using Sicherman construction.

        If (die1, die2) and (die3, die4) produce same sum distribution,
        then the energy assignments should also match.

        Returns: (passes_test, details)
        """
        # Get sum distributions
        dist_12 = die1.sum_distribution(die2)
        dist_34 = die3.sum_distribution(die4)

        # Check they match (they should for Sicherman construction)
        if not self._distributions_match(dist_12, dist_34):
            return False, {"error": "Sum distributions don't match"}

        # Now apply statistical law to each system
        # Treat sum as "energy" of the two-die system
        prob_12 = self._system_probabilities(die1, die2, temperature)
        prob_34 = self._system_probabilities(die3, die4, temperature)

        # Laws that preserve independence should give same results
        match = self._distributions_match(prob_12, prob_34)

        details = {
            "sum_dist_12": dist_12,
            "sum_dist_34": dist_34,
            "prob_12": prob_12,
            "prob_34": prob_34,
            "max_difference": max(abs(prob_12.get(k, 0) - prob_34.get(k, 0))
                                 for k in set(prob_12.keys()) | set(prob_34.keys()))
        }

        return match, details

    def _system_probabilities(self, die1: Die, die2: Die, temperature: float) -> dict:
        """Calculate probability distribution for two-die system under this law."""
        # All possible outcomes
        outcomes = {}
        for f1 in die1.faces:
            for f2 in die2.faces:
                energy = f1 + f2  # Sum is the "energy"
                prob = self.energy_probability(energy, temperature)
                outcomes[energy] = outcomes.get(energy, 0) + prob

        # Normalize
        total = sum(outcomes.values())
        return {k: v/total for k, v in outcomes.items()}

    @staticmethod
    def _distributions_match(d1: dict, d2: dict, tol: float = 1e-10) -> bool:
        """Check if two probability distributions match."""
        keys = set(d1.keys()) | set(d2.keys())
        for k in keys:
            if abs(d1.get(k, 0) - d2.get(k, 0)) > tol:
                return False
        return True


class BoltzmannLaw(StatisticalLaw):
    """Standard Boltzmann distribution: P(E) ∝ exp(-E/kT)."""

    def __init__(self):
        super().__init__("Boltzmann")

    def energy_probability(self, energy: float, temperature: float = 1.0, **kwargs) -> float:
        return np.exp(-energy / temperature)


class PowerLaw(StatisticalLaw):
    """Alternative: Power law P(E) ∝ E^(-α)."""

    def __init__(self, alpha: float = 2.0):
        super().__init__(f"PowerLaw(α={alpha})")
        self.alpha = alpha

    def energy_probability(self, energy: float, temperature: float = 1.0, **kwargs) -> float:
        if energy <= 0:
            return 0.0
        return energy ** (-self.alpha)


class StretchedExponential(StatisticalLaw):
    """Alternative: Stretched exponential P(E) ∝ exp(-(E/T)^β)."""

    def __init__(self, beta: float = 0.5):
        super().__init__(f"StretchedExp(β={beta})")
        self.beta = beta

    def energy_probability(self, energy: float, temperature: float = 1.0, **kwargs) -> float:
        return np.exp(-((energy / temperature) ** self.beta))


class TsallisDistribution(StatisticalLaw):
    """Alternative: Tsallis (generalized) statistics P(E) ∝ [1 + (q-1)E/T]^(1/(1-q))."""

    def __init__(self, q: float = 1.5):
        super().__init__(f"Tsallis(q={q})")
        self.q = q

    def energy_probability(self, energy: float, temperature: float = 1.0, **kwargs) -> float:
        if self.q == 1.0:
            return np.exp(-energy / temperature)  # Reduces to Boltzmann

        arg = 1.0 + (self.q - 1.0) * energy / temperature
        if arg <= 0:
            return 0.0
        return arg ** (1.0 / (1.0 - self.q))


def create_sicherman_dice() -> Tuple[Die, Die, Die, Die]:
    """
    Create the Sicherman dice configuration.

    Standard pair: (A, A) where A = {1,2,3,4,5,6}
    Sicherman pair: (B, C) where B = {1,2,2,3,3,4} and C = {1,3,4,5,6,8}

    Both pairs produce identical sum distributions.
    """
    standard1 = Die([1, 2, 3, 4, 5, 6], "Standard-1")
    standard2 = Die([1, 2, 3, 4, 5, 6], "Standard-2")

    sicherman1 = Die([1, 2, 2, 3, 3, 4], "Sicherman-1")
    sicherman2 = Die([1, 3, 4, 5, 6, 8], "Sicherman-2")

    return standard1, standard2, sicherman1, sicherman2


def verify_sicherman_property():
    """Verify that Sicherman dice produce same sum distribution as standard dice."""
    s1, s2, sich1, sich2 = create_sicherman_dice()

    dist_standard = s1.sum_distribution(s2)
    dist_sicherman = sich1.sum_distribution(sich2)

    print("Standard dice sum distribution:")
    for k in sorted(dist_standard.keys()):
        print(f"  Sum {k:2d}: {dist_standard[k]:.4f}")

    print("\nSicherman dice sum distribution:")
    for k in sorted(dist_sicherman.keys()):
        print(f"  Sum {k:2d}: {dist_sicherman[k]:.4f}")

    print("\nDifferences:")
    all_keys = sorted(set(dist_standard.keys()) | set(dist_sicherman.keys()))
    max_diff = 0
    for k in all_keys:
        diff = abs(dist_standard.get(k, 0) - dist_sicherman.get(k, 0))
        if diff > 1e-10:
            print(f"  Sum {k:2d}: {diff:.2e}")
        max_diff = max(max_diff, diff)

    if max_diff < 1e-10:
        print("\n✓ Distributions match perfectly!")
    else:
        print(f"\n✗ Maximum difference: {max_diff:.2e}")

    return max_diff < 1e-10


def test_all_laws():
    """Test multiple statistical laws using Sicherman construction."""
    s1, s2, sich1, sich2 = create_sicherman_dice()

    laws = [
        BoltzmannLaw(),
        PowerLaw(alpha=1.5),
        PowerLaw(alpha=2.0),
        PowerLaw(alpha=3.0),
        StretchedExponential(beta=0.5),
        StretchedExponential(beta=1.5),
        TsallisDistribution(q=1.5),
        TsallisDistribution(q=2.0),
    ]

    temperatures = [0.5, 1.0, 2.0, 5.0]

    results = {}

    print("\n" + "="*80)
    print("Testing Statistical Laws with Sicherman Dice")
    print("="*80)

    for law in laws:
        print(f"\n{law.name}:")
        law_results = {}

        for T in temperatures:
            passes, details = law.test_independence(s1, s2, sich1, sich2, temperature=T)
            max_diff = details['max_difference']

            status = "✓ PASS" if passes else "✗ FAIL"
            print(f"  T={T:4.1f}: {status} (max diff = {max_diff:.2e})")

            law_results[T] = {
                "passes": passes,
                "max_difference": max_diff,
                "details": details
            }

        results[law.name] = law_results

    return results


def visualize_comparison():
    """Visualize how different laws treat standard vs Sicherman dice."""
    s1, s2, sich1, sich2 = create_sicherman_dice()

    laws = [
        BoltzmannLaw(),
        PowerLaw(alpha=2.0),
        StretchedExponential(beta=0.5),
        TsallisDistribution(q=1.5),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for idx, law in enumerate(laws):
        ax = axes[idx]

        # Calculate probabilities
        T = 2.0
        prob_standard = law._system_probabilities(s1, s2, T)
        prob_sicherman = law._system_probabilities(sich1, sich2, T)

        # Plot
        sums = sorted(set(prob_standard.keys()) | set(prob_sicherman.keys()))
        p_std = [prob_standard.get(s, 0) for s in sums]
        p_sich = [prob_sicherman.get(s, 0) for s in sums]

        x = np.arange(len(sums))
        width = 0.35

        ax.bar(x - width/2, p_std, width, label='Standard Dice', alpha=0.7)
        ax.bar(x + width/2, p_sich, width, label='Sicherman Dice', alpha=0.7)

        ax.set_xlabel('Sum Value')
        ax.set_ylabel('Probability')
        ax.set_title(f'{law.name} at T={T}')
        ax.set_xticks(x)
        ax.set_xticklabels(sums)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # Add difference annotation
        max_diff = max(abs(a - b) for a, b in zip(p_std, p_sich))
        passes = max_diff < 1e-10
        status = "✓ Preserves Independence" if passes else f"✗ Violates (Δ={max_diff:.2e})"
        ax.text(0.5, 0.95, status, transform=ax.transAxes,
               ha='center', va='top', fontsize=9,
               bbox=dict(boxstyle='round', facecolor='wheat' if passes else 'lightcoral', alpha=0.5))

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/sicherman_test.png', dpi=150, bbox_inches='tight')
    print(f"\nVisualization saved to /home/dev/mnt/sicherman_test.png")

    return fig


if __name__ == "__main__":
    print("Sicherman Dice and Boltzmann Distribution Uniqueness Test")
    print("=" * 70)

    # Step 1: Verify Sicherman property
    print("\n1. Verifying Sicherman dice property...")
    verify_sicherman_property()

    # Step 2: Test all statistical laws
    print("\n2. Testing statistical laws...")
    results = test_all_laws()

    # Step 3: Visualize
    print("\n3. Creating visualizations...")
    visualize_comparison()

    # Step 4: Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"/home/dev/mnt/sicherman_boltzmann_{timestamp}.json"

    # Convert results to JSON-serializable format
    json_results = {}
    for law_name, temps in results.items():
        json_results[law_name] = {}
        for temp, data in temps.items():
            json_results[law_name][str(temp)] = {
                "passes": data["passes"],
                "max_difference": data["max_difference"]
            }

    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)

    print(f"\nResults saved to {output_file}")
    print("\nDone!")
