#!/usr/bin/env python3
"""
AUTOCATALYTIC NETWORKS: Searching for Collective Self-Maintenance

Goal: Create a chemistry where sets of molecules can maintain each other
through catalytic cycles. This is the theoretical basis for origin of life
(Kauffman's autocatalytic sets, Gánti's chemoton).

Different from previous experiments:
- Not just replication (A → A)
- But catalytic cycles (A + B ⟶[C] D, D + E ⟶[A] B, etc.)

Can circular catalytic organization emerge spontaneously?
"""

import random
from collections import defaultdict
from typing import Set, Dict, List, Tuple


class Reaction:
    """A reaction: reactants → products, potentially catalyzed."""

    def __init__(self, reactants: Set[str], products: Set[str], catalyst: str = None):
        self.reactants = frozenset(reactants)
        self.products = frozenset(products)
        self.catalyst = catalyst

    def __hash__(self):
        return hash((self.reactants, self.products, self.catalyst))

    def __repr__(self):
        cat = f"[{self.catalyst}]" if self.catalyst else ""
        return f"{set(self.reactants)} →{cat} {set(self.products)}"


class CatalyticNetwork:
    """A network where molecules can catalyze reactions producing each other."""

    def __init__(self, food: List[str]):
        self.food = set(food)
        self.molecules: Dict[str, int] = defaultdict(int)
        self.reactions: List[Reaction] = []
        self.reaction_counts: Dict[Reaction, int] = defaultdict(int)

        # Start with food
        for mol in food:
            self.molecules[mol] = 20

        self.time = 0
        self.history = []

    def discover_reaction(self):
        """
        Randomly discover a possible reaction between molecules.
        This simulates chemical exploration of reaction space.
        """
        available = [m for m in self.molecules if self.molecules[m] > 0]

        if len(available) < 2:
            return

        # Pick random reactants
        reactants = set(random.sample(available, min(2, len(available))))

        # Create a product (simple: merge and modify)
        product_string = ''.join(sorted(reactants))

        # Random transformation
        if random.random() < 0.3:
            # Substitution
            product = product_string + random.choice(['a', 'b', 'c'])
        else:
            # Combination
            product = product_string

        products = {product}

        # Pick random catalyst (or none)
        catalyst = random.choice([None] + available) if available else None

        # Create reaction
        reaction = Reaction(reactants, products, catalyst)

        # Add if not already known
        if reaction not in self.reactions:
            self.reactions.append(reaction)

    def run_reaction(self, reaction: Reaction) -> bool:
        """Try to run a reaction if reactants available."""
        # Check if reactants present
        for reactant in reaction.reactants:
            if self.molecules[reactant] < 1:
                return False

        # Check if catalyst present (if needed)
        if reaction.catalyst and self.molecules[reaction.catalyst] < 1:
            # Can still happen, just slower
            if random.random() > 0.1:  # 90% chance to fail without catalyst
                return False

        # Run reaction
        for reactant in reaction.reactants:
            self.molecules[reactant] -= 1

        for product in reaction.products:
            self.molecules[product] += 1

        self.reaction_counts[reaction] += 1
        return True

    def step(self):
        """One time step."""
        self.time += 1

        # Add food
        for mol in self.food:
            self.molecules[mol] += 2

        # Discover new reactions occasionally
        if random.random() < 0.3:
            self.discover_reaction()

        # Run existing reactions
        for _ in range(20):
            if not self.reactions:
                break

            reaction = random.choice(self.reactions)
            self.run_reaction(reaction)

        # Decay
        for mol in list(self.molecules.keys()):
            if mol not in self.food and random.random() < 0.05:
                self.molecules[mol] = max(0, self.molecules[mol] - 1)

        # Record state
        self.record_state()

    def record_state(self):
        """Record state."""
        total = sum(self.molecules.values())
        non_food = sum(count for mol, count in self.molecules.items() if mol not in self.food)
        diversity = len([m for m in self.molecules if self.molecules[m] > 0])

        self.history.append({
            'time': self.time,
            'total': total,
            'non_food': non_food,
            'diversity': diversity
        })

    def detect_autocatalytic_set(self) -> List[Set[str]]:
        """
        Find sets of molecules that collectively catalyze their own production.

        An autocatalytic set has the property:
        - Every molecule in the set can be produced by reactions catalyzed by set members
        - Starting from food alone
        """
        # Find molecules that persist (not food)
        persistent = {mol for mol, count in self.molecules.items()
                     if count > 3 and mol not in self.food}

        if len(persistent) < 2:
            return []

        autocatalytic_sets = []

        # Check if groups of molecules form autocatalytic sets
        for size in range(2, min(6, len(persistent) + 1)):
            for subset in self._powerset_sample(persistent, size):
                if self._is_autocatalytic(set(subset)):
                    autocatalytic_sets.append(set(subset))

        return autocatalytic_sets

    def _powerset_sample(self, items: Set, size: int, max_samples: int = 50):
        """Sample from powerset of given size."""
        items_list = list(items)
        samples = []

        for _ in range(min(max_samples, 100)):
            if len(items_list) >= size:
                sample = random.sample(items_list, size)
                if sample not in samples:
                    samples.append(sample)
                    yield sample

    def _is_autocatalytic(self, mol_set: Set[str]) -> bool:
        """
        Check if a set is autocatalytic:
        Each member can be produced from food using reactions catalyzed by set members.
        """
        # For each molecule in set
        for mol in mol_set:
            # Can it be produced?
            can_be_produced = False

            for reaction in self.reactions:
                # Is this molecule a product?
                if mol in reaction.products:
                    # Are reactants either food or in set?
                    reactants_ok = all(r in self.food or r in mol_set for r in reaction.reactants)

                    # Is catalyst in set (or no catalyst needed)?
                    catalyst_ok = (reaction.catalyst is None or
                                 reaction.catalyst in mol_set or
                                 reaction.catalyst in self.food)

                    # Has this reaction happened?
                    reaction_active = self.reaction_counts[reaction] > 0

                    if reactants_ok and catalyst_ok and reaction_active:
                        can_be_produced = True
                        break

            if not can_be_produced:
                return False

        return True

    def detect_cycles(self) -> List[List[str]]:
        """Find catalytic cycles in the reaction network."""
        cycles = []

        # Build graph: molecule → molecules it helps produce
        graph = defaultdict(set)

        for reaction in self.reactions:
            if reaction.catalyst and self.reaction_counts[reaction] > 0:
                for product in reaction.products:
                    graph[reaction.catalyst].add(product)

        # Find cycles (simplified: length 2-4)
        for start in list(graph.keys()):  # Convert to list to avoid runtime error
            for mid in graph[start]:
                if start in graph.get(mid, set()):
                    cycles.append([start, mid])

        return cycles

    def report(self):
        """Report state."""
        print(f"\n=== TIME {self.time} ===")
        total = sum(self.molecules.values())
        non_food = sum(count for mol, count in self.molecules.items() if mol not in self.food)

        print(f"Molecules: {total} total, {non_food} non-food")
        print(f"Diversity: {len([m for m in self.molecules if self.molecules[m] > 0])} types")
        print(f"Reactions: {len(self.reactions)} discovered, {sum(self.reaction_counts.values())} total runs")

        # Most abundant non-food
        print("\nMost abundant (non-food):")
        non_food_mols = [(m, c) for m, c in self.molecules.items() if m not in self.food and c > 0]
        non_food_mols.sort(key=lambda x: x[1], reverse=True)

        for mol, count in non_food_mols[:10]:
            print(f"  {mol:15s} x{count:3d}")

        # Active reactions
        active_reactions = [(r, c) for r, c in self.reaction_counts.items() if c > 0]
        active_reactions.sort(key=lambda x: x[1], reverse=True)

        print(f"\nMost active reactions:")
        for reaction, count in active_reactions[:5]:
            print(f"  {reaction} : {count}x")

        # Check for autocatalytic sets
        auto_sets = self.detect_autocatalytic_set()
        if auto_sets:
            print(f"\n🌟 AUTOCATALYTIC SETS: {len(auto_sets)} found!")
            for i, mol_set in enumerate(auto_sets[:3]):
                print(f"  Set {i+1}: {mol_set}")

        # Check for cycles
        cycles = self.detect_cycles()
        if cycles:
            print(f"\n🔄 CATALYTIC CYCLES: {len(cycles)} found!")
            for cycle in cycles[:5]:
                print(f"  {' ⟷ '.join(cycle)}")


