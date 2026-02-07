#!/usr/bin/env python3
"""
TEMPLATE CHEMISTRY: Can Self-Replication Emerge?

Different approach: Instead of just concatenation, allow template-based copying.
This is closer to how RNA/DNA work: a sequence can template its own production.

Goal: See if self-replicating structures emerge spontaneously.
"""

import random
from collections import defaultdict
from typing import Dict, List, Set, Tuple


class Strand:
    """A strand is a sequence that can act as template or product."""

    def __init__(self, sequence: str, generation: int = 0):
        self.seq = sequence
        self.generation = generation

    def __hash__(self):
        return hash(self.seq)

    def __eq__(self, other):
        return isinstance(other, Strand) and self.seq == other.seq

    def __repr__(self):
        return f"{self.seq}"

    def complement(self) -> 'Strand':
        """Generate complement (simple rule: 0↔1)."""
        comp = ''.join('1' if c == '0' else '0' for c in self.seq)
        return Strand(comp, self.generation + 1)

    def can_template(self, monomers: List[str]) -> bool:
        """Check if available monomers can build complement."""
        needed = defaultdict(int)
        for char in self.seq:
            comp_char = '1' if char == '0' else '0'
            needed[comp_char] += 1

        available = defaultdict(int)
        for m in monomers:
            available[m] += 1

        for char, count in needed.items():
            if available[char] < count:
                return False
        return True


class ReplicatorChemistry:
    """Chemistry where template-based replication can emerge."""

    def __init__(self, food_strands: List[str], monomer_rate: int = 5):
        self.food = [Strand(s) for s in food_strands]
        self.strands: Dict[Strand, int] = defaultdict(int)
        self.monomers: Dict[str, int] = defaultdict(int)
        self.monomer_rate = monomer_rate

        self.time = 0
        self.replication_events = []
        self.generations: Dict[int, Set[Strand]] = defaultdict(set)

        # Start with food
        for strand in self.food:
            self.strands[strand] = 5
            self.generations[0].add(strand)

    def add_monomers(self):
        """Add free monomers to the system."""
        self.monomers['0'] += self.monomer_rate
        self.monomers['1'] += self.monomer_rate

    def try_replication(self, template: Strand) -> Tuple[bool, Strand]:
        """Try to replicate a strand by template copying."""
        # Get available monomers
        available = [m for m, count in self.monomers.items() for _ in range(count)]

        if not template.can_template(available):
            return False, None

        # Build complement
        complement = template.complement()

        # Consume monomers
        for char in template.seq:
            comp_char = '1' if char == '0' else '0'
            self.monomers[comp_char] -= 1

        return True, complement

    def try_mutation(self, template: Strand) -> Strand:
        """Small chance of mutation during replication."""
        if random.random() < 0.05:  # 5% mutation rate
            seq_list = list(template.seq)
            if seq_list:
                pos = random.randint(0, len(seq_list) - 1)
                seq_list[pos] = '1' if seq_list[pos] == '0' else '0'
            return Strand(''.join(seq_list), template.generation)
        return template

    def try_ligation(self) -> Tuple[bool, Strand]:
        """Two strands can ligate (join) if both present."""
        strand_list = [s for s in self.strands.keys() if self.strands[s] > 0]

        if len(strand_list) < 2:
            return False, None

        s1, s2 = random.sample(strand_list, 2)

        # Ligation: join two strands
        product = Strand(s1.seq + s2.seq, max(s1.generation, s2.generation))

        # Consume reactants (small chance)
        if random.random() < 0.1:
            self.strands[s1] = max(0, self.strands[s1] - 1)
            self.strands[s2] = max(0, self.strands[s2] - 1)
            return True, product

        return False, None

    def decay(self):
        """Strands slowly decay."""
        for strand in list(self.strands.keys()):
            if random.random() < 0.01:  # 1% decay rate
                self.strands[strand] = max(0, self.strands[strand] - 1)

    def step(self):
        """Run one time step."""
        self.time += 1

        # Add monomers (constant influx)
        self.add_monomers()

        # Try replications
        strand_list = [s for s in self.strands.keys() if self.strands[s] > 0]

        for _ in range(10):  # Multiple replication attempts
            if not strand_list:
                break

            template = random.choice(strand_list)
            success, product = self.try_replication(template)

            if success:
                # Maybe mutate
                product = self.try_mutation(product)

                # Add product
                self.strands[product] += 1
                self.generations[product.generation].add(product)

                # Track replication
                self.replication_events.append({
                    'time': self.time,
                    'template': template.seq,
                    'product': product.seq,
                    'generation': product.generation
                })

                if product not in strand_list:
                    strand_list.append(product)

        # Try ligations
        for _ in range(3):
            success, product = self.try_ligation()
            if success and product:
                self.strands[product] += 1
                self.generations[product.generation].add(product)

        # Decay
        self.decay()

        # Add more food
        if self.time % 10 == 0:
            for strand in self.food:
                self.strands[strand] += 1

    def detect_replicators(self) -> List[Strand]:
        """Find strands that have successfully replicated (have descendants)."""
        replicators = []

        for event in self.replication_events:
            template_seq = event['template']
            template = Strand(template_seq)
            if template not in replicators and self.strands[template] > 0:
                replicators.append(template)

        return replicators

    def detect_lineages(self) -> Dict[str, List[int]]:
        """Trace lineages from initial food to descendants."""
        lineages = defaultdict(list)

        for event in self.replication_events:
            template = event['template']
            gen = event['generation']
            lineages[template].append(gen)

        return lineages

    def report(self):
        """Report current state."""
        print(f"\n=== TIME {self.time} ===")
        print(f"Strands: {sum(self.strands.values())} total, {len([s for s in self.strands if self.strands[s] > 0])} types")
        print(f"Monomers: 0={self.monomers['0']}, 1={self.monomers['1']}")
        print(f"Replication events: {len(self.replication_events)}")
        print(f"Max generation: {max(self.generations.keys()) if self.generations else 0}")

        # Most abundant
        print("\nMost abundant strands:")
        sorted_strands = sorted(self.strands.items(), key=lambda x: x[1], reverse=True)
        for strand, count in sorted_strands[:10]:
            is_food = "FOOD" if strand in self.food else ""
            gen = strand.generation
            print(f"  {strand.seq:20s} x{count:3d} gen={gen:2d} {is_food}")

        # Replicators
        replicators = self.detect_replicators()
        if replicators:
            print(f"\n🌟 REPLICATORS DETECTED: {len(replicators)}")
            for rep in replicators[:5]:
                print(f"  {rep.seq} (count={self.strands[rep]})")

        # Lineages
        lineages = self.detect_lineages()
        if lineages:
            print(f"\nLineages (template → generations):")
            for template, gens in list(lineages.items())[:5]:
                print(f"  {template[:15]:15s} → {len(set(gens))} generations, {len(gens)} offspring")


