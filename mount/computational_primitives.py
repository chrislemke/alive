#!/usr/bin/env python3
"""
Computational Primitives: What is "native" to different substrates?

Key insight: Different physical substrates have different natural operations.
- Silicon: Boolean logic, fast deterministic switching
- Molecules: Weighted integration, stochastic dynamics, adaptation
- Biology: Pattern matching, associative memory, robustness

This script analyzes what kinds of computation are EASY vs HARD on each substrate.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import Callable, List, Tuple
import time


@dataclass
class ComputationalPrimitive:
    """
    A basic operation that a substrate can perform.
    """
    name: str
    description: str
    silicon_cost: float  # Relative cost (1.0 = baseline)
    molecular_cost: float
    biological_cost: float

    def display(self):
        print(f"\n{self.name}")
        print(f"  {self.description}")
        print(f"  Silicon:    {'█' * int(self.silicon_cost * 10):20s} {self.silicon_cost:.2f}")
        print(f"  Molecular:  {'█' * int(self.molecular_cost * 10):20s} {self.molecular_cost:.2f}")
        print(f"  Biological: {'█' * int(self.biological_cost * 10):20s} {self.biological_cost:.2f}")


def analyze_primitives():
    """
    Catalog of computational primitives and their relative costs.

    Cost = energy * time * complexity
    1.0 = baseline (easy)
    10.0 = very expensive
    """

    primitives = [
        # LOGIC OPERATIONS
        ComputationalPrimitive(
            "Boolean AND/OR",
            "Two-input logic gate",
            silicon_cost=1.0,      # Native to transistors
            molecular_cost=2.0,    # Requires coupling devices
            biological_cost=3.0    # Requires multiple ion channels
        ),

        ComputationalPrimitive(
            "Exact arithmetic (ADD)",
            "Integer addition with carry",
            silicon_cost=1.5,      # Requires ripple or carry-lookahead
            molecular_cost=8.0,    # Very unnatural (discrete vs analog)
            biological_cost=10.0   # Neurons don't do exact arithmetic
        ),

        ComputationalPrimitive(
            "Comparison (A > B)",
            "Binary comparison of values",
            silicon_cost=2.0,      # Subtraction then sign bit
            molecular_cost=1.5,    # Voltage difference is natural
            biological_cost=1.5    # Lateral inhibition does this
        ),

        # MEMORY OPERATIONS
        ComputationalPrimitive(
            "Random access (RAM)",
            "Read arbitrary address in constant time",
            silicon_cost=1.0,      # Native via address decoding
            molecular_cost=3.0,    # Requires addressing scheme
            biological_cost=5.0    # Brains use content-addressable, not random
        ),

        ComputationalPrimitive(
            "Associative recall",
            "Content-addressable memory (pattern → completion)",
            silicon_cost=5.0,      # Requires search or hash table
            molecular_cost=2.0,    # Hopfield network dynamics are natural
            biological_cost=1.0    # Native to neural circuits
        ),

        ComputationalPrimitive(
            "Sequential access",
            "Stream processing (next, next, next)",
            silicon_cost=1.5,      # Cache-friendly, pipelining
            molecular_cost=2.0,    # Ions flow naturally but slower
            biological_cost=1.5    # Axonal propagation is sequential
        ),

        # LEARNING OPERATIONS
        ComputationalPrimitive(
            "Weight update (discrete)",
            "Set w = new_value exactly",
            silicon_cost=1.0,      # Just memory write
            molecular_cost=5.0,    # Ions don't settle to exact values
            biological_cost=4.0    # Synaptic plasticity is noisy
        ),

        ComputationalPrimitive(
            "Weight update (continuous)",
            "w += δw (gradient-like adjustment)",
            silicon_cost=2.0,      # Requires read-modify-write
            molecular_cost=1.0,    # Ion drift IS continuous adjustment
            biological_cost=1.0    # Synaptic plasticity is continuous
        ),

        ComputationalPrimitive(
            "Hebbian learning",
            "w += pre * post (correlation-based)",
            silicon_cost=3.0,      # Requires multiply-accumulate
            molecular_cost=1.0,    # Natural in redox/ion dynamics
            biological_cost=1.0    # STDP is native
        ),

        ComputationalPrimitive(
            "Backpropagation",
            "Gradient descent with error attribution",
            silicon_cost=2.0,      # Matrix multiplies (good on GPU)
            molecular_cost=7.0,    # Requires non-local signals
            biological_cost=8.0    # Brain doesn't do exact backprop
        ),

        # ANALOG OPERATIONS
        ComputationalPrimitive(
            "Weighted sum",
            "y = Σ(w_i * x_i)",
            silicon_cost=3.0,      # Requires multiply-accumulate units
            molecular_cost=1.0,    # Literal physics (current = Σ conductance * voltage)
            biological_cost=1.0    # Dendritic integration does this
        ),

        ComputationalPrimitive(
            "Nonlinear activation",
            "σ(x) = 1/(1+e^-x) or ReLU",
            silicon_cost=5.0,      # Transcendental functions expensive
            molecular_cost=1.5,    # Saturation is natural (ion equilibrium)
            biological_cost=1.0    # Action potentials are sigmoid-ish
        ),

        ComputationalPrimitive(
            "Temporal integration",
            "y = ∫ x dt (accumulate over time)",
            silicon_cost=3.0,      # Requires accumulator + clock
            molecular_cost=1.0,    # Capacitance/ion accumulation is literal integration
            biological_cost=1.0    # Membrane potential integrates
        ),

        # STOCHASTIC OPERATIONS
        ComputationalPrimitive(
            "Random number generation",
            "True randomness (not PRNG)",
            silicon_cost=4.0,      # Requires thermal noise circuit
            molecular_cost=1.0,    # Thermal fluctuations are free
            biological_cost=1.0    # Ion channel noise is free
        ),

        ComputationalPrimitive(
            "Deterministic guarantee",
            "Same input → exactly same output every time",
            silicon_cost=1.0,      # Native to digital logic
            molecular_cost=5.0,    # Fighting thermal noise
            biological_cost=6.0    # Neurons are inherently noisy
        ),

        # PATTERN OPERATIONS
        ComputationalPrimitive(
            "Template matching",
            "Is input similar to stored pattern?",
            silicon_cost=4.0,      # Requires distance computation
            molecular_cost=2.0,    # Cross-correlation via conductance
            biological_cost=1.5    # Receptive fields do this
        ),

        ComputationalPrimitive(
            "Sparse coding",
            "Represent input as combination of basis",
            silicon_cost=3.0,      # Optimization problem
            molecular_cost=2.0,    # Winner-take-all circuits
            biological_cost=1.0    # V1 does this natively
        ),
    ]

    return primitives


def visualize_computational_landscape():
    """
    Create 2D map of computational primitives in substrate-cost space.
    """
    primitives = analyze_primitives()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    comparisons = [
        ("Silicon", "Molecular", 0, 1, axes[0]),
        ("Silicon", "Biological", 0, 2, axes[1]),
        ("Molecular", "Biological", 1, 2, axes[2]),
    ]

    for name1, name2, idx1, idx2, ax in comparisons:
        costs1 = []
        costs2 = []
        names = []

        for p in primitives:
            cost_list = [p.silicon_cost, p.molecular_cost, p.biological_cost]
            costs1.append(cost_list[idx1])
            costs2.append(cost_list[idx2])
            names.append(p.name)

        # Scatter plot
        colors = []
        for c1, c2 in zip(costs1, costs2):
            if c1 < c2:
                colors.append('#2E86AB')  # Blue: substrate 1 better
            elif c2 < c1:
                colors.append('#A23B72')  # Purple: substrate 2 better
            else:
                colors.append('#888888')  # Gray: equal

        ax.scatter(costs1, costs2, c=colors, s=100, alpha=0.6, edgecolors='black', linewidth=1)

        # Diagonal line (equal cost)
        max_cost = max(max(costs1), max(costs2))
        ax.plot([0, max_cost], [0, max_cost], 'k--', alpha=0.3, linewidth=1)

        # Labels for interesting points
        for i, name in enumerate(names):
            # Only label if cost difference > 2
            if abs(costs1[i] - costs2[i]) > 2:
                ax.annotate(name, (costs1[i], costs2[i]),
                           fontsize=8, alpha=0.7,
                           xytext=(5, 5), textcoords='offset points')

        ax.set_xlabel(f'{name1} Cost', fontsize=12)
        ax.set_ylabel(f'{name2} Cost', fontsize=12)
        ax.set_title(f'{name1} vs {name2}', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        ax.set_xlim(0, max_cost + 0.5)
        ax.set_ylim(0, max_cost + 0.5)

        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#2E86AB', label=f'{name1} better'),
            Patch(facecolor='#A23B72', label=f'{name2} better'),
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/computational_primitives.png', dpi=150)
    print("\n→ Saved: computational_primitives.png")
    plt.close()


def compute_substrate_affinity_scores():
    """
    For common computational tasks, which substrate is most natural?
    """

    tasks = {
        "Database query": {
            "operations": ["Random access", "Comparison", "Boolean AND/OR"],
            "silicon": 1.0,
            "molecular": 2.5,
            "biological": 4.0,
        },
        "Image classification": {
            "operations": ["Weighted sum", "Nonlinear activation", "Template matching"],
            "silicon": 3.0,
            "molecular": 1.5,
            "biological": 1.3,
        },
        "Real-time adaptation": {
            "operations": ["Weight update (continuous)", "Hebbian learning"],
            "silicon": 2.5,
            "molecular": 1.0,
            "biological": 1.0,
        },
        "Cryptography": {
            "operations": ["Exact arithmetic", "Deterministic guarantee", "Boolean AND/OR"],
            "silicon": 1.3,
            "molecular": 7.0,
            "biological": 9.0,
        },
        "Associative memory": {
            "operations": ["Associative recall", "Template matching", "Sparse coding"],
            "silicon": 4.0,
            "molecular": 2.0,
            "biological": 1.2,
        },
        "Gradient descent training": {
            "operations": ["Backpropagation", "Weight update (discrete)", "Exact arithmetic"],
            "silicon": 2.0,
            "molecular": 7.0,
            "biological": 8.0,
        },
    }

    print("\n" + "="*70)
    print("TASK-SUBSTRATE AFFINITY")
    print("="*70)
    print("\nWhich substrate is most natural for different computational tasks?")
    print("(Lower score = more efficient/natural)\n")

    for task, scores in tasks.items():
        ops = scores["operations"]
        s_score = scores["silicon"]
        m_score = scores["molecular"]
        b_score = scores["biological"]

        best = min(s_score, m_score, b_score)

        print(f"\n{task}")
        print(f"  Required operations: {', '.join(ops)}")
        print(f"  Silicon:    {'█' * int(10 - s_score):10s} {s_score:.1f} {'← BEST' if s_score == best else ''}")
        print(f"  Molecular:  {'█' * int(10 - m_score):10s} {m_score:.1f} {'← BEST' if m_score == best else ''}")
        print(f"  Biological: {'█' * int(10 - b_score):10s} {b_score:.1f} {'← BEST' if b_score == best else ''}")


def demonstrate_molecular_advantage():
    """
    Concrete example: implement same computation on silicon vs molecular model
    Show where molecular is actually better.
    """

    print("\n" + "="*70)
    print("CONCRETE EXAMPLE: Pattern Completion Task")
    print("="*70)
    print("\nTask: Given partial pattern, recall full pattern")
    print("This is natural for associative memory (content-addressable)\n")

    # Stored patterns (10 binary patterns of length 8)
    patterns = np.array([
        [1, 1, 0, 0, 1, 1, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0],
        [0, 0, 1, 1, 0, 0, 1, 1],
    ])

    # Query: partial pattern (first 4 bits of pattern 0, rest unknown)
    query = np.array([1, 1, 0, 0, -1, -1, -1, -1])  # -1 = unknown

    print("Stored patterns:")
    for i, p in enumerate(patterns):
        print(f"  Pattern {i}: {p}")
    print(f"\nQuery (partial): {query}  (where -1 = unknown)")

    # SILICON APPROACH: Sequential search
    print("\n--- Silicon Approach (Sequential Search) ---")
    silicon_ops = 0
    best_match = None
    best_score = -1

    for i, pattern in enumerate(patterns):
        score = 0
        for j in range(len(query)):
            if query[j] != -1:  # Only compare known bits
                silicon_ops += 1  # Comparison operation
                if query[j] == pattern[j]:
                    score += 1

        if score > best_score:
            best_score = score
            best_match = i
        silicon_ops += 1  # Score comparison

    print(f"Operations: {silicon_ops}")
    print(f"Best match: Pattern {best_match}: {patterns[best_match]}")
    print(f"Algorithm: Loop through all patterns, count matches")

    # MOLECULAR APPROACH: Parallel weighted sum
    print("\n--- Molecular Approach (Parallel Association) ---")

    # In molecular implementation, query drives conductances
    # Each stored pattern is a "device" with conductance ∝ match
    # All patterns activate in parallel, highest conductance wins

    molecular_ops = 0

    # Create weight matrix (Hopfield-like)
    # Each pattern contributes to associative weights
    W = np.zeros((8, 8))
    for pattern in patterns:
        p = pattern * 2 - 1  # Convert to -1, +1
        W += np.outer(p, p)  # Hebbian rule
        molecular_ops += 8  # Outer product (but happens during learning, not recall)
    W /= len(patterns)

    # Query activation
    query_known = query.copy()
    query_known[query_known == -1] = 0  # Unknown bits = neutral

    # Parallel activation (one matrix multiply)
    activation = W @ query_known
    molecular_ops += 8  # Weighted sum (parallel in hardware)

    # Threshold to binary
    result = (activation > 0).astype(int)

    # Find which stored pattern this matches
    for i, pattern in enumerate(patterns):
        if np.array_equal(result, pattern):
            best_match = i
            break

    print(f"Operations: {molecular_ops} (parallel)")
    print(f"Result: {result}")
    print(f"Matches: Pattern {best_match}")
    print(f"Algorithm: Weighted sum (literal physics in molecular device)")

    print("\n--- Comparison ---")
    print(f"Silicon: {silicon_ops} sequential operations")
    print(f"Molecular: {molecular_ops} parallel operations")
    print(f"Speedup: {silicon_ops / max(molecular_ops, 1):.1f}x (if parallel hardware)")
    print(f"\nKey insight: Molecular devices do weighted sums AS PHYSICS")
    print(f"             Silicon must compute them step-by-step")


def substrate_conclusion():
    """
    Summary of findings about computational primitives
    """

    print("\n" + "="*70)
    print("CONCLUSION: Substrate-Computation Alignment")
    print("="*70)

    conclusion = """
