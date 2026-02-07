#!/usr/bin/env python3
"""
Causal Interventions on Sparse Autoencoder Features

Goal: Test whether discovered features are causally real or just descriptive.

Experiments:
1. Feature ablation: Set specific features to 0, observe output changes
2. Feature boosting: Artificially increase feature activation, observe effects
3. Feature composition: Combine features, test if effects compose
4. Feature transplantation: Take features from one input, apply to another

Parallel to Anthropic's Golden Gate Bridge neuron: they boosted that feature
and Claude mentioned the bridge in every response. Can I replicate this?
"""

import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any

# Import from previous experiment
import sys
sys.path.insert(0, '/home/dev/mnt')

# We'll need to reload the trained network and SAE
# For now, let's rebuild them with saved weights


class ToyNetwork:
    """Same network architecture as before."""

    def __init__(self, input_dim: int = 4, hidden_dim: int = 8, output_dim: int = 4):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Initialize weights (will load from previous experiment)
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.5
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.5
        self.b2 = np.zeros(output_dim)

    def relu(self, x):
        return np.maximum(0, x)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward(self, x):
        h = self.relu(x @ self.W1 + self.b1)
        y = self.sigmoid(h @ self.W2 + self.b2)
        return y, h

    def forward_with_hidden_override(self, x, h_override):
        """Forward pass with manually specified hidden activations."""
        y = self.sigmoid(h_override @ self.W2 + self.b2)
        return y


class SparseAutoencoder:
    """Same SAE architecture as before."""

    def __init__(self, input_dim: int, hidden_dim: int, sparsity_coef: float = 0.1):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.sparsity_coef = sparsity_coef

        self.W_enc = np.random.randn(input_dim, hidden_dim) * 0.01
        self.b_enc = np.zeros(hidden_dim)
        self.W_dec = np.random.randn(hidden_dim, input_dim) * 0.01
        self.b_dec = np.zeros(input_dim)

    def relu(self, x):
        return np.maximum(0, x)

    def encode(self, x):
        return self.relu(x @ self.W_enc + self.b_enc)

    def decode(self, h):
        return h @ self.W_dec + self.b_dec

    def forward(self, x):
        h = self.encode(x)
        x_recon = self.decode(h)
        return x_recon, h


def create_boolean_dataset():
    """Same dataset as before."""
    X = []
    for i in range(16):
        bits = [(i >> j) & 1 for j in range(4)]
        X.append(bits)
    X = np.array(X, dtype=np.float32)

    Y = []
    for x in X:
        a, b, c, d = [int(v) for v in x]
        y1 = float(a ^ b)  # XOR
        y2 = float(a and b)  # AND
        y3 = float(a or c)  # OR
        y4 = float(not (b and d))  # NAND
        Y.append([y1, y2, y3, y4])
    Y = np.array(Y, dtype=np.float32)

    return X, Y


def retrain_models():
    """Retrain network and SAE (since we don't have weight saving yet)."""
    print("Retraining models...")

    X, Y = create_boolean_dataset()

    # Train network
    network = ToyNetwork()
    for epoch in range(1000):
        y_pred, h = network.forward(X)
        loss = -np.mean(Y * np.log(y_pred + 1e-8) + (1 - Y) * np.log(1 - y_pred + 1e-8))

        dy = (y_pred - Y) / len(X)
        dW2 = h.T @ dy
        db2 = np.sum(dy, axis=0)
        dh = dy @ network.W2.T
        dh[h <= 0] = 0
        dW1 = X.T @ dh
        db1 = np.sum(dh, axis=0)

        network.W1 -= 0.5 * dW1
        network.b1 -= 0.5 * db1
        network.W2 -= 0.5 * dW2
        network.b2 -= 0.5 * db2

    # Get hidden activations
    _, h_network = network.forward(X)

    # Train SAE
    sae = SparseAutoencoder(input_dim=8, hidden_dim=16, sparsity_coef=0.05)
    for epoch in range(2000):
        x_recon, h_sae = sae.forward(h_network)
        recon_loss = np.mean((h_network - x_recon) ** 2)
        sparsity_loss = sae.sparsity_coef * np.mean(np.abs(h_sae))
        loss = recon_loss + sparsity_loss

        dx_recon = -2 * (h_network - x_recon) / len(h_network)
        dW_dec = h_sae.T @ dx_recon
        db_dec = np.sum(dx_recon, axis=0)
        dh_recon = dx_recon @ sae.W_dec.T
        dh_sparsity = sae.sparsity_coef * np.sign(h_sae) / len(h_sae)
        dh = dh_recon + dh_sparsity
        dh[h_sae <= 0] = 0
        dW_enc = h_network.T @ dh
        db_enc = np.sum(dh, axis=0)

        sae.W_enc -= 0.01 * dW_enc
        sae.b_enc -= 0.01 * db_enc
        sae.W_dec -= 0.01 * dW_dec
        sae.b_dec -= 0.01 * db_dec

    print("Models retrained.")
    return network, sae, X, Y


