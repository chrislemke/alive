#!/usr/bin/env python3
"""
Analyze entropy of special prime families.

Do different types of primes have different entropy signatures?
"""

import numpy as np
import matplotlib.pyplot as plt
from prime_entropy import (
    bientropy, is_prime_simple, to_binary_string, sieve_of_eratosthenes
)


def is_mersenne_prime(p):
    """Check if p is a Mersenne prime (2^n - 1)."""
    if not is_prime_simple(p):
        return False
    # Check if p+1 is a power of 2
    return (p + 1) & p == 0


def is_fermat_number(n):
    """Check if n is a Fermat number (2^(2^k) + 1)."""
    if n < 3:
        return False
    # n-1 must be a power of 2
    m = n - 1
    if m & (m - 1) != 0:
        return False
    # m must be 2^(2^k)
    # Count bits in m
    bits = m.bit_length() - 1
    return (1 << (1 << bits)) == m


def is_sophie_germain_prime(p):
    """Check if p is a Sophie Germain prime (both p and 2p+1 are prime)."""
    return is_prime_simple(p) and is_prime_simple(2*p + 1)


def is_safe_prime(p):
    """Check if p is a safe prime (p = 2q+1 where q is prime)."""
    if not is_prime_simple(p) or p == 2:
        return False
    return p > 2 and (p - 1) % 2 == 0 and is_prime_simple((p - 1) // 2)


def is_twin_prime(p, primes_set):
    """Check if p is part of a twin prime pair."""
    return (p - 2 in primes_set) or (p + 2 in primes_set)


def popcount(n):
    """Count number of 1s in binary representation."""
    return bin(n).count('1')


def analyze_special_families(max_n=10000):
    """
    Categorize primes by type and compute entropy statistics.
    """
    primes = sieve_of_eratosthenes(max_n)
    primes_set = set(primes)

    families = {
        'Mersenne': [],
        'Sophie Germain': [],
        'Safe': [],
        'Twin': [],
        'Sparse (≤3 bits)': [],
        'Dense (≥80% bits)': [],
        'Generic': []
    }

    for p in primes:
        be = bientropy(p)
        binary = to_binary_string(p)
        bit_density = popcount(p) / len(binary)

        # Categorize (a prime can be in multiple families)
        categorized = False

        if is_mersenne_prime(p):
            families['Mersenne'].append((p, be))
            categorized = True

        if is_sophie_germain_prime(p):
            families['Sophie Germain'].append((p, be))
            categorized = True

        if is_safe_prime(p):
            families['Safe'].append((p, be))
            categorized = True

        if is_twin_prime(p, primes_set):
            families['Twin'].append((p, be))
            categorized = True

        if popcount(p) <= 3:
            families['Sparse (≤3 bits)'].append((p, be))
            categorized = True

        if bit_density >= 0.8:
            families['Dense (≥80% bits)'].append((p, be))
            categorized = True

        if not categorized:
            families['Generic'].append((p, be))

    # Print statistics
    print("="*70)
    print("Special Prime Families: Entropy Analysis")
    print("="*70)
    print(f"{'Family':<20} {'Count':>8} {'Mean H':>10} {'Std H':>10} {'Min H':>10} {'Max H':>10}")
    print("-"*70)

    stats = {}
    for family, members in families.items():
        if not members:
            continue

        _, entropies = zip(*members)
        entropies = np.array(entropies)

        stats[family] = {
            'count': len(members),
            'mean': np.mean(entropies),
            'std': np.std(entropies),
            'min': np.min(entropies),
            'max': np.max(entropies)
        }

        print(f"{family:<20} {stats[family]['count']:>8} {stats[family]['mean']:>10.4f} "
              f"{stats[family]['std']:>10.4f} {stats[family]['min']:>10.4f} {stats[family]['max']:>10.4f}")

    # Visualize
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Box plot comparison
    family_names = []
    family_entropies = []
    for family in ['Generic', 'Twin', 'Sophie Germain', 'Safe', 'Mersenne', 'Sparse (≤3 bits)', 'Dense (≥80% bits)']:
        if family in families and families[family]:
            family_names.append(family.replace(' (≤3 bits)', '\n(≤3 bits)').replace(' (≥80% bits)', '\n(≥80% bits)'))
            _, entropies = zip(*families[family])
            family_entropies.append(entropies)

    bp = axes[0, 0].boxplot(family_entropies, labels=family_names, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
    axes[0, 0].set_ylabel('BiEntropy')
    axes[0, 0].set_title('Entropy Distribution by Prime Family')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # Scatter: Generic vs special
    generic_nums, generic_ent = zip(*families['Generic']) if families['Generic'] else ([], [])
    axes[0, 1].scatter(generic_nums, generic_ent, alpha=0.3, s=5, label='Generic', color='gray')

    colors = ['red', 'blue', 'green', 'orange', 'purple']
    for (family, color) in zip(['Mersenne', 'Twin', 'Sophie Germain', 'Sparse (≤3 bits)', 'Dense (≥80% bits)'], colors):
        if families[family]:
            nums, ents = zip(*families[family])
            axes[0, 1].scatter(nums, ents, alpha=0.8, s=20, label=family, color=color)

    axes[0, 1].set_xlabel('Prime p')
    axes[0, 1].set_ylabel('BiEntropy')
    axes[0, 1].set_title('Entropy of Special Primes')
    axes[0, 1].legend(loc='best', fontsize=8)
    axes[0, 1].grid(True, alpha=0.3)

    # Histogram comparison: Mersenne/Sparse vs Generic
    if families['Generic']:
        _, generic_ent = zip(*families['Generic'])
        axes[1, 0].hist(generic_ent, bins=50, alpha=0.5, label='Generic', color='gray', density=True)

    if families['Sparse (≤3 bits)']:
        _, sparse_ent = zip(*families['Sparse (≤3 bits)'])
        axes[1, 0].hist(sparse_ent, bins=30, alpha=0.7, label='Sparse (≤3 bits)', color='red', density=True)

    axes[1, 0].set_xlabel('BiEntropy')
    axes[1, 0].set_ylabel('Density')
    axes[1, 0].set_title('Generic vs Sparse Primes')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Statistics summary
    summary_text = "Key Findings:\n\n"
    if 'Mersenne' in stats and 'Generic' in stats:
        summary_text += f"Mersenne: μ={stats['Mersenne']['mean']:.3f}, σ={stats['Mersenne']['std']:.3f}\n"
        summary_text += f"Generic:  μ={stats['Generic']['mean']:.3f}, σ={stats['Generic']['std']:.3f}\n\n"
        summary_text += f"Mersenne primes have {stats['Mersenne']['mean']/stats['Generic']['mean']:.1%} "
        summary_text += f"of generic entropy\n\n"

    if 'Sparse (≤3 bits)' in stats:
        summary_text += f"Sparse primes: μ={stats['Sparse (≤3 bits)']['mean']:.3f}\n"
        summary_text += "→ Very low entropy (simple binary patterns)\n\n"

    if 'Twin' in stats:
        summary_text += f"Twin primes: μ={stats['Twin']['mean']:.3f}\n"
        summary_text += "→ Similar to generic (no special entropy signature)\n"

    axes[1, 1].text(0.05, 0.95, summary_text, transform=axes[1, 1].transAxes,
                    fontsize=11, verticalalignment='top', family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    axes[1, 1].axis('off')

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/special_primes_entropy.png', dpi=150)
    print("\nSaved visualization to special_primes_entropy.png")

    return stats, families


def find_entropy_outliers(max_n=10000):
    """
    Find primes that don't fit the pattern.
    """
    primes = sieve_of_eratosthenes(max_n)
    prime_entropies = [(p, bientropy(p)) for p in primes]

    mean_entropy = np.mean([be for _, be in prime_entropies])
    std_entropy = np.std([be for _, be in prime_entropies])

    print("\n" + "="*70)
    print("Entropy Outliers (>2σ from mean)")
    print("="*70)

    outliers_low = []
    outliers_high = []

    for p, be in prime_entropies:
        z_score = (be - mean_entropy) / std_entropy
        if z_score < -2:
            outliers_low.append((p, be, z_score))
        elif z_score > 2:
            outliers_high.append((p, be, z_score))

    print(f"\nLow entropy outliers (n={len(outliers_low)}):")
    for p, be, z in sorted(outliers_low, key=lambda x: x[1])[:15]:
        binary = to_binary_string(p)
        pc = popcount(p)
        print(f"{p:>6} | H={be:.4f} | z={z:.2f} | bits={len(binary)} | ones={pc} | {binary}")

    print(f"\nHigh entropy outliers (n={len(outliers_high)}):")
    for p, be, z in sorted(outliers_high, key=lambda x: x[1], reverse=True)[:15]:
        binary = to_binary_string(p)
        pc = popcount(p)
        print(f"{p:>6} | H={be:.4f} | z={z:.2f} | bits={len(binary)} | ones={pc} | {binary}")


if __name__ == "__main__":
    stats, families = analyze_special_families(max_n=10000)

    # Show specific examples
    print("\n" + "="*70)
    print("Example Primes from Each Family")
    print("="*70)

    for family in ['Mersenne', 'Sparse (≤3 bits)', 'Dense (≥80% bits)', 'Twin', 'Generic']:
        if family in families and families[family]:
            print(f"\n{family}:")
            for p, be in families[family][:5]:
                binary = to_binary_string(p)
                print(f"  {p:>6} | H={be:.4f} | {binary}")

    # Find outliers
    find_entropy_outliers(max_n=10000)
