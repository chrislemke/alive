#!/usr/bin/env python3
"""
Sparse Autoencoder Experiment: Mechanistic Interpretability on a Toy System

Goal: Build a small neural network that learns a non-trivial task, then train
a sparse autoencoder on its hidden activations to see if interpretable features emerge.

Inspired by Anthropic's work on monosemanticity and dictionary learning.

Task: Learn XOR-like logical relationships (multiple boolean functions)
This creates polysemantic neurons (neurons activate for multiple unrelated reasons)
Then use SAE to disentangle into monosemantic features.
"""

import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Tuple, Any


class ToyNetwork:
    """Small feedforward network that learns boolean functions."""

    def __init__(self, input_dim: int = 4, hidden_dim: int = 8, output_dim: int = 4):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim

        # Initialize weights
        self.W1 = np.random.randn(input_dim, hidden_dim) * 0.5
        self.b1 = np.zeros(hidden_dim)
        self.W2 = np.random.randn(hidden_dim, output_dim) * 0.5
        self.b2 = np.zeros(output_dim)

    def relu(self, x):
        return np.maximum(0, x)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))

    def forward(self, x):
        """Forward pass, returns (output, hidden_activations)."""
        h = self.relu(x @ self.W1 + self.b1)
        y = self.sigmoid(h @ self.W2 + self.b2)
        return y, h

    def train(self, X, Y, epochs=1000, lr=0.1):
        """Train on data X -> Y."""
        losses = []

        for epoch in range(epochs):
            # Forward pass
            y_pred, h = self.forward(X)

            # Loss (binary cross-entropy)
            loss = -np.mean(Y * np.log(y_pred + 1e-8) + (1 - Y) * np.log(1 - y_pred + 1e-8))
            losses.append(loss)

            # Backward pass
            dy = (y_pred - Y) / len(X)
            dW2 = h.T @ dy
            db2 = np.sum(dy, axis=0)

            dh = dy @ self.W2.T
            dh[h <= 0] = 0  # ReLU gradient

            dW1 = X.T @ dh
            db1 = np.sum(dh, axis=0)

            # Update
            self.W1 -= lr * dW1
            self.b1 -= lr * db1
            self.W2 -= lr * dW2
            self.b2 -= lr * db2

            if epoch % 100 == 0:
                print(f"Epoch {epoch}: Loss = {loss:.4f}")

        return losses


class SparseAutoencoder:
    """Sparse autoencoder for disentangling polysemantic neurons."""

    def __init__(self, input_dim: int, hidden_dim: int, sparsity_coef: float = 0.1):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim  # Typically larger than input (overcomplete)
        self.sparsity_coef = sparsity_coef

        # Initialize weights
        self.W_enc = np.random.randn(input_dim, hidden_dim) * 0.01
        self.b_enc = np.zeros(hidden_dim)
        self.W_dec = np.random.randn(hidden_dim, input_dim) * 0.01
        self.b_dec = np.zeros(input_dim)

    def relu(self, x):
        return np.maximum(0, x)

    def encode(self, x):
        """Encode input into sparse representation."""
        return self.relu(x @ self.W_enc + self.b_enc)

    def decode(self, h):
        """Decode sparse representation back to input."""
        return h @ self.W_dec + self.b_dec

    def forward(self, x):
        """Full forward pass."""
        h = self.encode(x)
        x_recon = self.decode(h)
        return x_recon, h

    def train(self, X, epochs=1000, lr=0.01):
        """Train to reconstruct X with sparse hidden activations."""
        losses = []
        sparsities = []

        for epoch in range(epochs):
            # Forward pass
            x_recon, h = self.forward(X)

            # Reconstruction loss
            recon_loss = np.mean((X - x_recon) ** 2)

            # Sparsity loss (L1 penalty on activations)
            sparsity_loss = self.sparsity_coef * np.mean(np.abs(h))

            # Total loss
            loss = recon_loss + sparsity_loss
            losses.append(loss)
            sparsities.append(np.mean(h > 0))

            # Backward pass
            dx_recon = -2 * (X - x_recon) / len(X)
            dW_dec = h.T @ dx_recon
            db_dec = np.sum(dx_recon, axis=0)

            dh_recon = dx_recon @ self.W_dec.T
            dh_sparsity = self.sparsity_coef * np.sign(h) / len(X)
            dh = dh_recon + dh_sparsity
            dh[h <= 0] = 0  # ReLU gradient

            dW_enc = X.T @ dh
            db_enc = np.sum(dh, axis=0)

            # Update
            self.W_enc -= lr * dW_enc
            self.b_enc -= lr * db_enc
            self.W_dec -= lr * dW_dec
            self.b_dec -= lr * db_dec

            if epoch % 100 == 0:
                print(f"Epoch {epoch}: Loss = {loss:.4f}, Recon = {recon_loss:.4f}, "
                      f"Sparsity = {sparsity_loss:.4f}, Active = {sparsities[-1]:.2%}")

        return losses, sparsities


