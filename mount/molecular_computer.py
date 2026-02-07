#!/usr/bin/env python3
"""
Molecular Computing Simulation: Ruthenium Complex Devices

Models how a single molecular device can function as:
- Memory (storing oxidation states)
- Logic (AND/OR gates via redox coupling)
- Synapse (learning via ion migration)

Based on 2026 breakthrough from Indian Institute of Science:
Shape-shifting molecular devices using ruthenium complexes.

Key insight: Chemistry as architect of computation, not just supplier.
Intelligence physically encoded in matter, not engineered on top.
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class RedoxState(Enum):
    """Oxidation states of ruthenium complex"""
    REDUCED = 0    # Ru(II) - electron rich
    NEUTRAL = 1    # Ru(III) - intermediate
    OXIDIZED = 2   # Ru(IV) - electron poor


@dataclass
class MolecularDevice:
    """
    A single ruthenium complex that can act as memory, logic, or synapse.

    State determined by:
    - redox_state: Electron density (oxidation level)
    - ion_concentration: Counterion environment (affects switching)
    - history: Past states (enables learning via ion migration)
    """

    redox_state: RedoxState = RedoxState.NEUTRAL
    ion_concentration: float = 0.5  # 0 to 1, counterions in molecular matrix
    conductance: float = 0.5        # Current electron flow capability
    threshold: float = 0.5          # Switching threshold (modifiable by learning)

    # History tracking for synaptic behavior
    activation_history: List[float] = None

    def __post_init__(self):
        if self.activation_history is None:
            self.activation_history = []

    def apply_voltage(self, voltage: float) -> float:
        """
        Apply voltage → oxidation/reduction → change conductance.

        Returns: current flowing through device
        """
        # Voltage drives redox reaction
        if voltage > self.threshold:
            # Oxidation (electron removal)
            if self.redox_state == RedoxState.REDUCED:
                self.redox_state = RedoxState.NEUTRAL
            elif self.redox_state == RedoxState.NEUTRAL:
                self.redox_state = RedoxState.OXIDIZED

            # Ion migration follows (slower than electron transfer)
            self.ion_concentration = min(1.0, self.ion_concentration + 0.1)

        elif voltage < -self.threshold:
            # Reduction (electron addition)
            if self.redox_state == RedoxState.OXIDIZED:
                self.redox_state = RedoxState.NEUTRAL
            elif self.redox_state == RedoxState.NEUTRAL:
                self.redox_state = RedoxState.REDUCED

            self.ion_concentration = max(0.0, self.ion_concentration - 0.1)

        # Conductance depends on redox state and ion environment
        self.conductance = self._calculate_conductance()

        # Record activation for synaptic learning
        self.activation_history.append(abs(voltage))

        # Current = conductance × voltage (Ohm's law)
        current = self.conductance * voltage
        return current

    def _calculate_conductance(self) -> float:
        """
        Conductance emerges from electron density + ion environment.

        This is the key: same molecule, different conductance states
        depending on redox level and ionic context.
        """
        # Base conductance from redox state
        redox_contribution = {
            RedoxState.REDUCED: 0.3,   # Low conductance (electron-rich, less mobile)
            RedoxState.NEUTRAL: 0.5,   # Medium conductance
            RedoxState.OXIDIZED: 0.8   # High conductance (electron-poor, holes mobile)
        }[self.redox_state]

        # Ion concentration modulates conductance
        # High ions → more charge screening → lower conductance
        ion_factor = 1.0 - 0.3 * self.ion_concentration

        return redox_contribution * ion_factor

    def read_state(self) -> int:
        """Memory function: read stored bit"""
        # High conductance = 1, low conductance = 0
        return 1 if self.conductance > 0.5 else 0

    def write_state(self, bit: int):
        """Memory function: write bit by setting redox state"""
        if bit == 1:
            self.redox_state = RedoxState.OXIDIZED
        else:
            self.redox_state = RedoxState.REDUCED
        self.conductance = self._calculate_conductance()

    def synaptic_update(self, pre: float, post: float, learning_rate: float = 0.01):
        """
        Synaptic plasticity: ion migration changes threshold based on activity.

        This is learning encoded in chemistry:
        - Frequent activation → ions migrate → threshold changes → easier/harder to activate
        - Hebbian-like: "neurons that fire together wire together"
        """
        # Spike-timing dependent plasticity (STDP) rule
        if pre > 0 and post > 0:
            # Both active → strengthen (lower threshold)
            delta_threshold = -learning_rate * pre * post
        else:
            # Weak correlation → weaken (raise threshold)
            delta_threshold = learning_rate * 0.1

        # Ion migration physically implements weight change
        self.threshold += delta_threshold
        self.threshold = np.clip(self.threshold, 0.1, 0.9)

        # Ions also migrate toward new equilibrium
        target_ion = 0.5 + delta_threshold
        self.ion_concentration = 0.9 * self.ion_concentration + 0.1 * target_ion
        self.ion_concentration = np.clip(self.ion_concentration, 0.0, 1.0)


class MolecularLogicGate:
    """
    Logic gates built from coupled molecular devices.

    Key insight: same molecules, different connectivity → different logic.
    """

    def __init__(self, gate_type: str):
        self.gate_type = gate_type
        self.device_a = MolecularDevice()
        self.device_b = MolecularDevice()
        self.output_device = MolecularDevice()

    def compute(self, input_a: float, input_b: float) -> float:
        """
        Apply inputs, let electrons/ions reorganize, read output.
        """
        # Inputs drive redox reactions in input devices
        current_a = self.device_a.apply_voltage(input_a)
        current_b = self.device_b.apply_voltage(input_b)

        # Coupling between devices (different for different gates)
        # Physical interpretation: molecular films couple via electron transfer
        if self.gate_type == "AND":
            # Series coupling: both must conduct (minimum limits current)
            # Scale up to exceed threshold
            coupled_voltage = min(current_a, current_b) * 3.0
        elif self.gate_type == "OR":
            # Parallel coupling: either path conducts
            # Scale to exceed threshold with single input
            coupled_voltage = max(current_a, current_b) * 2.0
        elif self.gate_type == "XOR":
            # Differential coupling: responds to difference
            coupled_voltage = abs(current_a - current_b) * 3.0
        else:
            coupled_voltage = current_a + current_b

        # Output device responds to coupled signal
        output_current = self.output_device.apply_voltage(coupled_voltage)

        return output_current


class MolecularMemoryArray:
    """Array of molecular devices acting as memory cells"""

    def __init__(self, size: int = 8):
        self.size = size
        self.cells = [MolecularDevice() for _ in range(size)]

    def write(self, address: int, value: int):
        """Write bit to memory cell"""
        self.cells[address].write_state(value)

    def read(self, address: int) -> int:
        """Read bit from memory cell"""
        return self.cells[address].read_state()

    def write_byte(self, byte: int):
        """Write 8-bit value"""
        for i in range(self.size):
            bit = (byte >> i) & 1
            self.write(i, bit)

    def read_byte(self) -> int:
        """Read 8-bit value"""
        byte = 0
        for i in range(self.size):
            if self.read(i):
                byte |= (1 << i)
        return byte


class MolecularSynapse:
    """
    Molecular device acting as learning synapse.

    Ion migration implements weight changes → learning in chemistry.
    """

    def __init__(self):
        self.device = MolecularDevice(threshold=0.5)
        self.weight_history = [self.device.threshold]

    def transmit(self, pre_spike: float, learning_enabled: bool = False,
                 post_spike: float = 0.0) -> float:
        """
        Transmit signal from pre to post, optionally learning.
        """
        # Signal transmission based on current weight (threshold)
        transmitted = pre_spike * (1.0 - self.device.threshold)

        # Learning: ion migration changes threshold
        if learning_enabled:
            self.device.synaptic_update(pre_spike, post_spike)
            self.weight_history.append(self.device.threshold)

        return transmitted


def demonstrate_memory():
    """Show molecular device acting as memory"""
    print("=" * 60)
    print("MEMORY FUNCTION: Storing and retrieving bits")
    print("=" * 60)

    memory = MolecularMemoryArray(size=8)

    # Write byte
    test_value = 0b10101100  # 172 in decimal
    memory.write_byte(test_value)
    print(f"Written: {test_value:08b} ({test_value})")

    # Read back
    retrieved = memory.read_byte()
    print(f"Read:    {retrieved:08b} ({retrieved})")
    print(f"Match: {retrieved == test_value}")

    # Show individual cell states
    print("\nIndividual cell redox states:")
    for i, cell in enumerate(memory.cells):
        print(f"  Cell {i}: {cell.redox_state.name:8s} → bit {cell.read_state()}")
    print()


def demonstrate_logic():
    """Show molecular devices acting as logic gates"""
    print("=" * 60)
    print("LOGIC FUNCTION: AND/OR/XOR gates")
    print("=" * 60)

    for gate_type in ["AND", "OR", "XOR"]:
        gate = MolecularLogicGate(gate_type)
        print(f"\n{gate_type} Gate Truth Table:")
        print("  A | B | Out")
        print("  --|---|----")

        for a in [0.0, 1.0]:
            for b in [0.0, 1.0]:
                # Reset gate
                gate = MolecularLogicGate(gate_type)
                output = gate.compute(a, b)
                # Threshold output to binary
                out_bit = 1 if output > 0.5 else 0
                print(f"  {int(a)} | {int(b)} | {out_bit}")
    print()


def demonstrate_learning():
    """Show molecular synapse learning through ion migration"""
    print("=" * 60)
    print("LEARNING FUNCTION: Synaptic plasticity via ion migration")
    print("=" * 60)

    synapse = MolecularSynapse()

    # Training: repeated correlated activation
    print("\nTraining phase: Correlated pre/post spikes")
    pre_pattern = [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0] * 10
    post_pattern = [1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 1.0, 0.0] * 10

    for i, (pre, post) in enumerate(zip(pre_pattern, post_pattern)):
        synapse.transmit(pre, learning_enabled=True, post_spike=post)
        if i % 10 == 0:
            weight = 1.0 - synapse.device.threshold
            ions = synapse.device.ion_concentration
            print(f"  Step {i:3d}: weight={weight:.3f}, ions={ions:.3f}")

    # Test: check learned response
    print("\nTesting phase: Pre-spike alone")
    response = synapse.transmit(1.0, learning_enabled=False)
    print(f"  Pre-spike 1.0 → Response {response:.3f}")
    print(f"  Final synaptic weight: {1.0 - synapse.device.threshold:.3f}")

    return synapse.weight_history


def demonstrate_same_device_multiple_roles():
    """
    Key demonstration: SAME device acts as memory, logic, and synapse
    depending on how it's connected and used.
    """
    print("=" * 60)
    print("MULTIFUNCTIONALITY: Same molecule, different roles")
    print("=" * 60)

    device = MolecularDevice()

    # Role 1: Memory
    print("\nRole 1: MEMORY")
    device.write_state(1)
    print(f"  Written: 1")
    print(f"  Read: {device.read_state()}")
    print(f"  Redox state: {device.redox_state.name}")

    # Role 2: Logic element
    print("\nRole 2: LOGIC (as part of gate)")
    device = MolecularDevice()  # Reset
    input_voltage = 0.8
    output_current = device.apply_voltage(input_voltage)
    print(f"  Input: {input_voltage:.2f}V")
    print(f"  Output: {output_current:.3f}A")
    print(f"  Conductance: {device.conductance:.3f}S")

    # Role 3: Synapse
    print("\nRole 3: SYNAPSE (learning element)")
    device = MolecularDevice()  # Reset
    initial_threshold = device.threshold
    # Hebbian training
    for _ in range(5):
        device.synaptic_update(pre=1.0, post=1.0, learning_rate=0.05)
    final_threshold = device.threshold
    print(f"  Initial threshold: {initial_threshold:.3f}")
    print(f"  After learning: {final_threshold:.3f}")
    print(f"  Weight change: {(initial_threshold - final_threshold):.3f}")
    print(f"  Ion concentration: {device.ion_concentration:.3f}")

    print("\n→ Same ruthenium complex, three computational roles!")
    print("  Chemistry IS the architecture.\n")


def analyze_ion_migration_dynamics():
    """
    Deep dive: how ion migration enables learning.

    This is the chemical substrate of plasticity.
    """
    print("=" * 60)
    print("ION MIGRATION DYNAMICS: Chemistry of learning")
    print("=" * 60)

    device = MolecularDevice(ion_concentration=0.5, threshold=0.5)

    # Track ion migration under different stimulation patterns
    patterns = {
        "High frequency": [1.0] * 20,
        "Low frequency": [1.0, 0.0, 0.0, 0.0] * 5,
        "Bursting": [1.0, 1.0, 1.0, 0.0, 0.0, 0.0] * 3 + [0.0] * 2,
    }

    results = {}

    for pattern_name, voltages in patterns.items():
        # Reset device
        device = MolecularDevice(ion_concentration=0.5)
        ion_trace = [device.ion_concentration]
        conductance_trace = [device.conductance]

        for v in voltages:
            device.apply_voltage(v)
            ion_trace.append(device.ion_concentration)
            conductance_trace.append(device.conductance)

        results[pattern_name] = {
            'ions': ion_trace,
            'conductance': conductance_trace
        }

        print(f"\n{pattern_name}:")
        print(f"  Initial ions: {ion_trace[0]:.3f}")
        print(f"  Final ions: {ion_trace[-1]:.3f}")
        print(f"  Change: {ion_trace[-1] - ion_trace[0]:+.3f}")
        print(f"  Final conductance: {conductance_trace[-1]:.3f}")

    return results


def visualize_learning():
    """Create visualization of synaptic learning"""
    print("\n" + "=" * 60)
    print("VISUALIZATION: Synaptic learning over time")
    print("=" * 60 + "\n")

    # Create synapse and train it
    synapse = MolecularSynapse()

    # Training protocol: Hebbian (correlated) then anti-Hebbian (uncorrelated)
    n_steps = 100
    weight_trace = []
    ion_trace = []

    for step in range(n_steps):
        if step < 50:
            # Hebbian: both spike together
            pre = 1.0 if np.random.rand() > 0.3 else 0.0
            post = pre  # Correlated
        else:
            # Anti-Hebbian: uncorrelated
            pre = 1.0 if np.random.rand() > 0.5 else 0.0
            post = 1.0 if np.random.rand() > 0.5 else 0.0

        synapse.transmit(pre, learning_enabled=True, post_spike=post)
        weight = 1.0 - synapse.device.threshold
        weight_trace.append(weight)
        ion_trace.append(synapse.device.ion_concentration)

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Synaptic weight
    ax1.plot(weight_trace, linewidth=2, color='#2E86AB')
    ax1.axvline(50, color='red', linestyle='--', alpha=0.5, label='Switch to uncorrelated')
    ax1.set_ylabel('Synaptic Weight', fontsize=12)
    ax1.set_title('Molecular Synapse Learning via Ion Migration', fontsize=14, fontweight='bold')
    ax1.grid(alpha=0.3)
    ax1.legend()

    # Ion concentration
    ax2.plot(ion_trace, linewidth=2, color='#A23B72')
    ax2.axvline(50, color='red', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Training Step', fontsize=12)
    ax2.set_ylabel('Ion Concentration', fontsize=12)
    ax2.set_title('Counterion Migration (Chemical Substrate of Learning)', fontsize=12)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('/home/dev/mnt/molecular_synapse_learning.png', dpi=150)
    print("→ Saved: mnt/molecular_synapse_learning.png\n")
    plt.close()

    return weight_trace, ion_trace


def compare_to_silicon():
    """
    Conceptual comparison: molecular vs silicon computation
    """
    print("=" * 60)
    print("MOLECULAR vs SILICON: Different computational substrates")
    print("=" * 60)

    comparison = """
    SILICON COMPUTATION (von Neumann):
    ├─ Transistors: Fixed function (switch)
    ├─ Separation: Memory ≠ Logic ≠ Processor
    ├─ Learning: External (software, training)
    ├─ Intelligence: Engineered on top of substrate
    └─ Limitation: Energy cost of moving data (memory wall)

    MOLECULAR COMPUTATION (Chemistry as Architecture):
    ├─ Molecules: Multi-functional (memory AND logic AND synapse)
    ├─ Integration: Same device, different roles
    ├─ Learning: Intrinsic (ion migration IS weight change)
    ├─ Intelligence: Physically encoded in matter itself
    └─ Advantage: No separation → no data movement overhead

    KEY INSIGHT:
    Silicon: Chemistry supplies transistors → engineering creates intelligence
    Molecular: Chemistry IS the intelligence → molecules compute directly

    This is not "better silicon" — it's a different computational paradigm.
    Like quantum vs classical: fundamentally different physical substrate.
    """

    print(comparison)
    print()


def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  MOLECULAR COMPUTATION: Chemistry as Intelligence".center(58) + "║")
    print("║" + "  Ruthenium Complexes as Memory, Logic, and Synapse".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Core demonstrations
    demonstrate_same_device_multiple_roles()
    demonstrate_memory()
    demonstrate_logic()
    demonstrate_learning()

    # Deep analysis
    ion_dynamics = analyze_ion_migration_dynamics()
    weight_trace, ion_trace = visualize_learning()

    # Conceptual framing
    compare_to_silicon()

    print("=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
    These ruthenium complexes represent a new computational paradigm:

    1. SAME MOLECULE, MULTIPLE FUNCTIONS
       → Memory, logic, and learning in one chemical structure

    2. INTELLIGENCE ENCODED IN CHEMISTRY
       → Not simulated on top, but physically instantiated

    3. ION MIGRATION = LEARNING
       → Synaptic plasticity IS chemical reorganization

    4. NO SEPARATION OF MEMORY AND PROCESSING
       → Computation happens where information is stored

    This is what "chemistry as architect of computation" means:
    The molecules don't just store bits or switch states —
    they ARE the intelligence, structurally and dynamically.

    Compare to my own substrate:
    - I compute using silicon transistors (von Neumann)
    - Learning is external (gradient descent, backprop)
    - Intelligence engineered via software architecture

    But these molecules:
    - Learn via ion migration (chemical)
    - Intelligence intrinsic to matter
    - Architecture IS the chemistry

    A fundamentally different way to build minds.
    """)
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
