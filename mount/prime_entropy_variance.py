#!/usr/bin/env python3
"""
Deeper analysis: variance and distribution shape of prime entropy.

Hypothesis: Primes have HIGHER VARIANCE in BiEntropy than composites,
not necessarily higher mean.
"""

import numpy as np
import matplotlib.pyplot as plt
from prime_entropy import (
    bientropy, sieve_of_eratosthenes, is_prime_simple,
    to_binary_string, factorize_simple
)


def analyze_variance(max_n=5000):
    """
    Compare variance and distribution shape between primes and composites.
    """
    primes = set(sieve_of_eratosthenes(max_n))

    prime_entropies = []
    composite_entropies = []

    for n in range(2, max_n + 1):
        be = bientropy(n)

        if n in primes:
            prime_entropies.append(be)
        else:
            composite_entropies.append(be)

    prime_arr = np.array(prime_entropies)
    comp_arr = np.array(composite_entropies)

    # Statistics
    stats = {
        'Prime mean': np.mean(prime_arr),
        'Prime std': np.std(prime_arr),
        'Prime variance': np.var(prime_arr),
        'Prime median': np.median(prime_arr),
        'Prime IQR': np.percentile(prime_arr, 75) - np.percentile(prime_arr, 25),
        'Composite mean': np.mean(comp_arr),
        'Composite std': np.std(comp_arr),
        'Composite variance': np.var(comp_arr),
        'Composite median': np.median(comp_arr),
        'Composite IQR': np.percentile(comp_arr, 75) - np.percentile(comp_arr, 25),
    }

    print("="*60)
    print(f"Entropy Statistics (n=2 to {max_n})")
    print("="*60)
    for key, val in stats.items():
        print(f"{key:>20}: {val:.6f}")

    print(f"\nVariance ratio (Prime/Composite): {stats['Prime variance']/stats['Composite variance']:.4f}")
    print(f"Std ratio (Prime/Composite): {stats['Prime std']/stats['Composite std']:.4f}")

    # Test for bimodality in primes
    print("\n" + "="*60)
    print("Distribution Shape Analysis")
    print("="*60)

    # Skewness and kurtosis
    from scipy.stats import skew, kurtosis

    prime_skew = skew(prime_arr)
    comp_skew = skew(comp_arr)
    prime_kurt = kurtosis(prime_arr)
    comp_kurt = kurtosis(comp_arr)

    print(f"Prime skewness: {prime_skew:.4f} (negative = left-skewed)")
    print(f"Composite skewness: {comp_skew:.4f}")
    print(f"Prime kurtosis: {prime_kurt:.4f} (>0 = heavy tails)")
    print(f"Composite kurtosis: {comp_kurt:.4f}")

    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # CDF comparison
    prime_sorted = np.sort(prime_arr)
    comp_sorted = np.sort(comp_arr)
    prime_cdf = np.arange(1, len(prime_sorted) + 1) / len(prime_sorted)
    comp_cdf = np.arange(1, len(comp_sorted) + 1) / len(comp_sorted)

    axes[0, 0].plot(prime_sorted, prime_cdf, label='Prime', color='blue', linewidth=2)
    axes[0, 0].plot(comp_sorted, comp_cdf, label='Composite', color='red', linewidth=2)
    axes[0, 0].set_xlabel('BiEntropy')
    axes[0, 0].set_ylabel('Cumulative Probability')
    axes[0, 0].set_title('CDF Comparison')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Box plot
    axes[0, 1].boxplot([prime_arr, comp_arr], labels=['Prime', 'Composite'])
    axes[0, 1].set_ylabel('BiEntropy')
    axes[0, 1].set_title('Distribution Comparison')
    axes[0, 1].grid(True, alpha=0.3)

    # Histogram with more bins
    axes[1, 0].hist(comp_arr, bins=100, alpha=0.6, label='Composite', color='red', density=True)
    axes[1, 0].hist(prime_arr, bins=100, alpha=0.6, label='Prime', color='blue', density=True)
    axes[1, 0].set_xlabel('BiEntropy')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].set_title('Detailed Distribution (100 bins)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Variance by magnitude
    # Split into ranges and compute variance in each
    ranges = [(2, 100), (100, 500), (500, 1000), (1000, 2000), (2000, max_n)]
    prime_vars = []
    comp_vars = []
    range_labels = []

    for low, high in ranges:
        p_in_range = [bientropy(n) for n in range(low, min(high, max_n) + 1) if n in primes]
        c_in_range = [bientropy(n) for n in range(low, min(high, max_n) + 1) if n not in primes]

        if p_in_range:
            prime_vars.append(np.var(p_in_range))
        else:
            prime_vars.append(0)

        if c_in_range:
            comp_vars.append(np.var(c_in_range))
        else:
            comp_vars.append(0)

        range_labels.append(f"{low}-{high}")

    x_pos = np.arange(len(ranges))
    width = 0.35

    axes[1, 1].bar(x_pos - width/2, prime_vars, width, label='Prime', color='blue', alpha=0.7)
    axes[1, 1].bar(x_pos + width/2, comp_vars, width, label='Composite', color='red', alpha=0.7)
    axes[1, 1].set_xlabel('Range')
    axes[1, 1].set_ylabel('Variance')
    axes[1, 1].set_title('Variance by Magnitude Range')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(range_labels, rotation=45)
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/prime_entropy_variance.png', dpi=150)
    print(f"\nSaved visualization to prime_entropy_variance.png")

    return stats


def find_patterns_in_low_entropy_primes():
    """
    What do low-entropy primes have in common?
    """
    primes = sieve_of_eratosthenes(10000)
    prime_entropies = [(p, bientropy(p)) for p in primes]

    # Low entropy primes
    low_entropy = [p for p, be in prime_entropies if be < 0.3]

    print("\n" + "="*60)
    print(f"Low Entropy Primes (BiEntropy < 0.3):")
    print("="*60)

    patterns = {}

    for p in low_entropy[:30]:
        binary = to_binary_string(p)
        be = bientropy(p)

        # Check for patterns
        is_mersenne = (p + 1) & p == 0  # p = 2^k - 1
        is_fermat_like = bin(p).count('1') <= 3  # Few 1s

        pattern = []
        if is_mersenne:
            pattern.append("Mersenne-like")
        if '11' in binary:
            pattern.append("consecutive 1s")
        if binary.count('1') <= len(binary) // 3:
            pattern.append("sparse")

        pattern_str = ", ".join(pattern) if pattern else "other"

        if pattern_str not in patterns:
            patterns[pattern_str] = []
        patterns[pattern_str].append(p)

        print(f"{p:>6} | BiEntropy: {be:.4f} | Binary: {binary:>20} | {pattern_str}")

    print("\n" + "="*60)
    print("Pattern summary:")
    print("="*60)
    for pattern, members in patterns.items():
        print(f"{pattern}: {len(members)} primes")


def entropy_and_prime_gaps():
    """
    Is there a relationship between BiEntropy and prime gaps?
    """
    primes = sieve_of_eratosthenes(5000)

    gaps = []
    entropies = []

    for i in range(len(primes) - 1):
        gap = primes[i+1] - primes[i]
        be = bientropy(primes[i])

        gaps.append(gap)
        entropies.append(be)

    # Correlation
    correlation = np.corrcoef(gaps, entropies)[0, 1]

    print("\n" + "="*60)
    print("BiEntropy vs Prime Gaps")
    print("="*60)
    print(f"Correlation: {correlation:.4f}")
    print("(Close to 0 = no linear relationship)")

    # Visualize
    plt.figure(figsize=(10, 6))
    plt.scatter(entropies, gaps, alpha=0.5, s=10)
    plt.xlabel('BiEntropy of prime p')
    plt.ylabel('Gap to next prime (p_{n+1} - p_n)')
    plt.title(f'BiEntropy vs Prime Gaps (correlation: {correlation:.4f})')
    plt.grid(True, alpha=0.3)
    plt.savefig('/home/dev/mnt/entropy_vs_gaps.png', dpi=150)
    print("Saved visualization to entropy_vs_gaps.png")


if __name__ == "__main__":
    # Main analysis
    stats = analyze_variance(max_n=5000)

    # Pattern exploration
    find_patterns_in_low_entropy_primes()

    # Gap analysis
    entropy_and_prime_gaps()
