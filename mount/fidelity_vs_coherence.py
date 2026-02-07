"""
FIDELITY VS COHERENCE: THE REAL BOTTLENECK

Key discovery from coherence_threshold.py analysis:
- 13s coherence breakthrough unlocks ZERO new algorithms
- Reason: FIDELITY, not coherence, is the bottleneck
- At 99.9% fidelity, circuits with >1000 gates have fidelity < 0.37

This explores: What fidelity is needed for different algorithm classes?
"""

import numpy as np
import matplotlib.pyplot as plt
from coherence_threshold import ALGORITHMS, CoherenceModel, Algorithm
from typing import List, Tuple
import json
from datetime import datetime


def compute_required_fidelity(circuit_depth: int, min_fidelity: float = 0.5) -> float:
    """
    Compute required per-gate fidelity for given circuit depth

    F_total = F_gate^D ≥ min_fidelity
    F_gate ≥ min_fidelity^(1/D)

    Error per gate: ε = 1 - F_gate ≈ -ln(F_total) / D (for small ε)
    """
    if circuit_depth == 0:
        return 1.0
    return min_fidelity ** (1.0 / circuit_depth)


def compute_error_budget(circuit_depth: int, min_fidelity: float = 0.5) -> float:
    """Error per gate needed to achieve min_fidelity after D gates"""
    f_gate = compute_required_fidelity(circuit_depth, min_fidelity)
    return 1.0 - f_gate