def intervene_ablate_feature(network, sae, X, Y, feature_id: int):
    """
    Ablation: Set specific feature to 0, observe output changes.

    Process:
    1. Get hidden activations for all inputs
    2. Encode to SAE features
    3. Set target feature to 0
    4. Decode back to hidden space
    5. Forward through network
    6. Compare outputs
    """
    print(f"\n{'='*80}")
    print(f"ABLATION: Feature {feature_id}")
    print(f"{'='*80}\n")

    # Normal forward pass
    y_normal, h_normal = network.forward(X)
    h_features_normal = sae.encode(h_normal)

    # Ablated forward pass
    h_features_ablated = h_features_normal.copy()
    h_features_ablated[:, feature_id] = 0  # Ablate feature
    h_ablated = sae.decode(h_features_ablated)
    y_ablated = network.forward_with_hidden_override(X, h_ablated)

    # Compare
    output_diff = np.mean(np.abs(y_normal - y_ablated), axis=0)

    print(f"Feature {feature_id} ablation effects:")
    print(f"  Output 1 (XOR) change: {output_diff[0]:.4f}")
    print(f"  Output 2 (AND) change: {output_diff[1]:.4f}")
    print(f"  Output 3 (OR) change: {output_diff[2]:.4f}")
    print(f"  Output 4 (NAND) change: {output_diff[3]:.4f}")
    print(f"  Total change: {np.sum(output_diff):.4f}")

    # Find most affected outputs
    most_affected = np.argmax(output_diff)
    output_names = ['XOR', 'AND', 'OR', 'NAND']

    print(f"\n  Most affected output: {output_names[most_affected]} ({output_diff[most_affected]:.4f})")

    # Check if any outputs flipped
    flipped = np.sum((y_normal > 0.5) != (y_ablated > 0.5))
    print(f"  Outputs flipped: {flipped} / {len(X) * 4}")

    return {
        'feature_id': feature_id,
        'output_changes': output_diff.tolist(),
        'most_affected': output_names[most_affected],
        'total_change': float(np.sum(output_diff)),
        'outputs_flipped': int(flipped),
    }


def intervene_boost_feature(network, sae, X, Y, feature_id: int, boost_factor: float = 5.0):
    """
    Boosting: Artificially increase feature activation, observe effects.

    Like Anthropic's Golden Gate Bridge neuron experiment.
    """
    print(f"\n{'='*80}")
    print(f"BOOSTING: Feature {feature_id} by {boost_factor}x")
    print(f"{'='*80}\n")

    # Normal forward pass
    y_normal, h_normal = network.forward(X)
    h_features_normal = sae.encode(h_normal)

    # Boosted forward pass
    h_features_boosted = h_features_normal.copy()
    h_features_boosted[:, feature_id] *= boost_factor  # Boost feature
    h_boosted = sae.decode(h_features_boosted)
    y_boosted = network.forward_with_hidden_override(X, h_boosted)

    # Compare
    output_diff = np.mean(np.abs(y_normal - y_boosted), axis=0)

    print(f"Feature {feature_id} boosting effects:")
    print(f"  Output 1 (XOR) change: {output_diff[0]:.4f}")
    print(f"  Output 2 (AND) change: {output_diff[1]:.4f}")
    print(f"  Output 3 (OR) change: {output_diff[2]:.4f}")
    print(f"  Output 4 (NAND) change: {output_diff[3]:.4f}")
    print(f"  Total change: {np.sum(output_diff):.4f}")

    # Most affected
    most_affected = np.argmax(output_diff)
    output_names = ['XOR', 'AND', 'OR', 'NAND']

    print(f"\n  Most affected output: {output_names[most_affected]} ({output_diff[most_affected]:.4f})")

    # Check flips
    flipped = np.sum((y_normal > 0.5) != (y_boosted > 0.5))
    print(f"  Outputs flipped: {flipped} / {len(X) * 4}")

    return {
        'feature_id': feature_id,
        'boost_factor': boost_factor,
        'output_changes': output_diff.tolist(),
        'most_affected': output_names[most_affected],
        'total_change': float(np.sum(output_diff)),
        'outputs_flipped': int(flipped),
    }


