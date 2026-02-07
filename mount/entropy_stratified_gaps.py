#!/usr/bin/env python3
"""
Test: Do structural vs generic primes have different gap distributions?
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from prime_entropy import bientropy, sieve_of_eratosthenes


def analyze_stratified_gaps(max_n=20000):
    """
    Categorize primes by entropy, then analyze their gaps.
    """
    primes = sieve_of_eratosthenes(max_n)

    # Compute entropies
    prime_data = []
    for p in primes:
        h = bientropy(p)
        prime_data.append((p, h))

    # Stratify into classes
    structural = []  # H < 0.3
    transition = []  # 0.3 ≤ H < 0.6
    generic = []     # H ≥ 0.6

    for p, h in prime_data:
        if h < 0.3:
            structural.append(p)
        elif h < 0.6:
            transition.append(p)
        else:
            generic.append(p)

    print("="*70)
    print("Prime Stratification by Entropy")
    print("="*70)
    print(f"Structural (H<0.3):    {len(structural):>6} primes ({100*len(structural)/len(primes):.1f}%)")
    print(f"Transition (0.3≤H<0.6): {len(transition):>6} primes ({100*len(transition)/len(primes):.1f}%)")
    print(f"Generic (H≥0.6):       {len(generic):>6} primes ({100*len(generic)/len(primes):.1f}%)")

    # Compute gap distributions for each class
    def compute_gaps(prime_list):
        if len(prime_list) < 2:
            return []
        return [prime_list[i+1] - prime_list[i] for i in range(len(prime_list)-1)]

    structural_gaps = compute_gaps(structural)
    transition_gaps = compute_gaps(transition)
    generic_gaps = compute_gaps(generic)

    # Statistics
    print("\n" + "="*70)
    print("Gap Statistics by Entropy Class")
    print("="*70)
    print(f"{'Class':<15} {'Mean Gap':>12} {'Median Gap':>12} {'Max Gap':>12} {'Std Gap':>12}")
    print("-"*70)

    if structural_gaps:
        print(f"{'Structural':<15} {np.mean(structural_gaps):>12.2f} {np.median(structural_gaps):>12.1f} "
              f"{max(structural_gaps):>12} {np.std(structural_gaps):>12.2f}")
    if transition_gaps:
        print(f"{'Transition':<15} {np.mean(transition_gaps):>12.2f} {np.median(transition_gaps):>12.1f} "
              f"{max(transition_gaps):>12} {np.std(transition_gaps):>12.2f}")
    if generic_gaps:
        print(f"{'Generic':<15} {np.mean(generic_gaps):>12.2f} {np.median(generic_gaps):>12.1f} "
              f"{max(generic_gaps):>12} {np.std(generic_gaps):>12.2f}")

    # Statistical test: are distributions different?
    print("\n" + "="*70)
    print("Statistical Tests (Mann-Whitney U)")
    print("="*70)

    if structural_gaps and generic_gaps:
        u_stat, p_val = stats.mannwhitneyu(structural_gaps, generic_gaps, alternative='two-sided')
        print(f"Structural vs Generic: U={u_stat:.0f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  → Significantly different distributions (p<0.05)")
        else:
            print("  → No significant difference")

    if transition_gaps and generic_gaps:
        u_stat, p_val = stats.mannwhitneyu(transition_gaps, generic_gaps, alternative='two-sided')
        print(f"Transition vs Generic: U={u_stat:.0f}, p={p_val:.4f}")
        if p_val < 0.05:
            print("  → Significantly different distributions (p<0.05)")
        else:
            print("  → No significant difference")

    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Gap distributions
    if structural_gaps:
        axes[0, 0].hist(structural_gaps, bins=30, alpha=0.7, label='Structural', color='red', density=True)
    if transition_gaps:
        axes[0, 0].hist(transition_gaps, bins=30, alpha=0.6, label='Transition', color='orange', density=True)
    if generic_gaps:
        axes[0, 0].hist(generic_gaps, bins=30, alpha=0.5, label='Generic', color='blue', density=True)

    axes[0, 0].set_xlabel('Gap to Next Prime')
    axes[0, 0].set_ylabel('Density')
    axes[0, 0].set_title('Gap Distribution by Entropy Class')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_xlim(0, 100)

    # CDF comparison
    if structural_gaps:
        structural_sorted = np.sort(structural_gaps)
        axes[0, 1].plot(structural_sorted, np.arange(1, len(structural_sorted)+1)/len(structural_sorted),
                       label='Structural', color='red', linewidth=2)
    if transition_gaps:
        transition_sorted = np.sort(transition_gaps)
        axes[0, 1].plot(transition_sorted, np.arange(1, len(transition_sorted)+1)/len(transition_sorted),
                       label='Transition', color='orange', linewidth=2)
    if generic_gaps:
        generic_sorted = np.sort(generic_gaps)
        axes[0, 1].plot(generic_sorted, np.arange(1, len(generic_sorted)+1)/len(generic_sorted),
                       label='Generic', color='blue', linewidth=2)

    axes[0, 1].set_xlabel('Gap to Next Prime')
    axes[0, 1].set_ylabel('Cumulative Probability')
    axes[0, 1].set_title('CDF Comparison')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].set_xlim(0, 100)

    # Box plot
    gap_data = []
    gap_labels = []
    if structural_gaps:
        gap_data.append(structural_gaps)
        gap_labels.append('Structural')
    if transition_gaps:
        gap_data.append(transition_gaps)
        gap_labels.append('Transition')
    if generic_gaps:
        gap_data.append(generic_gaps)
        gap_labels.append('Generic')

    axes[1, 0].boxplot(gap_data, labels=gap_labels, patch_artist=True)
    axes[1, 0].set_ylabel('Gap to Next Prime')
    axes[1, 0].set_title('Gap Distribution Comparison')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

    # Show structural primes explicitly
    if structural:
        axes[1, 1].scatter(range(len(structural)), structural, s=20, color='red', alpha=0.7)
        axes[1, 1].set_xlabel('Index in Structural Primes')
        axes[1, 1].set_ylabel('Prime Value')
        axes[1, 1].set_title(f'Structural Primes (n={len(structural)})')
        axes[1, 1].grid(True, alpha=0.3)

        # Annotate first few
        for i, p in enumerate(structural[:10]):
            axes[1, 1].annotate(str(p), (i, p), fontsize=8, ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/entropy_stratified_gaps.png', dpi=150)
    print("\nSaved visualization to entropy_stratified_gaps.png")

    # Show specific structural primes and their gaps
    print("\n" + "="*70)
    print("Structural Primes and Their Gaps")
    print("="*70)
    print(f"{'Prime':>10} {'Binary':>20} {'Gap':>10}")
    print("-"*70)

    for i, p in enumerate(structural[:20]):
        from prime_entropy import to_binary_string
        binary = to_binary_string(p)
        gap = structural[i+1] - p if i+1 < len(structural) else '—'
        print(f"{p:>10} {binary:>20} {str(gap):>10}")


if __name__ == "__main__":
    analyze_stratified_gaps(max_n=20000)