def visualize_fidelity_bottleneck():
    """Show that fidelity, not coherence, is the bottleneck"""

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Required gate fidelity vs circuit depth
    ax = axes[0, 0]

    depths = np.logspace(0, 8, 100)  # 1 to 10^8 gates
    min_fidelities = [0.1, 0.3, 0.5, 0.7, 0.9]

    for min_fid in min_fidelities:
        required = [compute_required_fidelity(int(d), min_fid) for d in depths]
        ax.plot(depths, required, label=f'Target fidelity = {min_fid}', linewidth=2)

    # Mark current technology
    ax.axhline(0.999, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Current: 99.9%')
    ax.axhline(0.9999, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Target: 99.99%')
    ax.axhline(0.99999, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Future: 99.999%')

    ax.set_xscale('log')
    ax.set_xlabel('Circuit Depth (gates)', fontsize=12)
    ax.set_ylabel('Required Per-Gate Fidelity', fontsize=12)
    ax.set_title('Fidelity Requirements: The Real Bottleneck', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(True, alpha=0.3)
    ax.set_ylim([0.9985, 1.0001])

    # Plot 2: Error budget per gate
    ax = axes[0, 1]

    for min_fid in [0.5, 0.7, 0.9]:
        errors = [compute_error_budget(int(d), min_fid) * 1e6 for d in depths]  # in ppm
        ax.plot(depths, errors, label=f'Target fidelity = {min_fid}', linewidth=2)

    # Mark current technology
    ax.axhline(1000, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Current: 0.1%')
    ax.axhline(100, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Target: 0.01%')
    ax.axhline(10, color='blue', linestyle='--', linewidth=2, alpha=0.7, label='Future: 0.001%')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Circuit Depth (gates)', fontsize=12)
    ax.set_ylabel('Error Budget per Gate (ppm)', fontsize=12)
    ax.set_title('Per-Gate Error Budget vs Circuit Depth', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Plot 3: Algorithm feasibility matrix (fidelity × coherence)
    ax = axes[1, 0]

    fidelities = np.linspace(0.999, 0.99999, 50)
    coherence_times = np.logspace(-1, 2, 50)  # 0.1s to 100s

    # For each algorithm category, count how many become feasible
    categories = ['factoring', 'search', 'simulation', 'optimization']

    for i, category in enumerate(categories):
        category_algos = [a for a in ALGORITHMS if a.category == category]
        feasibility = np.zeros((len(fidelities), len(coherence_times)))

        for j, fid in enumerate(fidelities):
            for k, T2 in enumerate(coherence_times):
                model = CoherenceModel(gate_time_us=1.0, gate_fidelity=fid)
                n_feasible = sum(1 for a in category_algos if model.is_feasible(a, T2, safety_factor=3.0)[0])
                feasibility[j, k] = n_feasible

        # Plot contour for this category
        ax = axes[1, i % 2] if i < 2 else axes[1, i % 2]

        # Move plots around
        if i == 0:
            ax = axes[1, 0]
        elif i == 1:
            ax = axes[1, 1]

    # Actually, let's just show ONE comprehensive heatmap
    ax = axes[1, 0]

    # Count total feasible algorithms
    total_feasibility = np.zeros((len(fidelities), len(coherence_times)))

    for j, fid in enumerate(fidelities):
        for k, T2 in enumerate(coherence_times):
            model = CoherenceModel(gate_time_us=1.0, gate_fidelity=fid)
            n_feasible = sum(1 for a in ALGORITHMS if model.is_feasible(a, T2, safety_factor=3.0)[0])
            total_feasibility[j, k] = n_feasible

    im = ax.contourf(coherence_times, fidelities, total_feasibility, levels=15, cmap='RdYlGn')
    ax.set_xscale('log')
    ax.set_xlabel('Coherence Time (s)', fontsize=12)
    ax.set_ylabel('Per-Gate Fidelity', fontsize=12)
    ax.set_title('Algorithm Feasibility Landscape', fontsize=14, fontweight='bold')

    # Mark current technology
    ax.axhline(0.999, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Current fidelity')
    ax.axvline(1.0, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Old coherence')
    ax.axvline(13.0, color='green', linestyle='--', linewidth=2, alpha=0.7, label='Feb 2026 coherence')

    plt.colorbar(im, ax=ax, label='# Feasible Algorithms')
    ax.legend(fontsize=9, loc='lower right')

    # Plot 4: Algorithm positioning in (depth, qubits) space with feasibility
    ax = axes[1, 1]

    # Current technology point
    fid_current = 0.999
    T2_current = 13.0
    model_current = CoherenceModel(gate_time_us=1.0, gate_fidelity=fid_current)

    # Future technology point
    fid_future = 0.9999
    T2_future = 60.0
    model_future = CoherenceModel(gate_time_us=1.0, gate_fidelity=fid_future)

    for category in ['factoring', 'search', 'simulation', 'optimization']:
        algos = [a for a in ALGORITHMS if a.category == category]

        for algo in algos:
            feasible_now = model_current.is_feasible(algo, T2_current, safety_factor=3.0)[0]
            feasible_future = model_future.is_feasible(algo, T2_future, safety_factor=3.0)[0]

            if feasible_now:
                marker = 'o'  # Feasible now
                alpha = 0.8
                size = 100
            elif feasible_future:
                marker = 's'  # Feasible with better tech
                alpha = 0.6
                size = 80
            else:
                marker = 'x'  # Still infeasible
                alpha = 0.4
                size = 60

            ax.scatter(algo.circuit_depth, algo.qubits, marker=marker, s=size,
                      alpha=alpha, label=category if algos[0] == algo else "")

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Circuit Depth (gates)', fontsize=12)
    ax.set_ylabel('Number of Qubits', fontsize=12)
    ax.set_title(f'Algorithm Feasibility Map\n(○=Now[99.9%, 13s], □=Future[99.99%, 60s], ×=Later)',
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('fidelity_vs_coherence.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to fidelity_vs_coherence.png")


def generate_insight_report():
    """Generate key insights about fidelity vs coherence bottleneck"""

    print("\n" + "=" * 80)
    print("KEY INSIGHTS: FIDELITY IS THE BOTTLENECK, NOT COHERENCE")
    print("=" * 80)

    # Technology points
    fid_current = 0.999
    T2_current_old = 1.0
    T2_current_new = 13.0

    fid_needed_1k = compute_required_fidelity(1000, 0.5)
    fid_needed_10k = compute_required_fidelity(10000, 0.5)
    fid_needed_100k = compute_required_fidelity(100000, 0.5)
    fid_needed_1M = compute_required_fidelity(1000000, 0.5)

    print(f"\n📊 REQUIRED FIDELITY FOR DIFFERENT CIRCUIT DEPTHS (target 50% final fidelity):")
    print(f"  1,000 gates   → {fid_needed_1k:.6f} ({(1-fid_needed_1k)*1e6:.1f} ppm error)")
    print(f"  10,000 gates  → {fid_needed_10k:.6f} ({(1-fid_needed_10k)*1e6:.1f} ppm error)")
    print(f"  100,000 gates → {fid_needed_100k:.6f} ({(1-fid_needed_100k)*1e6:.2f} ppm error)")
    print(f"  1,000,000 gates → {fid_needed_1M:.6f} ({(1-fid_needed_1M)*1e6:.3f} ppm error)")

    print(f"\n🔬 CURRENT TECHNOLOGY (Feb 2026):")
    print(f"  Gate fidelity: {fid_current} (1000 ppm error)")
    print(f"  Coherence time: {T2_current_new}s (was {T2_current_old}s)")
    print(f"  Max feasible depth at 50% fidelity: ~693 gates")
    print(f"  Max feasible depth at 10% fidelity: ~2,302 gates")

    # Count algorithms feasible at different tech levels
    model_old = CoherenceModel(gate_time_us=1.0, gate_fidelity=0.999)
    model_new_coherence = CoherenceModel(gate_time_us=1.0, gate_fidelity=0.999)
    model_new_fidelity = CoherenceModel(gate_time_us=1.0, gate_fidelity=0.9999)
    model_future = CoherenceModel(gate_time_us=1.0, gate_fidelity=0.99999)

    n_feasible_old = sum(1 for a in ALGORITHMS if model_old.is_feasible(a, T2_current_old, safety_factor=3.0)[0])
    n_feasible_new_coh = sum(1 for a in ALGORITHMS if model_new_coherence.is_feasible(a, T2_current_new, safety_factor=3.0)[0])
    n_feasible_new_fid = sum(1 for a in ALGORITHMS if model_new_fidelity.is_feasible(a, T2_current_new, safety_factor=3.0)[0])
    n_feasible_future = sum(1 for a in ALGORITHMS if model_future.is_feasible(a, 60.0, safety_factor=3.0)[0])

    print(f"\n💡 IMPACT ANALYSIS:")
    print(f"  2025 tech (99.9%, 1s):        {n_feasible_old}/{len(ALGORITHMS)} algorithms feasible")
    print(f"  2026 coherence boost (99.9%, 13s):  {n_feasible_new_coh}/{len(ALGORITHMS)} algorithms feasible → +{n_feasible_new_coh - n_feasible_old} algorithms")
    print(f"  If fidelity improved (99.99%, 13s):  {n_feasible_new_fid}/{len(ALGORITHMS)} algorithms feasible → +{n_feasible_new_fid - n_feasible_old} algorithms")
    print(f"  Future (99.999%, 60s):        {n_feasible_future}/{len(ALGORITHMS)} algorithms feasible → +{n_feasible_future - n_feasible_old} algorithms")

    print(f"\n🎯 KEY FINDING:")
    if n_feasible_new_fid - n_feasible_old > n_feasible_new_coh - n_feasible_old:
        print(f"  Improving fidelity 99.9%→99.99% unlocks {n_feasible_new_fid - n_feasible_old} algorithms")
        print(f"  Improving coherence 1s→13s unlocks {n_feasible_new_coh - n_feasible_old} algorithms")
        print(f"  CONCLUSION: FIDELITY is {(n_feasible_new_fid - n_feasible_old) / max(1, n_feasible_new_coh - n_feasible_old):.1f}× more impactful than coherence!")

    # Find which algorithms need better fidelity
    print(f"\n📋 ALGORITHMS BLOCKED BY FIDELITY (feasible with 99.99% but not 99.9%):")
    newly_feasible = []
    for algo in ALGORITHMS:
        old_feas = model_new_coherence.is_feasible(algo, T2_current_new, safety_factor=3.0)[0]
        new_feas = model_new_fidelity.is_feasible(algo, T2_current_new, safety_factor=3.0)[0]
        if new_feas and not old_feas:
            newly_feasible.append(algo)
            print(f"  ✓ {algo.name:25s} ({algo.circuit_depth:8d} gates, {algo.qubits:4d} qubits) - {algo.description}")

    print(f"\n🚀 TESTABLE PREDICTIONS:")
    print(f"  1. Improving gate fidelity 99.9% → 99.99% is MORE valuable than coherence 1s → 13s")
    print(f"  2. At current fidelity (99.9%), coherence >1s provides diminishing returns")
    print(f"  3. Shor's algorithm for RSA requires fidelity >99.9999% (< 1 ppm error per gate)")
    print(f"  4. Near-term focus should be: error correction > fidelity > coherence time")
    print(f"  5. \"Quantum advantage\" for chemistry/optimization needs ~99.99% fidelity + 10s coherence")

    print("=" * 80)

    return {
        "timestamp": datetime.now().isoformat(),
        "key_insight": "Fidelity is the bottleneck, not coherence time",
        "impact": {
            "coherence_1s_to_13s": n_feasible_new_coh - n_feasible_old,
            "fidelity_999_to_9999": n_feasible_new_fid - n_feasible_old,
            "fidelity_more_impactful": n_feasible_new_fid > n_feasible_new_coh,
        },
        "required_fidelity": {
            "1k_gates": float(fid_needed_1k),
            "10k_gates": float(fid_needed_10k),
            "100k_gates": float(fid_needed_100k),
            "1M_gates": float(fid_needed_1M),
        },
        "algorithms_unlocked_by_better_fidelity": [
            {"name": a.name, "depth": a.circuit_depth, "qubits": a.qubits, "description": a.description}
            for a in newly_feasible
        ]
    }


if __name__ == "__main__":
    visualize_fidelity_bottleneck()
    report = generate_insight_report()

    with open(f"fidelity_bottleneck_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(report, f, indent=2)