def experiment():
    """Run autocatalytic network experiment."""
    print("=" * 70)
    print("AUTOCATALYTIC NETWORKS: Searching for Collective Self-Maintenance")
    print("=" * 70)
    print("\nFood: A, B, C")
    print("Rules: Random reactions, catalysis, discovery")
    print("Question: Will autocatalytic sets emerge?")
    print()

    network = CatalyticNetwork(food=['A', 'B', 'C'])

    for i in range(150):
        network.step()
        if i % 50 == 0:
            network.report()

    print("\n" + "=" * 70)
    print("FINAL ANALYSIS")
    print("=" * 70)

    auto_sets = network.detect_autocatalytic_set()
    cycles = network.detect_cycles()

    print(f"\nTotal reactions discovered: {len(network.reactions)}")
    print(f"Total reaction events: {sum(network.reaction_counts.values())}")
    print(f"Autocatalytic sets found: {len(auto_sets)}")
    print(f"Catalytic cycles found: {len(cycles)}")

    if auto_sets:
        print("\n🎉 AUTOCATALYTIC CLOSURE ACHIEVED!")
        print("\nSets that maintain themselves:")
        for i, mol_set in enumerate(auto_sets[:5]):
            print(f"\nSet {i+1}: {mol_set}")

            # Show supporting reactions
            print("  Supporting reactions:")
            for reaction in network.reactions:
                if network.reaction_counts[reaction] > 0:
                    products_in_set = any(p in mol_set for p in reaction.products)
                    catalyst_in_set = reaction.catalyst in mol_set if reaction.catalyst else False

                    if products_in_set and catalyst_in_set:
                        print(f"    {reaction}")

    if cycles:
        print(f"\n🔄 CIRCULAR CATALYSIS EMERGED!")
        print("\nCatalytic cycles:")
        for cycle in cycles[:10]:
            print(f"  {' → '.join(cycle + [cycle[0]])}")

    return network


if __name__ == '__main__':
    network = experiment()
