#!/usr/bin/env python3
"""
Exploring prime numbers through information theory and entropy.

Based on BiEntropy research (Croll 2013-2020) and recent work on
entropy/periodicity/primality (2025).

Key ideas:
- Binary derivatives reveal structure in numbers
- Shannon entropy measures randomness
- Primes have high entropy (incompressible)
- Composites have low entropy (periodic patterns from factors)
"""

import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
from scipy.stats import entropy as scipy_entropy


def to_binary_string(n):
    """Convert integer to binary string (without '0b' prefix)."""
    return bin(n)[2:]


def binary_derivative(binary_str):
    """
    Compute binary derivative via XOR of adjacent bits.

    Example: 1011 -> 110 (1⊕0=1, 0⊕1=1, 1⊕1=0)

    The derivative reveals periodic structure - fully periodic
    numbers have derivatives that quickly reach zero.
    """
    if len(binary_str) <= 1:
        return ""

    result = []
    for i in range(len(binary_str) - 1):
        # XOR adjacent bits
        xor = int(binary_str[i]) ^ int(binary_str[i + 1])
        result.append(str(xor))

    return ''.join(result)


def all_binary_derivatives(n):
    """
    Compute all binary derivatives until string becomes empty.

    Returns list of derivative strings (not including original).
    """
    derivatives = []
    current = to_binary_string(n)

    while len(current) > 1:
        current = binary_derivative(current)
        if current:  # Don't add empty string
            derivatives.append(current)

    return derivatives


def shannon_entropy(binary_str):
    """
    Shannon entropy of a binary string.

    H = -Σ p(x) log2(p(x))

    For binary: H ∈ [0, 1], where:
    - H=0: all same bit (perfectly ordered)
    - H=1: equal 0s and 1s (maximum disorder)
    """
    if not binary_str:
        return 0.0

    # Count 0s and 1s
    counts = Counter(binary_str)
    total = len(binary_str)

    # Compute probabilities
    probs = [count / total for count in counts.values()]

    # Shannon entropy in base 2
    return scipy_entropy(probs, base=2)


def bientropy(n):
    """
    BiEntropy: weighted average of Shannon entropies of binary derivatives.

    BiEn(n) = Σ w_i * H(d_i)

    where d_i is i-th derivative and w_i is weight (various schemes possible).

    High BiEntropy → disorder → likely prime
    Low BiEntropy → order → composite
    """
    derivatives = all_binary_derivatives(n)

    if not derivatives:
        return 0.0

    # Compute entropy of each derivative
    entropies = [shannon_entropy(d) for d in derivatives]

    # Weighted average (use equal weights for simplicity)
    # Could also use: weights = [1/(i+1) for i in range(len(entropies))]
    return np.mean(entropies)


def tribentropy(n):
    """
    TriEntropy: considers length-normalized entropy.

    Accounts for the fact that longer derivatives can have higher entropy.
    """
    derivatives = all_binary_derivatives(n)

    if not derivatives:
        return 0.0

    # Normalize each entropy by theoretical maximum for that length
    normalized_entropies = []
    for d in derivatives:
        h = shannon_entropy(d)
        # Theoretical max is 1.0 for binary
        normalized_entropies.append(h)

    return np.mean(normalized_entropies)


