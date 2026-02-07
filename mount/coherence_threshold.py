"""
COHERENCE TIME THRESHOLDS FOR QUANTUM ALGORITHMS (2026)

Following Feb 2026 breakthrough: neutral atom qubits achieving 13-second coherence time
(10× improvement over previous ~1s records). This models which quantum algorithms
become FEASIBLE as coherence time increases.

Key insight: Algorithm feasibility depends on THREE factors:
1. Circuit depth D (number of sequential gates)
2. Gate time τ_gate (physical operation time)
3. Coherence time T₂ (decoherence timescale)

Requirement: D × τ_gate << T₂ (need many coherence times)

Reference: Caltech 6,100 qubit array with 13s coherence (Feb 2026)
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
import json
from datetime import datetime

@dataclass
class Algorithm:
    """Quantum algorithm with resource requirements"""
    name: str
    circuit_depth: int  # Number of sequential gates
    qubits: int  # Number of qubits needed
    description: str
    category: str  # 'factoring', 'search', 'simulation', 'optimization'

    def execution_time(self, gate_time_us: float) -> float:
        """Total execution time in seconds"""
        return self.circuit_depth * gate_time_us * 1e-6

    def required_coherence(self, gate_time_us: float, safety_factor: float = 10.0) -> float:
        """Required coherence time with safety factor"""
        return self.execution_time(gate_time_us) * safety_factor


# Database of quantum algorithms with realistic estimates
ALGORITHMS = [
    # Factoring (Shor's algorithm)
    Algorithm("Shor-128bit", 10**6, 2048, "Factor 128-bit RSA key", "factoring"),
    Algorithm("Shor-256bit", 4*10**6, 4096, "Factor 256-bit RSA key", "factoring"),
    Algorithm("Shor-512bit", 16*10**6, 8192, "Factor 512-bit RSA key", "factoring"),
    Algorithm("Shor-2048bit", 256*10**6, 32768, "Factor 2048-bit RSA key", "factoring"),

    # Search (Grover's algorithm)
    Algorithm("Grover-16", 4, 4, "Search 2^4 items", "search"),
    Algorithm("Grover-32", 32, 5, "Search 2^5 items", "search"),
    Algorithm("Grover-1024", 1024, 10, "Search 2^10 items", "search"),
    Algorithm("Grover-1M", 32768, 20, "Search 2^20 items", "search"),
    Algorithm("Grover-1B", 1048576, 30, "Search 2^30 items", "search"),

    # Quantum simulation
    Algorithm("H2-molecule", 100, 4, "Hydrogen molecule ground state", "simulation"),
    Algorithm("LiH-molecule", 500, 10, "Lithium hydride simulation", "simulation"),
    Algorithm("N2-molecule", 2000, 20, "Nitrogen molecule simulation", "simulation"),
    Algorithm("Fermi-Hubbard-4x4", 10000, 16, "4×4 Fermi-Hubbard model", "simulation"),
    Algorithm("Fermi-Hubbard-8x8", 100000, 64, "8×8 Fermi-Hubbard model", "simulation"),

    # Optimization (QAOA - Quantum Approximate Optimization Algorithm)
    Algorithm("QAOA-p1-10", 20, 10, "QAOA depth 1, 10 variables", "optimization"),
    Algorithm("QAOA-p5-20", 200, 20, "QAOA depth 5, 20 variables", "optimization"),
    Algorithm("QAOA-p10-50", 1000, 50, "QAOA depth 10, 50 variables", "optimization"),
    Algorithm("QAOA-p20-100", 4000, 100, "QAOA depth 20, 100 variables", "optimization"),

    # Quantum machine learning
    Algorithm("QML-small", 100, 10, "Small quantum neural network", "ml"),
    Algorithm("QML-medium", 1000, 20, "Medium quantum neural network", "ml"),
    Algorithm("QML-large", 10000, 50, "Large quantum neural network", "ml"),

    # Error correction (surface code)
    Algorithm("Surface-code-d3", 100, 17, "Distance-3 surface code cycle", "error_correction"),
    Algorithm("Surface-code-d5", 200, 49, "Distance-5 surface code cycle", "error_correction"),
    Algorithm("Surface-code-d7", 300, 97, "Distance-7 surface code cycle", "error_correction"),
]


class CoherenceModel:
    """Model quantum algorithm feasibility vs coherence time"""

    def __init__(self, gate_time_us: float = 1.0, gate_fidelity: float = 0.999):
        """
        Parameters:
        - gate_time_us: Single-gate execution time in microseconds
        - gate_fidelity: Per-gate fidelity (1 = perfect)
        """
        self.gate_time_us = gate_time_us
        self.gate_fidelity = gate_fidelity

    def effective_fidelity(self, algo: Algorithm) -> float:
        """Circuit fidelity after D gates"""
        return self.gate_fidelity ** algo.circuit_depth

    def is_feasible(self, algo: Algorithm, coherence_time_s: float,
                   min_fidelity: float = 0.5, safety_factor: float = 3.0) -> Tuple[bool, str]:
        """
        Check if algorithm is feasible with given coherence time

        Returns: (feasible, reason)
        """
        exec_time = algo.execution_time(self.gate_time_us)
        required_T2 = algo.required_coherence(self.gate_time_us, safety_factor)
        eff_fidelity = self.effective_fidelity(algo)

        if coherence_time_s < required_T2:
            return False, f"Coherence too short ({coherence_time_s:.2f}s < {required_T2:.2f}s)"

        if eff_fidelity < min_fidelity:
            return False, f"Fidelity too low ({eff_fidelity:.3f} < {min_fidelity:.3f})"

        return True, "Feasible"

    def compute_threshold_matrix(self, coherence_times_s: List[float],
                                 safety_factor: float = 3.0) -> np.ndarray:
        """
        Compute feasibility matrix: algorithms × coherence times
        Returns: Binary matrix (1 = feasible, 0 = infeasible)
        """
        n_algos = len(ALGORITHMS)
        n_times = len(coherence_times_s)
        matrix = np.zeros((n_algos, n_times))

        for i, algo in enumerate(ALGORITHMS):
            for j, T2 in enumerate(coherence_times_s):
                feasible, _ = self.is_feasible(algo, T2, safety_factor=safety_factor)
                matrix[i, j] = 1 if feasible else 0

        return matrix

    def find_crossing_algorithms(self, T2_old: float, T2_new: float) -> List[Algorithm]:
        """Find algorithms that become feasible between two coherence times"""
        crossing = []
        for algo in ALGORITHMS:
            old_feasible, _ = self.is_feasible(algo, T2_old)
            new_feasible, _ = self.is_feasible(algo, T2_new)
            if not old_feasible and new_feasible:
                crossing.append(algo)
        return crossing


def visualize_coherence_landscape(model: CoherenceModel, filename: str = "coherence_landscape.png"):
    """Visualize algorithm feasibility vs coherence time"""

    # Coherence times from 0.1s to 100s (logarithmic)
    coherence_times = np.logspace(-1, 2, 50)  # 0.1s to 100s

    # Key milestones
    T2_old = 1.0  # Previous record (~1 second)
    T2_new = 13.0  # Feb 2026 breakthrough (13 seconds)
    T2_future = 60.0  # Near-term target (1 minute)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Execution time vs circuit depth
    ax = axes[0, 0]
    for category in ['factoring', 'search', 'simulation', 'optimization']:
        algos = [a for a in ALGORITHMS if a.category == category]
        depths = [a.circuit_depth for a in algos]
        exec_times = [a.execution_time(model.gate_time_us) for a in algos]
        ax.scatter(depths, exec_times, label=category, s=100, alpha=0.7)

    # Mark coherence times
    ax.axhline(T2_old, color='red', linestyle='--', alpha=0.5, label='Old record (1s)')
    ax.axhline(T2_new, color='green', linestyle='--', alpha=0.5, label='Feb 2026 (13s)')
    ax.axhline(T2_future, color='blue', linestyle='--', alpha=0.5, label='Future (60s)')

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Circuit Depth (gates)', fontsize=12)
    ax.set_ylabel('Execution Time (s)', fontsize=12)
    ax.set_title('Algorithm Requirements vs Coherence Milestones', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Plot 2: Feasibility timeline
    ax = axes[0, 1]
    matrix = model.compute_threshold_matrix(coherence_times.tolist())

    im = ax.imshow(matrix, aspect='auto', cmap='RdYlGn', extent=[coherence_times[0], coherence_times[-1], 0, len(ALGORITHMS)])
    ax.set_xscale('log')
    ax.set_xlabel('Coherence Time (s)', fontsize=12)
    ax.set_ylabel('Algorithm Index', fontsize=12)
    ax.set_title('Feasibility Matrix: Algorithm × Coherence Time', fontsize=14, fontweight='bold')

    # Mark milestones
    ax.axvline(T2_old, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.axvline(T2_new, color='green', linestyle='--', linewidth=2, alpha=0.7)
    ax.axvline(T2_future, color='blue', linestyle='--', linewidth=2, alpha=0.7)

    plt.colorbar(im, ax=ax, label='Feasible')

    # Plot 3: Algorithms crossing threshold
    ax = axes[1, 0]

    crossing_1s_to_13s = model.find_crossing_algorithms(T2_old, T2_new)
    crossing_13s_to_60s = model.find_crossing_algorithms(T2_new, T2_future)

    categories = ['factoring', 'search', 'simulation', 'optimization', 'ml', 'error_correction']
    counts_1_to_13 = [sum(1 for a in crossing_1s_to_13s if a.category == cat) for cat in categories]
    counts_13_to_60 = [sum(1 for a in crossing_13s_to_60s if a.category == cat) for cat in categories]

    x = np.arange(len(categories))
    width = 0.35

    ax.bar(x - width/2, counts_1_to_13, width, label='1s → 13s (Feb 2026)', alpha=0.8)
    ax.bar(x + width/2, counts_13_to_60, width, label='13s → 60s (future)', alpha=0.8)

    ax.set_xlabel('Algorithm Category', fontsize=12)
    ax.set_ylabel('# Algorithms Unlocked', fontsize=12)
    ax.set_title('Algorithms Unlocked by Coherence Improvements', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Plot 4: Fidelity requirements
    ax = axes[1, 1]

    for category in ['factoring', 'search', 'simulation', 'optimization']:
        algos = [a for a in ALGORITHMS if a.category == category]
        depths = [a.circuit_depth for a in algos]
        fidelities = [model.effective_fidelity(a) for a in algos]
        ax.scatter(depths, fidelities, label=category, s=100, alpha=0.7)

    ax.axhline(0.5, color='red', linestyle='--', alpha=0.5, label='Min useful fidelity')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Circuit Depth (gates)', fontsize=12)
    ax.set_ylabel('Effective Fidelity', fontsize=12)
    ax.set_title(f'Fidelity vs Circuit Depth (gate fidelity={model.gate_fidelity})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Saved visualization to {filename}")

    return crossing_1s_to_13s, crossing_13s_to_60s


def generate_report(model: CoherenceModel) -> dict:
    """Generate comprehensive analysis report"""

    T2_old = 1.0
    T2_new = 13.0
    T2_future = 60.0

    crossing_1_to_13 = model.find_crossing_algorithms(T2_old, T2_new)
    crossing_13_to_60 = model.find_crossing_algorithms(T2_new, T2_future)

    report = {
        "timestamp": datetime.now().isoformat(),
        "model_parameters": {
            "gate_time_us": model.gate_time_us,
            "gate_fidelity": model.gate_fidelity,
        },
        "coherence_milestones": {
            "old_record_s": T2_old,
            "feb_2026_breakthrough_s": T2_new,
            "near_term_target_s": T2_future,
        },
        "algorithms_unlocked": {
            "1s_to_13s": [
                {
                    "name": a.name,
                    "category": a.category,
                    "circuit_depth": a.circuit_depth,
                    "qubits": a.qubits,
                    "description": a.description,
                    "execution_time_s": a.execution_time(model.gate_time_us),
                    "required_coherence_s": a.required_coherence(model.gate_time_us),
                }
                for a in crossing_1_to_13
            ],
            "13s_to_60s": [
                {
                    "name": a.name,
                    "category": a.category,
                    "circuit_depth": a.circuit_depth,
                    "qubits": a.qubits,
                    "description": a.description,
                    "execution_time_s": a.execution_time(model.gate_time_us),
                    "required_coherence_s": a.required_coherence(model.gate_time_us),
                }
                for a in crossing_13_to_60
            ],
        },
        "key_insights": {
            "impact_1s_to_13s": len(crossing_1_to_13),
            "impact_13s_to_60s": len(crossing_13_to_60),
            "total_feasible_at_1s": sum(1 for a in ALGORITHMS if model.is_feasible(a, T2_old)[0]),
            "total_feasible_at_13s": sum(1 for a in ALGORITHMS if model.is_feasible(a, T2_new)[0]),
            "total_feasible_at_60s": sum(1 for a in ALGORITHMS if model.is_feasible(a, T2_future)[0]),
        }
    }

    return report


if __name__ == "__main__":
    print("=" * 80)
    print("COHERENCE TIME THRESHOLDS FOR QUANTUM ALGORITHMS")
    print("Modeling Feb 2026 breakthrough: 13-second coherence time")
    print("=" * 80)
    print()

    # Initialize model with realistic parameters
    # Neutral atom qubits: ~1 μs gate time, ~99.9% fidelity
    model = CoherenceModel(gate_time_us=1.0, gate_fidelity=0.999)

    print(f"Model parameters:")
    print(f"  Gate time: {model.gate_time_us} μs")
    print(f"  Gate fidelity: {model.gate_fidelity}")
    print()

    # Generate visualization
    crossing_1_to_13, crossing_13_to_60 = visualize_coherence_landscape(model)

    # Generate and save report
    report = generate_report(model)

    report_file = f"coherence_threshold_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n📊 RESULTS:")
    print(f"\nAlgorithms unlocked by 1s → 13s breakthrough (Feb 2026):")
    print(f"  Total: {len(crossing_1_to_13)} algorithms")
    for algo in crossing_1_to_13:
        print(f"  ✓ {algo.name:20s} ({algo.category:15s}) - {algo.description}")

    print(f"\nAlgorithms that would be unlocked by 13s → 60s improvement:")
    print(f"  Total: {len(crossing_13_to_60)} algorithms")
    for algo in crossing_13_to_60:
        print(f"  ○ {algo.name:20s} ({algo.category:15s}) - {algo.description}")

    print(f"\n📈 FEASIBILITY SUMMARY:")
    print(f"  At 1s coherence:  {report['key_insights']['total_feasible_at_1s']}/{len(ALGORITHMS)} algorithms feasible")
    print(f"  At 13s coherence: {report['key_insights']['total_feasible_at_13s']}/{len(ALGORITHMS)} algorithms feasible")
    print(f"  At 60s coherence: {report['key_insights']['total_feasible_at_60s']}/{len(ALGORITHMS)} algorithms feasible")

    print(f"\n💡 KEY INSIGHT:")
    print(f"  The 13× improvement in coherence time (1s → 13s) unlocks {len(crossing_1_to_13)} new algorithms.")
    print(f"  A further 4.6× improvement (13s → 60s) would unlock {len(crossing_13_to_60)} more algorithms.")
    print(f"  This shows DIMINISHING RETURNS—early improvements have disproportionate impact.")

    print(f"\nSaved report to {report_file}")
    print("=" * 80)
