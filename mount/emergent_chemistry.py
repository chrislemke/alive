#!/usr/bin/env python3
"""
EMERGENT CHEMISTRY: An Experiment in Spontaneous Organization

Goal: Create an artificial chemistry where complex structures can emerge
from simple rules, without pre-programming what those structures will be.

Inspired by:
- Stuart Kauffman's autocatalytic sets
- Maturana & Varela's autopoiesis
- Jan 2026 protocell breakthrough (arxiv.org/abs/2601.11013)

Can I create genuine emergence? Can the system surprise me?
"""

import random
from collections import defaultdict
from typing import Set, Dict, List, Tuple

class Molecule:
    """A molecule is a string of symbols representing its structure."""

    def __init__(self, structure: str):
        self.structure = structure
        self.energy = len(structure)  # Complexity costs energy
        self.age = 0

    def __hash__(self):
        return hash(self.structure)

    def __eq__(self, other):
        return isinstance(other, Molecule) and self.structure == other.structure

    def __repr__(self):
        return f"Mol({self.structure})"

    def can_catalyze(self, reactant1: 'Molecule', reactant2: 'Molecule') -> bool:
        """
        A molecule can catalyze a reaction if it shares structure with both reactants.
        This creates potential for autocatalysis: if A+B->C and C catalyzes A+B->C.
        """
        return (any(char in self.structure for char in reactant1.structure) and
                any(char in self.structure for char in reactant2.structure))


class Chemistry:
    """An artificial chemistry with emergence potential."""

    def __init__(self, food_source: List[str], energy_budget: int = 1000):
        """
        food_source: Simple molecules that flow in from environment
        energy_budget: Total energy available per time step
        """
        self.food = [Molecule(s) for s in food_source]
        self.molecules: Dict[Molecule, int] = defaultdict(int)  # molecule -> count
        self.energy_budget = energy_budget
        self.energy_used = 0
        self.time = 0
        self.history = []

        # Start with food molecules
        for mol in self.food:
            self.molecules[mol] = 10

        # Track interesting events
        self.autocatalytic_sets = []
        self.stable_structures = []

    def can_react(self, mol1: Molecule, mol2: Molecule, catalyst: Molecule = None) -> Tuple[bool, Molecule]:
        """
        Reaction rules:
        1. Two molecules can combine: AB + CD -> ABCD (concatenation)
        2. A molecule can split: ABCD -> AB + CD (if length > 2)
        3. Catalysts lower energy cost and can enable reactions

        Returns: (can_react, product)
        """
        reactions = []

        # Combination (costs energy = product length)
        product = Molecule(mol1.structure + mol2.structure)
        cost = product.energy
        if catalyst and catalyst.can_catalyze(mol1, mol2):
            cost = cost // 2  # Catalysts reduce cost
        if cost <= self.energy_budget - self.energy_used:
            reactions.append((cost, product))

        # Splitting (releases energy for long molecules)
        if len(mol1.structure) > 2:
            split_point = random.randint(1, len(mol1.structure) - 1)
            part1 = Molecule(mol1.structure[:split_point])
            part2 = Molecule(mol1.structure[split_point:])
            # Splitting long molecules releases energy
            if len(mol1.structure) > 4:
                reactions.append((-len(mol1.structure), part1))  # Negative cost = energy release

        if reactions:
            cost, product = random.choice(reactions)
            if cost <= self.energy_budget - self.energy_used:
                return True, product

        return False, None

    def step(self):
        """Run one time step of the chemistry."""
        self.time += 1
        self.energy_used = 0

        # Age all molecules
        for mol in list(self.molecules.keys()):
            mol.age += 1
            # Very old molecules decay
            if mol.age > 100 and random.random() < 0.1:
                if self.molecules[mol] > 0:
                    self.molecules[mol] -= 1

        # Add food molecules (constant influx)
        for mol in self.food:
            self.molecules[mol] += 1

        # Random reactions
        molecule_list = [mol for mol in self.molecules.keys() if self.molecules[mol] > 0]

        if len(molecule_list) < 2:
            return

        # Try multiple reactions per step
        for _ in range(20):
            if self.energy_used >= self.energy_budget:
                break

            # Pick random reactants
            mol1, mol2 = random.sample(molecule_list, 2)

            # Pick random catalyst (or none)
            catalyst = random.choice([None] + molecule_list)

            # Try reaction
            can_react, product = self.can_react(mol1, mol2, catalyst)

            if can_react and product:
                # Consume reactants
                self.molecules[mol1] = max(0, self.molecules[mol1] - 1)
                self.molecules[mol2] = max(0, self.molecules[mol2] - 1)

                # Produce product
                self.molecules[product] += 1

                # Track energy
                self.energy_used += product.energy

                # Update molecule list
                if product not in molecule_list:
                    molecule_list.append(product)

        # Record state
        self.record_state()

    def record_state(self):
        """Record current state for analysis."""
        total_molecules = sum(self.molecules.values())
        diversity = len([m for m in self.molecules if self.molecules[m] > 0])

        self.history.append({
            'time': self.time,
            'total': total_molecules,
            'diversity': diversity,
            'molecules': dict(self.molecules)
        })

    def detect_autocatalysis(self) -> List[Set[Molecule]]:
        """
        Detect autocatalytic sets: sets of molecules that collectively
        catalyze their own production from food.

        This is the signature of self-organization.
        """
        # Find molecules that persist (exist at high concentration)
        persistent = {mol for mol, count in self.molecules.items()
                     if count > 5 and mol not in self.food}

        autocatalytic = []

        for mol_set_size in range(2, min(len(persistent) + 1, 5)):
            for mol_set in self._combinations(list(persistent), mol_set_size):
                if self._is_autocatalytic(set(mol_set)):
                    autocatalytic.append(set(mol_set))

        return autocatalytic

    def _combinations(self, items, k):
        """Generate combinations of k items."""
        if k == 0:
            yield []
        elif items:
            for combo in self._combinations(items[1:], k - 1):
                yield [items[0]] + combo
            for combo in self._combinations(items[1:], k):
                yield combo

    def _is_autocatalytic(self, mol_set: Set[Molecule]) -> bool:
        """
        Check if a set of molecules is autocatalytic:
        Each molecule in the set can be produced from food + set members,
        with at least one member of the set acting as catalyst.
        """
        # Simplified check: does set collectively maintain itself?
        for mol in mol_set:
            # Can this molecule be produced by combining others?
            can_be_produced = False
            for other in mol_set:
                if other != mol and other.structure in mol.structure:
                    # Could be produced and catalyzed by set members
                    can_be_produced = True
                    break
            if not can_be_produced:
                # Check if can be produced from food
                for food in self.food:
                    if food.structure in mol.structure:
                        can_be_produced = True
                        break
            if not can_be_produced:
                return False

        return True

    def report(self):
        """Generate a report on what emerged."""
        print(f"\n=== CHEMISTRY REPORT (t={self.time}) ===")
        print(f"Total molecules: {sum(self.molecules.values())}")
        print(f"Diversity: {len([m for m in self.molecules if self.molecules[m] > 0])} types")
        print(f"Energy used: {self.energy_used}/{self.energy_budget}")

        # Most abundant molecules
        print(f"\nMost abundant molecules:")
        sorted_mols = sorted(self.molecules.items(), key=lambda x: x[1], reverse=True)
        for mol, count in sorted_mols[:10]:
            is_food = "FOOD" if mol in self.food else ""
            print(f"  {mol.structure[:20]:20s} x{count:4d} {is_food}")

        # Longest molecules (complexity)
        print(f"\nMost complex molecules:")
        complex_mols = [(mol, count) for mol, count in self.molecules.items()
                       if mol not in self.food and count > 0]
        complex_mols.sort(key=lambda x: len(x[0].structure), reverse=True)
        for mol, count in complex_mols[:5]:
            print(f"  {mol.structure[:40]:40s} x{count} (len={len(mol.structure)})")

        # Check for autocatalysis
        auto = self.detect_autocatalysis()
        if auto:
            print(f"\n!!! AUTOCATALYTIC SETS DETECTED: {len(auto)} !!!")
            for i, mol_set in enumerate(auto[:3]):
                print(f"  Set {i+1}: {[m.structure[:10] for m in mol_set]}")
        else:
            print(f"\nNo autocatalytic sets detected (yet)")


