#!/usr/bin/env python3
"""
Visualize the topology of primes in entropy-gap space.

Can we see structure by plotting (entropy, gap) for each prime?
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from prime_entropy import bientropy, sieve_of_eratosthenes, to_binary_string


def visualize_prime_topology(max_n=10000):
    """
    Plot each prime in (entropy, gap) space.
    """
    primes = sieve_of_eratosthenes(max_n)

    # Compute entropy and gaps
    data = []
    for i in range(len(primes) - 1):
        p = primes[i]
        h = bientropy(p)
        gap = primes[i+1] - p

        data.append((p, h, gap))

    # Separate into arrays
    prime_vals, entropies, gaps = zip(*data)

    # Create visualizations
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # Main scatter: entropy vs gap (colored by log(prime))
    ax1 = fig.add_subplot(gs[0:2, 0:2])
    scatter = ax1.scatter(entropies, gaps, c=np.log10(prime_vals),
                         cmap='viridis', alpha=0.6, s=10, edgecolors='none')
    ax1.set_xlabel('BiEntropy')
    ax1.set_ylabel('Gap to Next Prime')
    ax1.set_title('Prime Topology: Entropy vs Gap')
    ax1.set_ylim(0, 200)
    ax1.grid(True, alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax1, label='log₁₀(prime)')

    # Mark special regions
    ax1.axvline(x=0.3, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Structural boundary')
    ax1.axvline(x=0.6, color='orange', linestyle='--', alpha=0.5, linewidth=2, label='Generic boundary')
    ax1.legend(loc='upper right')

    # Marginal: entropy distribution
    ax2 = fig.add_subplot(gs[0:2, 2])
    ax2.hist(entropies, bins=50, orientation='horizontal', color='blue', alpha=0.6, edgecolor='black')
    ax2.set_ylabel('BiEntropy')
    ax2.set_xlabel('Count')
    ax2.set_title('Entropy\nDistribution')
    ax2.set_ylim(ax1.get_ylim())
    ax2.grid(True, alpha=0.3, axis='y')

    # Marginal: gap distribution
    ax3 = fig.add_subplot(gs[2, 0:2])
    ax3.hist(gaps, bins=50, color='green', alpha=0.6, edgecolor='black')
    ax3.set_xlabel('Gap to Next Prime')
    ax3.set_ylabel('Count')
    ax3.set_title('Gap Distribution')
    ax3.set_xlim(0, 200)
    ax3.grid(True, alpha=0.3, axis='x')

    # Stats box
    ax4 = fig.add_subplot(gs[2, 2])

    # Compute statistics for regions
    structural = [(h, g) for h, g in zip(entropies, gaps) if h < 0.3]
    transition = [(h, g) for h, g in zip(entropies, gaps) if 0.3 <= h < 0.6]
    generic = [(h, g) for h, g in zip(entropies, gaps) if h >= 0.6]

    stats_text = f"""TOPOLOGY STATS
(n={len(data)} primes)

Structural (H<0.3):
  Count: {len(structural)}
  Mean gap: {np.mean([g for _, g in structural]) if structural else 0:.1f}

Transition (0.3≤H<0.6):
  Count: {len(transition)}
  Mean gap: {np.mean([g for _, g in transition]) if transition else 0:.1f}

Generic (H≥0.6):
  Count: {len(generic)}
  Mean gap: {np.mean([g for _, g in generic]) if generic else 0:.1f}

Correlation(H,gap):
  r = {np.corrcoef(entropies, gaps)[0,1]:.4f}
"""

    ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    ax4.axis('off')

    plt.savefig('/home/dev/mnt/prime_topology.png', dpi=200, bbox_inches='tight')
    print("Saved prime_topology.png")

    return data


def analyze_clusters(max_n=10000):
    """
    Look for clustering patterns in entropy-gap space.
    """
    primes = sieve_of_eratosthenes(max_n)

    data = []
    for i in range(len(primes) - 1):
        p = primes[i]
        h = bientropy(p)
        gap = primes[i+1] - p
        data.append((p, h, gap))

    # Find "deserts" - regions with few primes
    print("\n" + "="*70)
    print("Clustering Analysis")
    print("="*70)

    # Divide into grid
    h_bins = np.linspace(0, 1, 11)
    gap_bins = [0, 5, 10, 20, 50, 100, 200, 500, 1000, 5000]

    grid = {}
    for (p, h, gap) in data:
        h_idx = np.digitize([h], h_bins)[0]
        gap_idx = np.digitize([gap], gap_bins)[0]

        key = (h_idx, gap_idx)
        if key not in grid:
            grid[key] = []
        grid[key].append(p)

    # Find dense and sparse regions
    print("\nDense regions (>50 primes):")
    for key, primes_in_cell in sorted(grid.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        h_idx, gap_idx = key
        h_range = f"{h_bins[h_idx-1]:.1f}-{h_bins[min(h_idx, len(h_bins)-1)]:.1f}"
        gap_range = f"{gap_bins[gap_idx-1]:.0f}-{gap_bins[min(gap_idx, len(gap_bins)-1)]:.0f}"
        print(f"  H ∈ [{h_range}], Gap ∈ [{gap_range}]: {len(primes_in_cell)} primes")

    print("\nSparse regions (<5 primes in high-gap zones):")
    for key, primes_in_cell in grid.items():
        h_idx, gap_idx = key
        if gap_idx >= 5 and len(primes_in_cell) < 5 and len(primes_in_cell) > 0:
            h_range = f"{h_bins[h_idx-1]:.1f}-{h_bins[min(h_idx, len(h_bins)-1)]:.1f}"
            gap_range = f"{gap_bins[gap_idx-1]:.0f}-{gap_bins[min(gap_idx, len(gap_bins)-1)]:.0f}"
            print(f"  H ∈ [{h_range}], Gap ∈ [{gap_range}]: {len(primes_in_cell)} primes - {primes_in_cell[:5]}")


def find_anomalous_primes(max_n=10000):
    """
    Find primes that are anomalous in entropy-gap space.
    """
    primes = sieve_of_eratosthenes(max_n)

    data = []
    for i in range(len(primes) - 1):
        p = primes[i]
        h = bientropy(p)
        gap = primes[i+1] - p
        data.append((p, h, gap))

    print("\n" + "="*70)
    print("Anomalous Primes")
    print("="*70)

    # High gap with high entropy (unusual - should be structural)
    print("\nHigh entropy + Large gap (>50):")
    anomalies = [(p, h, gap) for p, h, gap in data if h > 0.7 and gap > 50]
    for p, h, gap in sorted(anomalies, key=lambda x: x[2], reverse=True)[:10]:
        binary = to_binary_string(p)
        print(f"  {p:>6} | H={h:.4f} | gap={gap:>3} | {binary}")

    # Low gap with low entropy (unusual - structural should have large gaps)
    print("\nLow entropy + Small gap (<10):")
    anomalies = [(p, h, gap) for p, h, gap in data if h < 0.4 and gap < 10]
    for p, h, gap in sorted(anomalies, key=lambda x: x[1])[:10]:
        binary = to_binary_string(p)
        print(f"  {p:>6} | H={h:.4f} | gap={gap:>3} | {binary}")


if __name__ == "__main__":
    print("="*70)
    print("Prime Topology in Entropy-Gap Space")
    print("="*70)

    data = visualize_prime_topology(max_n=10000)
    analyze_clusters(max_n=10000)
    find_anomalous_primes(max_n=10000)

    print("\n" + "="*70)
    print("Analysis complete. Check prime_topology.png for visualization.")
    print("="*70)