def is_prime_simple(n):
    """Simple primality test."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(np.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def sieve_of_eratosthenes(limit):
    """Generate all primes up to limit."""
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False

    for i in range(2, int(np.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i*i, limit + 1, i):
                sieve[j] = False

    return [i for i in range(limit + 1) if sieve[i]]


def analyze_entropy_distribution(max_n=1000):
    """
    Analyze BiEntropy distribution for primes vs composites.
    """
    primes = set(sieve_of_eratosthenes(max_n))

    prime_entropies = []
    composite_entropies = []

    for n in range(2, max_n + 1):
        be = bientropy(n)

        if n in primes:
            prime_entropies.append((n, be))
        else:
            composite_entropies.append((n, be))

    return prime_entropies, composite_entropies


def visualize_entropy_distribution(max_n=1000):
    """
    Visualize BiEntropy for primes vs composites.
    """
    print(f"Computing BiEntropy for numbers 2 to {max_n}...")
    prime_ent, comp_ent = analyze_entropy_distribution(max_n)

    prime_nums, prime_vals = zip(*prime_ent)
    comp_nums, comp_vals = zip(*comp_ent)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Scatter plot
    axes[0, 0].scatter(comp_nums, comp_vals, alpha=0.3, s=1, label='Composite', color='red')
    axes[0, 0].scatter(prime_nums, prime_vals, alpha=0.5, s=2, label='Prime', color='blue')
    axes[0, 0].set_xlabel('n')
    axes[0, 0].set_ylabel('BiEntropy')
    axes[0, 0].set_title('BiEntropy: Primes vs Composites')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Histogram
    axes[0, 1].hist(comp_vals, bins=50, alpha=0.6, label='Composite', color='red', density=True)
    axes[0, 1].hist(prime_vals, bins=50, alpha=0.6, label='Prime', color='blue', density=True)
    axes[0, 1].set_xlabel('BiEntropy')
    axes[0, 1].set_ylabel('Density')
    axes[0, 1].set_title('BiEntropy Distribution')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Statistics
    prime_mean = np.mean(prime_vals)
    prime_std = np.std(prime_vals)
    comp_mean = np.mean(comp_vals)
    comp_std = np.std(comp_vals)

    stats_text = f"""
    Primes:     μ={prime_mean:.4f}, σ={prime_std:.4f}
    Composites: μ={comp_mean:.4f}, σ={comp_std:.4f}
    Difference: Δμ={prime_mean - comp_mean:.4f}
    """

    axes[1, 0].text(0.1, 0.5, stats_text, fontsize=12, family='monospace',
                    verticalalignment='center')
    axes[1, 0].axis('off')
    axes[1, 0].set_title('Statistics')

    # Entropy vs log(n) - looking for structure
    axes[1, 1].scatter(np.log(comp_nums), comp_vals, alpha=0.3, s=1, label='Composite', color='red')
    axes[1, 1].scatter(np.log(prime_nums), prime_vals, alpha=0.5, s=2, label='Prime', color='blue')
    axes[1, 1].set_xlabel('log(n)')
    axes[1, 1].set_ylabel('BiEntropy')
    axes[1, 1].set_title('BiEntropy vs log(n)')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/prime_entropy_distribution.png', dpi=150)
    print(f"Saved visualization to prime_entropy_distribution.png")

    return {
        'prime_mean': prime_mean,
        'prime_std': prime_std,
        'comp_mean': comp_mean,
        'comp_std': comp_std,
        'separation': prime_mean - comp_mean
    }


def explore_derivatives(n):
    """
    Deep dive into binary derivatives of a single number.
    """
    print(f"\n{'='*60}")
    print(f"Number: {n} ({'PRIME' if is_prime_simple(n) else 'COMPOSITE'})")
    print(f"{'='*60}")

    binary = to_binary_string(n)
    print(f"Binary: {binary} (length {len(binary)})")

    derivatives = all_binary_derivatives(n)
    print(f"\nBinary derivatives ({len(derivatives)} total):")

    for i, d in enumerate(derivatives):
        h = shannon_entropy(d)
        print(f"  d{i+1}: {d:>20} | entropy: {h:.4f}")

    be = bientropy(n)
    print(f"\nBiEntropy: {be:.4f}")


def find_low_entropy_primes(max_n=10000, count=20):
    """
    Find primes with unusually LOW entropy (counterexamples to hypothesis).
    """
    primes = sieve_of_eratosthenes(max_n)

    prime_entropies = [(p, bientropy(p)) for p in primes]
    prime_entropies.sort(key=lambda x: x[1])

    print(f"\n{'='*60}")
    print(f"Primes with LOWEST BiEntropy (n < {max_n}):")
    print(f"{'='*60}")

    for p, be in prime_entropies[:count]:
        print(f"{p:>6} | BiEntropy: {be:.4f} | Binary: {to_binary_string(p)}")

    return prime_entropies[:count]


def find_high_entropy_composites(max_n=10000, count=20):
    """
    Find composites with unusually HIGH entropy (false positives).
    """
    composites = [n for n in range(4, max_n + 1) if not is_prime_simple(n)]

    comp_entropies = [(c, bientropy(c)) for c in composites]
    comp_entropies.sort(key=lambda x: x[1], reverse=True)

    print(f"\n{'='*60}")
    print(f"Composites with HIGHEST BiEntropy (n < {max_n}):")
    print(f"{'='*60}")

    for c, be in comp_entropies[:count]:
        factors = factorize_simple(c)
        print(f"{c:>6} | BiEntropy: {be:.4f} | Binary: {to_binary_string(c)} | Factors: {factors}")

    return comp_entropies[:count]


def factorize_simple(n):
    """Simple factorization for analysis."""
    factors = []
    d = 2
    temp = n
    while d * d <= temp:
        while temp % d == 0:
            factors.append(d)
            temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    return factors


if __name__ == "__main__":
    print("Prime Numbers and Information Theory")
    print("=" * 60)

    # Example: compare a prime and composite
    explore_derivatives(17)   # Prime
    explore_derivatives(18)   # Composite (2 * 3^2)
    explore_derivatives(127)  # Mersenne prime
    explore_derivatives(128)  # Power of 2

    # Find edge cases
    find_low_entropy_primes(max_n=5000, count=15)
    find_high_entropy_composites(max_n=5000, count=15)

    # Large-scale analysis
    stats = visualize_entropy_distribution(max_n=2000)

    print(f"\n{'='*60}")
    print("Summary Statistics:")
    print(f"{'='*60}")
    for key, val in stats.items():
        print(f"{key:>15}: {val:.4f}")