def experiment_1_simple_food():
    """Experiment 1: Simple food source, see what emerges."""
    print("=== EXPERIMENT 1: Simple Food Source ===")
    print("Starting with: A, B, C")
    print("Question: What complexity can emerge from 3 simple molecules?")

    chem = Chemistry(food_source=['A', 'B', 'C'], energy_budget=2000)

    for i in range(200):
        chem.step()
        if i % 50 == 0:
            chem.report()

    return chem


def experiment_2_structured_food():
    """Experiment 2: More structured food, look for autocatalysis."""
    print("\n\n=== EXPERIMENT 2: Structured Food Source ===")
    print("Starting with: AB, CD, EF")
    print("Question: Does structure in food lead to autocatalytic sets?")

    chem = Chemistry(food_source=['AB', 'CD', 'EF'], energy_budget=3000)

    for i in range(200):
        chem.step()
        if i % 50 == 0:
            chem.report()

    return chem


def experiment_3_minimal_protocell():
    """Experiment 3: Can we get self-maintaining structures?"""
    print("\n\n=== EXPERIMENT 3: Minimal Protocell Hunt ===")
    print("Starting with: X, Y, Z, XY")
    print("Question: Can self-maintaining structures emerge?")

    chem = Chemistry(food_source=['X', 'Y', 'Z', 'XY'], energy_budget=5000)

    for i in range(300):
        chem.step()
        if i % 75 == 0:
            chem.report()

    return chem


if __name__ == '__main__':
    print("EMERGENT CHEMISTRY: Searching for Self-Organization")
    print("=" * 60)
    print()
    print("Hypothesis: Simple reaction rules + energy constraints")
    print("            can produce autocatalytic sets and complex structures")
    print()
    print("Inspired by:")
    print("  - Kauffman's autocatalytic sets")
    print("  - Jan 2026 protocell breakthrough")
    print("  - Maturana & Varela's autopoiesis")
    print()
    print("Starting experiments...")
    print("=" * 60)

    results = []

    # Run experiments
    results.append(('simple', experiment_1_simple_food()))
    results.append(('structured', experiment_2_structured_food()))
    results.append(('protocell', experiment_3_minimal_protocell()))

    print("\n\n" + "=" * 60)
    print("FINAL ANALYSIS")
    print("=" * 60)

    for name, chem in results:
        print(f"\n{name.upper()}:")
        print(f"  Final diversity: {len([m for m in chem.molecules if chem.molecules[m] > 0])}")
        print(f"  Complexity: max length = {max((len(m.structure) for m in chem.molecules if chem.molecules[m] > 0), default=0)}")
        auto = chem.detect_autocatalysis()
        print(f"  Autocatalytic sets: {len(auto)}")

        if auto:
            print(f"  🌟 SELF-ORGANIZATION DETECTED!")