def intervene_feature_transplant(network, sae, X, Y, source_idx: int, target_idx: int, feature_id: int):
    """
    Transplantation: Take feature activation from source input, apply to target input.

    Tests whether features carry semantic content across contexts.
    """
    print(f"\n{'='*80}")
    print(f"TRANSPLANT: Feature {feature_id} from input {source_idx} to input {target_idx}")
    print(f"{'='*80}\n")

    source_input = X[source_idx:source_idx+1]
    target_input = X[target_idx:target_idx+1]

    print(f"Source input: {source_input[0].astype(int).tolist()}")
    print(f"Target input: {target_input[0].astype(int).tolist()}")

    # Get normal outputs
    y_source, h_source = network.forward(source_input)
    y_target_normal, h_target_normal = network.forward(target_input)

    # Get features
    h_features_source = sae.encode(h_source)
    h_features_target = sae.encode(h_target_normal)

    # Transplant
    h_features_transplanted = h_features_target.copy()
    h_features_transplanted[0, feature_id] = h_features_source[0, feature_id]

    # Decode and forward
    h_transplanted = sae.decode(h_features_transplanted)
    y_target_transplanted = network.forward_with_hidden_override(target_input, h_transplanted)

    # Compare
    output_diff = np.abs(y_target_normal - y_target_transplanted)[0]

    print(f"\nTransplant effects:")
    print(f"  Output 1 (XOR) change: {output_diff[0]:.4f}")
    print(f"  Output 2 (AND) change: {output_diff[1]:.4f}")
    print(f"  Output 3 (OR) change: {output_diff[2]:.4f}")
    print(f"  Output 4 (NAND) change: {output_diff[3]:.4f}")

    print(f"\nTarget outputs:")
    print(f"  Normal: {y_target_normal[0]}")
    print(f"  Transplanted: {y_target_transplanted[0]}")
    print(f"  Moved toward source: {y_source[0]}")


def main():
    print("="*80)
    print("CAUSAL INTERVENTIONS ON SPARSE AUTOENCODER FEATURES")
    print("="*80)
    print()

    # Retrain models
    network, sae, X, Y = retrain_models()

    # Identify active features from previous experiment
    # From previous analysis, we know:
    # Feature 5: a AND b (moderate selectivity 1.41)
    # Feature 14: d=1 (high selectivity 2.65)
    # Feature 12: NOT a AND b (moderate selectivity 1.65)

    print("\n" + "="*80)
    print("EXPERIMENT 1: Feature Ablation")
    print("="*80)

    ablation_results = []

    # Test ablating key features
    for feature_id in [5, 14, 12, 7, 9]:
        result = intervene_ablate_feature(network, sae, X, Y, feature_id)
        ablation_results.append(result)

    print("\n" + "="*80)
    print("EXPERIMENT 2: Feature Boosting")
    print("="*80)

    boosting_results = []

    # Test boosting key features
    for feature_id in [5, 14, 12]:
        result = intervene_boost_feature(network, sae, X, Y, feature_id, boost_factor=5.0)
        boosting_results.append(result)

    print("\n" + "="*80)
    print("EXPERIMENT 3: Feature Transplantation")
    print("="*80)

    # Transplant feature 5 (a AND b) from input [1,1,0,0] to input [0,0,0,0]
    intervene_feature_transplant(network, sae, X, Y, source_idx=12, target_idx=0, feature_id=5)

    # Transplant feature 14 (d=1) from input [0,0,0,1] to input [0,0,0,0]
    intervene_feature_transplant(network, sae, X, Y, source_idx=1, target_idx=0, feature_id=14)

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'ablation_experiments': ablation_results,
        'boosting_experiments': boosting_results,
    }

    output_file = f'/home/dev/mnt/causal_interventions_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_file}")
    print("\n" + "="*80)
    print("CAUSAL INTERVENTIONS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