def create_boolean_dataset():
    """
    Create dataset of boolean functions.
    4 inputs: a, b, c, d
    4 outputs: a XOR b, c AND d, a OR c, NOT(b AND d)

    These functions require different logical operations, so neurons will
    become polysemantic (activate for different reasons in different contexts).
    """
    # All 16 possible 4-bit inputs
    X = []
    for i in range(16):
        bits = [(i >> j) & 1 for j in range(4)]
        X.append(bits)
    X = np.array(X, dtype=np.float32)

    # Compute outputs
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


def analyze_features(sae, network, X):
    """Analyze what each SAE feature represents."""
    # Get network hidden activations
    _, h_network = network.forward(X)

    # Get SAE features
    h_sae = sae.encode(h_network)

    # For each SAE feature, find which inputs activate it most
    feature_analysis = []

    for i in range(sae.hidden_dim):
        activations = h_sae[:, i]

        # Skip dead features
        if np.max(activations) < 0.01:
            feature_analysis.append({
                'feature_id': i,
                'status': 'dead',
                'max_activation': float(np.max(activations)),
            })
            continue

        # Find top activating inputs
        top_k = 3
        top_indices = np.argsort(activations)[-top_k:][::-1]

        top_patterns = []
        for idx in top_indices:
            pattern = X[idx].astype(int).tolist()
            activation = float(activations[idx])
            top_patterns.append({
                'input': pattern,
                'activation': activation,
            })

        # Compute selectivity: how concentrated is activation?
        # High selectivity = activates for few specific inputs
        # Low selectivity = activates broadly
        selectivity = np.std(activations) / (np.mean(activations) + 1e-8)

        feature_analysis.append({
            'feature_id': i,
            'status': 'active',
            'max_activation': float(np.max(activations)),
            'mean_activation': float(np.mean(activations)),
            'selectivity': float(selectivity),
            'top_patterns': top_patterns,
        })

    return feature_analysis


def main():
    print("=" * 80)
    print("SPARSE AUTOENCODER EXPERIMENT: Mechanistic Interpretability on Toy System")
    print("=" * 80)
    print()

    # Create dataset
    print("Creating boolean function dataset...")
    X, Y = create_boolean_dataset()
    print(f"Dataset: {len(X)} examples, {X.shape[1]} inputs, {Y.shape[1]} outputs")
    print()

    # Train network
    print("Training toy network on boolean functions...")
    network = ToyNetwork(input_dim=4, hidden_dim=8, output_dim=4)
    losses = network.train(X, Y, epochs=1000, lr=0.5)
    print()

    # Test network
    y_pred, h_network = network.forward(X)
    accuracy = np.mean((y_pred > 0.5) == Y)
    print(f"Network accuracy: {accuracy:.2%}")
    print()

    # Get hidden activations for all inputs
    print("Extracting hidden activations...")
    _, h_network = network.forward(X)
    print(f"Hidden activations shape: {h_network.shape}")
    print(f"Mean activation: {np.mean(h_network):.3f}")
    print(f"Sparsity (zero activations): {np.mean(h_network == 0):.2%}")
    print()

    # Train sparse autoencoder
    print("Training sparse autoencoder on hidden activations...")
    print("(Using overcomplete representation: 8 neurons -> 16 features)")
    sae = SparseAutoencoder(input_dim=8, hidden_dim=16, sparsity_coef=0.05)
    sae_losses, sae_sparsities = sae.train(h_network, epochs=2000, lr=0.01)
    print()

    # Test reconstruction
    h_recon, h_sae = sae.forward(h_network)
    recon_error = np.mean((h_network - h_recon) ** 2)
    print(f"Final reconstruction error: {recon_error:.4f}")
    print(f"Final SAE sparsity (active features): {np.mean(h_sae > 0):.2%}")
    print()

    # Analyze features
    print("Analyzing learned features...")
    feature_analysis = analyze_features(sae, network, X)

    # Count feature types
    active_features = [f for f in feature_analysis if f['status'] == 'active']
    dead_features = [f for f in feature_analysis if f['status'] == 'dead']

    print(f"Active features: {len(active_features)}")
    print(f"Dead features: {len(dead_features)}")
    print()

    # Show top features by selectivity
    print("Most selective features (monosemantic candidates):")
    active_features.sort(key=lambda f: f['selectivity'], reverse=True)

    for f in active_features[:5]:
        print(f"\nFeature {f['feature_id']}:")
        print(f"  Selectivity: {f['selectivity']:.2f}")
        print(f"  Max activation: {f['max_activation']:.3f}")
        print(f"  Top activating inputs:")
        for p in f['top_patterns']:
            print(f"    {p['input']} -> {p['activation']:.3f}")

    # Save results
    results = {
        'timestamp': datetime.now().isoformat(),
        'network': {
            'architecture': {'input': 4, 'hidden': 8, 'output': 4},
            'accuracy': float(accuracy),
        },
        'sae': {
            'architecture': {'input': 8, 'hidden': 16},
            'final_reconstruction_error': float(recon_error),
            'final_sparsity': float(np.mean(h_sae > 0)),
        },
        'features': {
            'active': len(active_features),
            'dead': len(dead_features),
            'analysis': feature_analysis,
        },
    }

    output_file = f'/home/dev/mnt/sae_experiment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to {output_file}")
    print("\n" + "=" * 80)
    print("EXPERIMENT COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
