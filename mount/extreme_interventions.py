#!/usr/bin/env python3
"""
Extreme Causal Interventions - Testing limits of feature manipulation

Since mild interventions had little effect, try more extreme manipulations:
1. Ablate ALL features except one - does single feature suffice?
2. Massive boosting (100x) - can we break the network?
3. Random feature injection - add noise to feature space
4. Feature permutation - swap feature identities
"""

import numpy as np
from causal_interventions import retrain_models, create_boolean_dataset


def intervene_isolate_single_feature(network, sae, X, Y, feature_id: int):
    """Keep only ONE feature active, zero out all others."""
    print(f"\n{'='*80}")
    print(f"ISOLATION: Keep only feature {feature_id}, zero all others")
    print(f"{'='*80}\n")

    # Normal
    y_normal, h_normal = network.forward(X)
    accuracy_normal = np.mean((y_normal > 0.5) == Y)

    # Isolated
    h_features = sae.encode(h_normal)
    h_features_isolated = np.zeros_like(h_features)
    h_features_isolated[:, feature_id] = h_features[:, feature_id]  # Keep only this feature

    h_isolated = sae.decode(h_features_isolated)
    y_isolated = network.forward_with_hidden_override(X, h_isolated)
    accuracy_isolated = np.mean((y_isolated > 0.5) == Y)

    print(f"Accuracy with all features: {accuracy_normal:.2%}")
    print(f"Accuracy with only feature {feature_id}: {accuracy_isolated:.2%}")
    print(f"Degradation: {(accuracy_normal - accuracy_isolated):.2%}")

    return accuracy_normal, accuracy_isolated


def intervene_massive_boost(network, sae, X, Y, feature_id: int, boost: float = 100.0):
    """Boost feature by 100x - can we break the network?"""
    print(f"\n{'='*80}")
    print(f"MASSIVE BOOST: Feature {feature_id} by {boost}x")
    print(f"{'='*80}\n")

    # Normal
    y_normal, h_normal = network.forward(X)

    # Massively boosted
    h_features = sae.encode(h_normal)
    h_features_boosted = h_features.copy()
    h_features_boosted[:, feature_id] *= boost

    h_boosted = sae.decode(h_features_boosted)
    y_boosted = network.forward_with_hidden_override(X, h_boosted)

    # Check saturation
    print(f"Normal output range: [{y_normal.min():.4f}, {y_normal.max():.4f}]")
    print(f"Boosted output range: [{y_boosted.min():.4f}, {y_boosted.max():.4f}]")

    # Count saturated outputs
    saturated = np.sum((y_boosted < 0.01) | (y_boosted > 0.99))
    total = y_boosted.size
    print(f"Saturated outputs: {saturated}/{total} ({saturated/total:.1%})")

    # Accuracy change
    accuracy_normal = np.mean((y_normal > 0.5) == Y)
    accuracy_boosted = np.mean((y_boosted > 0.5) == Y)
    print(f"\nAccuracy normal: {accuracy_normal:.2%}")
    print(f"Accuracy boosted: {accuracy_boosted:.2%}")


def intervene_random_noise(network, sae, X, Y, noise_scale: float = 1.0):
    """Add random noise to feature space."""
    print(f"\n{'='*80}")
    print(f"RANDOM NOISE: scale {noise_scale}")
    print(f"{'='*80}\n")

    # Normal
    y_normal, h_normal = network.forward(X)
    accuracy_normal = np.mean((y_normal > 0.5) == Y)

    # With noise
    h_features = sae.encode(h_normal)
    noise = np.random.randn(*h_features.shape) * noise_scale
    h_features_noisy = np.maximum(0, h_features + noise)  # Keep ReLU constraint

    h_noisy = sae.decode(h_features_noisy)
    y_noisy = network.forward_with_hidden_override(X, h_noisy)
    accuracy_noisy = np.mean((y_noisy > 0.5) == Y)

    print(f"Accuracy without noise: {accuracy_normal:.2%}")
    print(f"Accuracy with noise (scale {noise_scale}): {accuracy_noisy:.2%}")
    print(f"Degradation: {(accuracy_normal - accuracy_noisy):.2%}")


def intervene_bypass_sae(network, sae, X, Y):
    """Compare: use SAE features vs. direct hidden activations."""
    print(f"\n{'='*80}")
    print(f"BYPASS TEST: SAE features vs. direct hidden activations")
    print(f"{'='*80}\n")

    # Direct (no SAE)
    y_direct, h_direct = network.forward(X)
    accuracy_direct = np.mean((y_direct > 0.5) == Y)

    # Through SAE (encode then decode)
    h_features = sae.encode(h_direct)
    h_reconstructed = sae.decode(h_features)
    y_reconstructed = network.forward_with_hidden_override(X, h_reconstructed)
    accuracy_reconstructed = np.mean((y_reconstructed > 0.5) == Y)

    # Reconstruction error
    recon_error = np.mean((h_direct - h_reconstructed) ** 2)

    print(f"Accuracy (direct hidden): {accuracy_direct:.2%}")
    print(f"Accuracy (through SAE): {accuracy_reconstructed:.2%}")
    print(f"Reconstruction error: {recon_error:.6f}")
    print(f"\nConclusion: SAE adds {recon_error:.6f} MSE but preserves {accuracy_reconstructed:.1%} accuracy")


def main():
    print("="*80)
    print("EXTREME CAUSAL INTERVENTIONS")
    print("="*80)

    network, sae, X, Y = retrain_models()

    # Test 1: Isolate single features
    print("\n" + "="*80)
    print("TEST 1: Feature Isolation (keep only ONE feature)")
    print("="*80)

    for feature_id in [5, 14, 12]:
        intervene_isolate_single_feature(network, sae, X, Y, feature_id)

    # Test 2: Massive boosting
    print("\n" + "="*80)
    print("TEST 2: Massive Feature Boosting (100x)")
    print("="*80)

    for feature_id in [5, 14, 12]:
        intervene_massive_boost(network, sae, X, Y, feature_id, boost=100.0)

    # Test 3: Random noise
    print("\n" + "="*80)
    print("TEST 3: Random Noise in Feature Space")
    print("="*80)

    for noise_scale in [0.5, 1.0, 2.0]:
        intervene_random_noise(network, sae, X, Y, noise_scale)

    # Test 4: Bypass SAE
    print("\n" + "="*80)
    print("TEST 4: SAE vs. Direct Hidden Activations")
    print("="*80)

    intervene_bypass_sae(network, sae, X, Y)

    print("\n" + "="*80)
    print("EXTREME INTERVENTIONS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
