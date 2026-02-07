#!/usr/bin/env python3
"""
Quantum Measurement Simulator
==============================

Explores the measurement problem through simulation:
1. Decoherence and basis selection
2. Born rule emergence from branching
3. Observer states in superposition
4. Environment-induced measurement

Not a textbook QM calculator, but an investigation of WHY measurement works.
"""

import numpy as np
from typing import Tuple, List, Dict
import json
from datetime import datetime


class QuantumState:
    """Represents a quantum state in arbitrary dimensions"""

    def __init__(self, amplitudes: np.ndarray):
        """
        Args:
            amplitudes: Complex amplitudes (will be normalized)
        """
        self.amplitudes = np.array(amplitudes, dtype=complex)
        self.normalize()

    def normalize(self):
        """Normalize the state vector"""
        norm = np.linalg.norm(self.amplitudes)
        if norm > 0:
            self.amplitudes /= norm

    def measure_in_basis(self, basis_states: List[np.ndarray]) -> Tuple[int, 'QuantumState']:
        """
        Measure in a given basis.

        Returns:
            (outcome_index, collapsed_state)
        """
        # Project onto each basis state
        projections = []
        probabilities = []

        for basis in basis_states:
            # Inner product
            projection = np.dot(np.conj(basis), self.amplitudes)
            projections.append(projection)
            probabilities.append(abs(projection)**2)

        # Normalize probabilities (should sum to 1, but numerical errors)
        probabilities = np.array(probabilities)
        probabilities /= probabilities.sum()

        # Sample according to Born rule
        outcome = np.random.choice(len(basis_states), p=probabilities)

        # Collapse to outcome state
        collapsed = QuantumState(basis_states[outcome])

        return outcome, collapsed

    def evolve_unitary(self, hamiltonian: np.ndarray, time: float):
        """Evolve under unitary operator U = exp(-iHt)"""
        U = np.linalg.matrix_power(
            np.eye(len(self.amplitudes)) - 1j * hamiltonian * time,
            1
        )
        # Better: use actual matrix exponential
        from scipy.linalg import expm
        U = expm(-1j * hamiltonian * time)
        self.amplitudes = U @ self.amplitudes
        self.normalize()

    def density_matrix(self) -> np.ndarray:
        """Return density matrix ρ = |ψ⟩⟨ψ|"""
        return np.outer(self.amplitudes, np.conj(self.amplitudes))

    def __repr__(self):
        return f"QuantumState({self.amplitudes})"


class Environment:
    """Represents an environment that can decohere a system"""

    def __init__(self, n_states: int, coupling_strength: float = 0.1):
        """
        Args:
            n_states: Number of environment states
            coupling_strength: How strongly system couples to environment
        """
        self.n_states = n_states
        self.coupling_strength = coupling_strength
        self.state = QuantumState(np.random.randn(n_states) + 1j*np.random.randn(n_states))

    def entangle_with_system(self, system_state: QuantumState) -> np.ndarray:
        """
        Create entanglement between system and environment.

        Returns combined density matrix showing decoherence.
        """
        # Simplified decoherence model:
        # Each system state couples to different environment states
        # |0⟩|env_0⟩ and |1⟩|env_1⟩ where env_0 ⊥ env_1

        n_sys = len(system_state.amplitudes)
        n_env = self.n_states

        # For 2-level system, create orthogonal environment states
        if n_sys == 2:
            # System state: α|0⟩ + β|1⟩
            alpha, beta = system_state.amplitudes[0], system_state.amplitudes[1]

            # Orthogonal environment states (simplified - just use basis states)
            env_0 = np.zeros(n_env, dtype=complex)
            env_0[0] = 1  # |env_0⟩ = |0⟩_env

            env_1 = np.zeros(n_env, dtype=complex)
            env_1[1] = 1  # |env_1⟩ = |1⟩_env

            # After interaction: α|0⟩|env_0⟩ + β|1⟩|env_1⟩
            # This creates entanglement
            state_00 = np.kron(np.array([1, 0]), env_0)  # |0⟩|env_0⟩
            state_11 = np.kron(np.array([0, 1]), env_1)  # |1⟩|env_1⟩

            entangled_state = alpha * state_00 + beta * state_11

            # Density matrix of combined system
            rho_combined = np.outer(entangled_state, np.conj(entangled_state))

            # Trace out environment to get reduced density matrix
            rho_system = self._partial_trace_env(rho_combined, n_sys, n_env)

            return rho_system

        # Fallback for other dimensions
        return system_state.density_matrix()

    def _partial_trace_env(self, rho_combined: np.ndarray, n_sys: int, n_env: int) -> np.ndarray:
        """Trace out environment degrees of freedom"""
        rho_system = np.zeros((n_sys, n_sys), dtype=complex)

        for i in range(n_sys):
            for j in range(n_sys):
                for k in range(n_env):
                    idx1 = i * n_env + k
                    idx2 = j * n_env + k
                    rho_system[i, j] += rho_combined[idx1, idx2]

        return rho_system