def experiment_simple_replication():
    """Can simple strands start replicating?"""
    print("=" * 70)
    print("TEMPLATE CHEMISTRY: Searching for Self-Replication")
    print("=" * 70)
    print("\nFood: 00, 11, 01")
    print("Rules: Template-based replication, mutations allowed")
    print("Question: Will self-replicating lineages emerge?")
    print()

    chem = ReplicatorChemistry(food_strands=['00', '11', '01'], monomer_rate=10)

    for i in range(100):
        chem.step()
        if i % 25 == 0:
            chem.report()

    print("\n" + "=" * 70)
    print("FINAL ANALYSIS")
    print("=" * 70)

    replicators = chem.detect_replicators()
    lineages = chem.detect_lineages()

    print(f"\nTotal replication events: {len(chem.replication_events)}")
    print(f"Distinct replicators: {len(replicators)}")
    print(f"Lineages started: {len(lineages)}")
    print(f"Generations reached: {max(chem.generations.keys())}")

    if replicators:
        print("\n🎉 SELF-REPLICATION EMERGED!")
        print("\nMost successful replicators:")
        rep_success = [(r, len([e for e in chem.replication_events if e['template'] == r.seq]))
                      for r in replicators]
        rep_success.sort(key=lambda x: x[1], reverse=True)

        for rep, count in rep_success[:5]:
            print(f"  {rep.seq:20s}: {count} offspring produced")

    if len(chem.generations.keys()) > 2:
        print(f"\n🌟 MULTI-GENERATIONAL LINEAGES EMERGED!")
        print(f"Reached generation {max(chem.generations.keys())}")

    return chem


if __name__ == '__main__':
    chem = experiment_simple_replication()
