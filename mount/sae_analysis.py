#!/usr/bin/env python3
"""
Deeper analysis of learned SAE features.

Goal: Determine what logical concepts each feature represents.
"""

import json
import numpy as np


def load_results():
    """Load experimental results."""
    with open('/home/dev/mnt/sae_experiment_20260207_084755.json', 'r') as f:
        return json.load(f)


def analyze_feature_logic(feature_analysis):
    """
    For each active feature, determine what logical function it might represent.
    """
    print("=" * 80)
    print("FEATURE LOGIC ANALYSIS")
    print("=" * 80)
    print()

    # Get all possible inputs (4-bit)
    all_inputs = []
    for i in range(16):
        bits = [(i >> j) & 1 for j in range(4)]
        all_inputs.append(bits)

    for feature in feature_analysis:
        if feature['status'] == 'dead':
            continue

        feature_id = feature['feature_id']
        print(f"Feature {feature_id}:")
        print(f"  Selectivity: {feature['selectivity']:.2f}")
        print(f"  Max activation: {feature['max_activation']:.3f}")
        print()

        # Get activations for top patterns
        top_inputs = [p['input'] for p in feature['top_patterns']]

        # Try to identify logical pattern
        print("  Top activating inputs:")
        for inp in top_inputs[:3]:
            a, b, c, d = inp
            print(f"    a={a} b={b} c={c} d={d}")

        # Test various hypotheses
        hypotheses = []

        # Single bit
        for bit_name, bit_idx in [('a', 0), ('b', 1), ('c', 2), ('d', 3)]:
            if all(inp[bit_idx] == 1 for inp in top_inputs):
                hypotheses.append(f"{bit_name}=1")
            elif all(inp[bit_idx] == 0 for inp in top_inputs):
                hypotheses.append(f"{bit_name}=0")

        # Two-bit conjunctions
        if all(inp[0] == 1 and inp[1] == 1 for inp in top_inputs):
            hypotheses.append("a AND b")
        if all(inp[0] == 1 and inp[2] == 1 for inp in top_inputs):
            hypotheses.append("a AND c")
        if all(inp[0] == 1 and inp[3] == 1 for inp in top_inputs):
            hypotheses.append("a AND d")
        if all(inp[1] == 1 and inp[2] == 1 for inp in top_inputs):
            hypotheses.append("b AND c")
        if all(inp[1] == 1 and inp[3] == 1 for inp in top_inputs):
            hypotheses.append("b AND d")
        if all(inp[2] == 1 and inp[3] == 1 for inp in top_inputs):
            hypotheses.append("c AND d")

        # Negations
        if all(inp[0] == 1 and inp[1] == 0 for inp in top_inputs):
            hypotheses.append("a AND NOT b")
        if all(inp[0] == 0 and inp[1] == 1 for inp in top_inputs):
            hypotheses.append("NOT a AND b")
        if all(inp[0] == 0 and inp[1] == 0 for inp in top_inputs):
            hypotheses.append("NOT a AND NOT b")

        if hypotheses:
            print(f"\n  Possible interpretations: {', '.join(hypotheses)}")
        else:
            print(f"\n  Interpretation: Complex/unclear")

        print()
        print("-" * 80)
        print()


def compare_to_ground_truth():
    """
    Compare learned features to the actual boolean functions the network learned.

    Ground truth functions:
    - Output 1: a XOR b
    - Output 2: a AND b
    - Output 3: a OR c
    - Output 4: NOT(b AND d)
    """
    print("=" * 80)
    print("GROUND TRUTH COMPARISON")
    print("=" * 80)
    print()
    print("The network learned these functions:")
    print("  Output 1: a XOR b")
    print("  Output 2: a AND b")
    print("  Output 3: a OR c")
    print("  Output 4: NOT(b AND d)")
    print()
    print("Question: Did the SAE discover features corresponding to these functions?")
    print("Or did it find something else (intermediate representations)?")
    print()


def monosemanticity_score(feature_analysis):
    """
    Compute how monosemantic the features are.
    Higher selectivity = more monosemantic (activates for specific concept)
    Lower selectivity = more polysemantic (activates for multiple concepts)
    """
    print("=" * 80)
    print("MONOSEMANTICITY ANALYSIS")
    print("=" * 80)
    print()

    active_features = [f for f in feature_analysis if f['status'] == 'active']
    dead_features = [f for f in feature_analysis if f['status'] == 'dead']

    selectivities = [f['selectivity'] for f in active_features]

    print(f"Total features: {len(feature_analysis)}")
    print(f"Active features: {len(active_features)}")
    print(f"Dead features: {len(dead_features)}")
    print()
    print(f"Selectivity statistics:")
    print(f"  Mean: {np.mean(selectivities):.2f}")
    print(f"  Median: {np.median(selectivities):.2f}")
    print(f"  Min: {np.min(selectivities):.2f}")
    print(f"  Max: {np.max(selectivities):.2f}")
    print()
    print("Interpretation:")
    print("  Selectivity > 2.0: Highly monosemantic (activates for very specific inputs)")
    print("  Selectivity 1.0-2.0: Moderately monosemantic")
    print("  Selectivity < 1.0: Polysemantic (activates broadly)")
    print()

    # Categorize
    highly_mono = [f for f in active_features if f['selectivity'] > 2.0]
    moderately_mono = [f for f in active_features if 1.0 <= f['selectivity'] <= 2.0]
    polysemantic = [f for f in active_features if f['selectivity'] < 1.0]

    print(f"Highly monosemantic: {len(highly_mono)} ({len(highly_mono)/len(active_features)*100:.1f}%)")
    print(f"Moderately monosemantic: {len(moderately_mono)} ({len(moderately_mono)/len(active_features)*100:.1f}%)")
    print(f"Polysemantic: {len(polysemantic)} ({len(polysemantic)/len(active_features)*100:.1f}%)")
    print()


def main():
    results = load_results()
    feature_analysis = results['features']['analysis']

    compare_to_ground_truth()
    monosemanticity_score(feature_analysis)
    analyze_feature_logic(feature_analysis)


if __name__ == '__main__':
    main()