class MeasurementSimulator:
    """Simulates measurement process and explores interpretations"""

    def __init__(self):
        self.results = {
            'decoherence_tests': [],
            'born_rule_tests': [],
            'basis_preference_tests': [],
            'observer_branching_tests': []
        }

    def test_decoherence_basis_selection(self) -> Dict:
        """
        Test how decoherence selects a preferred basis.

        The environment couples to certain observables, making
        their eigenbasis the 'pointer basis'.
        """
        print("\n=== DECOHERENCE BASIS SELECTION ===")

        # Initial superposition in computational basis
        system = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])

        print(f"Initial state: |+⟩ = (|0⟩ + |1⟩)/√2")
        print(f"Density matrix (pure):")
        rho_initial = system.density_matrix()
        print(rho_initial)
        print(f"Off-diagonal (coherence): {abs(rho_initial[0,1]):.4f}")

        # Environment interaction
        env = Environment(n_states=10, coupling_strength=1.0)
        rho_decohered = env.entangle_with_system(system)

        print(f"\nAfter environment coupling:")
        print(rho_decohered)
        print(f"Off-diagonal (coherence): {abs(rho_decohered[0,1]):.4f}")

        result = {
            'initial_coherence': abs(rho_initial[0,1]),
            'final_coherence': abs(rho_decohered[0,1]),
            'coherence_loss': abs(rho_initial[0,1]) - abs(rho_decohered[0,1]),
            'interpretation': 'Environment destroys off-diagonal terms, selecting pointer basis'
        }

        self.results['decoherence_tests'].append(result)
        return result

    def test_born_rule_statistics(self, n_trials: int = 10000) -> Dict:
        """
        Verify Born rule: P(outcome) = |⟨outcome|ψ⟩|²

        This is GIVEN in standard QM. But WHY?
        """
        print(f"\n=== BORN RULE STATISTICS ({n_trials} trials) ===")

        # State with known probabilities
        alpha = 0.6
        beta = 0.8
        system = QuantumState([alpha, beta])

        expected_prob_0 = abs(alpha)**2
        expected_prob_1 = abs(beta)**2

        print(f"State: |ψ⟩ = {alpha:.2f}|0⟩ + {beta:.2f}|1⟩")
        print(f"Expected P(0) = {expected_prob_0:.4f}")
        print(f"Expected P(1) = {expected_prob_1:.4f}")

        # Measure many times
        outcomes = []
        basis = [np.array([1, 0]), np.array([0, 1])]

        for _ in range(n_trials):
            # Reset to initial state
            test_state = QuantumState([alpha, beta])
            outcome, _ = test_state.measure_in_basis(basis)
            outcomes.append(outcome)

        observed_prob_0 = outcomes.count(0) / n_trials
        observed_prob_1 = outcomes.count(1) / n_trials

        print(f"Observed P(0) = {observed_prob_0:.4f}")
        print(f"Observed P(1) = {observed_prob_1:.4f}")
        print(f"Error: {abs(observed_prob_0 - expected_prob_0):.4f}")

        result = {
            'expected': [expected_prob_0, expected_prob_1],
            'observed': [observed_prob_0, observed_prob_1],
            'error': abs(observed_prob_0 - expected_prob_0),
            'note': 'Born rule verified empirically but not explained'
        }

        self.results['born_rule_tests'].append(result)
        return result

    def test_basis_dependence(self) -> Dict:
        """
        Show that measurement outcome depends on chosen basis.

        This is the 'preferred basis problem': Why does nature
        pick one basis over another?
        """
        print("\n=== BASIS DEPENDENCE ===")

        # Superposition state
        system = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])
        print(f"State: |ψ⟩ = (|0⟩ + |1⟩)/√2")

        # Measure in computational basis
        basis_z = [np.array([1, 0]), np.array([0, 1])]
        outcomes_z = []
        for _ in range(1000):
            test_state = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])
            outcome, _ = test_state.measure_in_basis(basis_z)
            outcomes_z.append(outcome)

        print(f"\nZ-basis measurement:")
        print(f"  P(|0⟩) ≈ {outcomes_z.count(0)/1000:.3f}")
        print(f"  P(|1⟩) ≈ {outcomes_z.count(1)/1000:.3f}")

        # Measure in X basis (Hadamard basis)
        basis_x = [
            np.array([1/np.sqrt(2), 1/np.sqrt(2)]),   # |+⟩
            np.array([1/np.sqrt(2), -1/np.sqrt(2)])   # |-⟩
        ]
        outcomes_x = []
        for _ in range(1000):
            test_state = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])
            outcome, _ = test_state.measure_in_basis(basis_x)
            outcomes_x.append(outcome)

        print(f"\nX-basis measurement:")
        print(f"  P(|+⟩) ≈ {outcomes_x.count(0)/1000:.3f}")
        print(f"  P(|-⟩) ≈ {outcomes_x.count(1)/1000:.3f}")

        print("\nSAME STATE, DIFFERENT BASES → DIFFERENT OUTCOMES")
        print("Question: What picks the measurement basis in practice?")
        print("Answer: DECOHERENCE (environment interaction)")

        result = {
            'z_basis_probs': [outcomes_z.count(0)/1000, outcomes_z.count(1)/1000],
            'x_basis_probs': [outcomes_x.count(0)/1000, outcomes_x.count(1)/1000],
            'insight': 'Basis is not arbitrary - environment selects it via decoherence'
        }

        self.results['basis_preference_tests'].append(result)
        return result

    def test_observer_branching(self) -> Dict:
        """
        Simulate observer becoming entangled with system.

        Many-worlds interpretation: Observer branches, doesn't collapse.
        """
        print("\n=== OBSERVER BRANCHING (Many-Worlds) ===")

        # System in superposition
        system = QuantumState([1/np.sqrt(2), 1/np.sqrt(2)])

        # Observer (also quantum system with states |saw0⟩, |saw1⟩)
        observer = QuantumState([1, 0])  # Initially |ready⟩

        print("Initial:")
        print(f"  System: |ψ⟩ = (|0⟩ + |1⟩)/√2")
        print(f"  Observer: |ready⟩")
        print(f"  Combined: (|0⟩ + |1⟩)/√2 ⊗ |ready⟩")

        # Create joint state (2 system × 2 observer = 4 dimensional)
        combined = np.kron(system.amplitudes, observer.amplitudes)
        print(f"\nCombined amplitudes: {combined}")

        # Measurement interaction: CNOT-like entanglement
        # |0⟩|ready⟩ → |0⟩|saw0⟩
        # |1⟩|ready⟩ → |1⟩|saw1⟩

        # Unitary for measurement
        U_measure = np.array([
            [1, 0, 0, 0],  # |00⟩ → |00⟩  (system=0, observer=ready → system=0, observer=saw0)
            [0, 1, 0, 0],  # |01⟩ → |01⟩
            [0, 0, 0, 1],  # |10⟩ → |11⟩  (system=1, observer=ready → system=1, observer=saw1)
            [0, 0, 1, 0]   # |11⟩ → |10⟩
        ], dtype=complex)

        after_measurement = U_measure @ combined

        print(f"\nAfter measurement interaction:")
        print(f"  Combined: {after_measurement}")
        print(f"  = (|0,saw0⟩ + |1,saw1⟩)/√2")
        print("\nINTERPRETATIONS:")
        print("  Copenhagen: Wavefunction collapsed (but when? how? why?)")
        print("  Many-Worlds: Both branches exist, observer doesn't 'know' which")
        print("  Decoherence: Environment entangles, making branches non-interfering")

        # Check: Density matrix shows no interference between branches
        rho = np.outer(after_measurement, np.conj(after_measurement))

        print(f"\nDensity matrix (4×4):")
        print(rho)
        print(f"\nNote: Off-diagonal blocks (interference between branches) are non-zero")
        print(f"Adding environment would make them ~0 (decoherence)")

        result = {
            'initial_state': 'product',
            'final_state': 'entangled',
            'branches': 2,
            'interpretation': 'Observer becomes entangled with system - both outcomes exist in superposition'
        }

        self.results['observer_branching_tests'].append(result)
        return result

    def run_all_tests(self):
        """Run all measurement simulations"""
        print("="*60)
        print("QUANTUM MEASUREMENT SIMULATOR")
        print("Investigating the measurement problem")
        print("="*60)

        self.test_decoherence_basis_selection()
        self.test_born_rule_statistics()
        self.test_basis_dependence()
        self.test_observer_branching()

        # Save results
        with open(f'measurement_simulation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w') as f:
            # Convert numpy types for JSON serialization
            def convert(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, complex):
                    return {'real': obj.real, 'imag': obj.imag}
                return obj

            import json
            json.dump(self.results, f, indent=2, default=convert)

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("\nWhat we learned:")
        print("1. DECOHERENCE selects preferred basis via environment coupling")
        print("2. BORN RULE verified statistically but not derived from first principles")
        print("3. BASIS CHOICE determines measurement outcomes - not arbitrary")
        print("4. OBSERVER BRANCHING shows how measurement creates entanglement")
        print("\nWhat remains mysterious:")
        print("• WHY does |ψ|² give probabilities? (Born rule origin)")
        print("• WHEN does collapse happen? (measurement problem)")
        print("• WHERE do branches 'go'? (Many-worlds ontology)")
        print("• WHO/What constitutes an observer? (Observer problem)")
        print("\nConclusion: Measurement is decoherence + basis selection,")
        print("but probability interpretation remains fundamentally mysterious.")


if __name__ == '__main__':
    sim = MeasurementSimulator()
    sim.run_all_tests()