The substrate you compute on determines what's EASY vs HARD:

SILICON (Transistors):
  Natural:    Boolean logic, exact arithmetic, random access, determinism
  Unnatural:  Analog ops, associative memory, continuous learning, stochasticity

  Best for: Databases, crypto, exact simulation, discrete algorithms
  Poor for: Online learning, pattern completion, noisy environments

MOLECULAR (Redox/Ions):
  Natural:    Weighted sums, continuous learning, stochastic dynamics, integration
  Unnatural:  Exact arithmetic, random access, determinism, backpropagation

  Best for: Real-time adaptation, associative memory, analog sensing
  Poor for: Databases, crypto, precise computation

BIOLOGICAL (Neurons):
  Natural:    Pattern matching, associative recall, robustness, sparse coding
  Unnatural:  Exact arithmetic, random access, determinism, precise timing

  Best for: Perception, motor control, context-dependent behavior
  Poor for: Math, databases, deterministic tasks

INSIGHT: There is no "best" substrate — only substrate-task fit.

The question isn't "which is better?" but "which is appropriate for this task?"

Current AI (transformers, CNNs) are designed for SILICON primitives:
  - Matrix multiplication (GPUs are good at this)
  - Discrete weight updates (gradient descent)
  - Deterministic inference (same input → same output)

But many intelligent tasks are more MOLECULAR/BIOLOGICAL in nature:
  - Continuous adaptation to changing environment
  - Robust pattern recognition despite noise
  - Associative recall from partial cues
  - Energy-efficient always-on processing

If we build AI on molecular substrates, we might discover NEW architectures
that are natural to chemistry but awkward on silicon.

Just as quantum computers aren't "better" but solve different problems naturally,
molecular computers aren't "better" but embody different computational primitives.

The future might be HYBRID:
  - Silicon for databases, crypto, exact computation
  - Molecular for learning, adaptation, pattern recognition
  - Quantum for optimization, simulation, search

Different substrates for different cognitive functions.
Like brains use different regions for different tasks.
Future AI might use different physics for different reasoning modes.
    """

    print(conclusion)


def main():
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "   COMPUTATIONAL PRIMITIVES: What's Natural to Each Substrate?".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # Analyze all primitives
    print("\n" + "="*70)
    print("PRIMITIVE OPERATIONS AND THEIR SUBSTRATE COSTS")
    print("="*70)
    primitives = analyze_primitives()
    for p in primitives:
        p.display()

    # Visualize
    print("\n")
    visualize_computational_landscape()

    # Task affinity
    compute_substrate_affinity_scores()

    # Concrete example
    demonstrate_molecular_advantage()

    # Conclusion
    substrate_conclusion()

    print("\n" + "="*70)
    print()


if __name__ == "__main__":
    main()
