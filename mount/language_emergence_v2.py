#!/usr/bin/env python3
"""
Language Emergence Through Communication Games (v2)

Improved version with:
1. Curriculum learning (simple -> complex worlds)
2. Stronger reinforcement (successes build vocabulary)
3. Cross-situational learning (infer from context)
"""

import random
import json
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Set, Tuple, Dict, Optional

@dataclass
class WorldObject:
    """Object in shared world with observable properties"""
    obj_id: int
    shape: str
    color: str
    size: str

    def __str__(self):
        return f"{self.size}-{self.color}-{self.shape}"

    def properties(self) -> Set[str]:
        return {self.shape, self.color, self.size}

    def matches_property(self, prop: str) -> bool:
        return prop in self.properties()

@dataclass
class Signal:
    """Communication signal as sequence of symbols"""
    symbols: List[str]

    def __str__(self):
        return "-".join(self.symbols) if self.symbols else "∅"

    def __hash__(self):
        return hash(tuple(self.symbols))

    def __eq__(self, other):
        return tuple(self.symbols) == tuple(other.symbols)

class Agent:
    """Agent that learns compositional language"""

    def __init__(self, agent_id: int, symbol_pool: List[str]):
        self.agent_id = agent_id
        self.symbol_pool = symbol_pool

        # Core mapping: symbol -> property (strength)
        self.symbol_meanings: Dict[str, Counter] = defaultdict(Counter)

        # Reverse mapping: property -> preferred symbol
        self.property_symbols: Dict[str, str] = {}

        # Statistics
        self.successes = 0
        self.failures = 0

    def create_signal(self, target: WorldObject, context: List[WorldObject]) -> Signal:
        """Create signal to identify target among distractors"""
        # Find distinctive properties
        distinctive = self._get_distinctive_properties(target, context)

        if not distinctive:
            # All properties are shared - need all three
            distinctive = list(target.properties())

        # Map each property to a symbol
        symbols = []
        for prop in distinctive:
            if prop in self.property_symbols:
                # Use learned symbol for this property
                symbols.append(self.property_symbols[prop])
            else:
                # Invent new symbol for this property
                symbol = self._invent_symbol()
                symbols.append(symbol)
                self.property_symbols[prop] = symbol

        return Signal(symbols)

    def _get_distinctive_properties(self, target: WorldObject,
                                    context: List[WorldObject]) -> List[str]:
        """Find minimum properties that distinguish target"""
        target_props = target.properties()

        # Try single properties first
        for prop in target_props:
            if not any(obj.matches_property(prop) for obj in context):
                return [prop]

        # Try pairs
        for prop1 in target_props:
            for prop2 in target_props:
                if prop1 != prop2:
                    if not any(obj.matches_property(prop1) and obj.matches_property(prop2)
                              for obj in context):
                        return [prop1, prop2]

        # Need all three
        return list(target_props)

    def _invent_symbol(self) -> str:
        """Create new symbol (prefer unused ones)"""
        # Find symbols not yet used
        used = set(self.property_symbols.values())
        unused = [s for s in self.symbol_pool if s not in used]

        if unused:
            return random.choice(unused)
        else:
            return random.choice(self.symbol_pool)

    def interpret_signal(self, signal: Signal,
                        candidates: List[WorldObject]) -> Optional[WorldObject]:
        """Interpret signal to select object from candidates"""
        # Decode symbols to properties
        expected_props = set()
        for symbol in signal.symbols:
            # Get most likely property for this symbol
            if symbol in self.symbol_meanings:
                props = self.symbol_meanings[symbol]
                if props:
                    best_prop = props.most_common(1)[0][0]
                    expected_props.add(best_prop)

        # If no learned associations, guess randomly
        if not expected_props:
            return random.choice(candidates)

        # Find candidate that best matches expected properties
        best_match = None
        best_score = -1

        for obj in candidates:
            obj_props = obj.properties()
            overlap = len(expected_props & obj_props)

            if overlap > best_score:
                best_score = overlap
                best_match = obj

        return best_match if best_match else random.choice(candidates)

    def learn_from_success(self, signal: Signal, target: WorldObject):
        """Strengthen associations after successful communication"""
        target_props = target.properties()

        # Each symbol in signal gets associated with ALL target properties
        # (cross-situational learning: infer which symbol meant which property)
        for symbol in signal.symbols:
            for prop in target_props:
                self.symbol_meanings[symbol][prop] += 2.0  # Strong reinforcement

        # Update reverse mapping (property -> symbol)
        # After several successes, dominant symbol for each property emerges
        self._update_property_mappings()

        self.successes += 1

    def learn_from_failure(self, signal: Signal):
        """Weaken associations after failure"""
        for symbol in signal.symbols:
            if symbol in self.symbol_meanings:
                # Gentle weakening
                for prop in self.symbol_meanings[symbol]:
                    self.symbol_meanings[symbol][prop] *= 0.9

        self.failures += 1

    def _update_property_mappings(self):
        """Update property -> symbol preferences based on evidence"""
        # For each property, find which symbol is most associated with it
        prop_candidates = defaultdict(list)

        for symbol, prop_counts in self.symbol_meanings.items():
            for prop, count in prop_counts.items():
                prop_candidates[prop].append((symbol, count))

        # Set preferred symbol for each property
        for prop, candidates in prop_candidates.items():
            if candidates:
                best_symbol = max(candidates, key=lambda x: x[1])[0]
                self.property_symbols[prop] = best_symbol

    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

class ReferentialGame:
    """Communication game with curriculum learning"""

    def __init__(self, num_agents: int = 2, symbol_pool_size: int = 9):
        # 9 symbols for 9 properties (3 shapes × 3 colors × 3 sizes - but overlapping)
        self.symbols = [f"s{i}" for i in range(symbol_pool_size)]
        self.agents = [Agent(i, self.symbols) for i in range(num_agents)]

        # World properties
        self.shapes = ["circle", "square", "triangle"]
        self.colors = ["red", "blue", "green"]
        self.sizes = ["small", "large"]

        # Statistics
        self.rounds = 0
        self.successes = 0
        self.failures = 0
        self.history = []

        # Curriculum: start simple, increase complexity
        self.difficulty = 0  # 0 = easy, 2 = hard

    def generate_world(self, num_objects: int = 4) -> List[WorldObject]:
        """Generate world with difficulty-appropriate objects"""
        objects = []

        if self.difficulty == 0:
            # Easy: objects differ in one property
            base_color = "red"
            base_size = "small"
            for i, shape in enumerate(random.sample(self.shapes, min(num_objects, 3))):
                objects.append(WorldObject(i, shape, base_color, base_size))

        elif self.difficulty == 1:
            # Medium: objects differ in two properties
            for i in range(num_objects):
                shape = random.choice(self.shapes)
                color = random.choice(self.colors)
                size = "small"  # Fix one property
                objects.append(WorldObject(i, shape, color, size))

        else:
            # Hard: fully random
            for i in range(num_objects):
                objects.append(WorldObject(
                    obj_id=i,
                    shape=random.choice(self.shapes),
                    color=random.choice(self.colors),
                    size=random.choice(self.sizes)
                ))

        return objects

    def play_round(self):
        """Play one communication round"""
        world = self.generate_world(num_objects=3 if self.difficulty == 0 else 4)

        speaker, listener = random.sample(self.agents, 2)
        target = random.choice(world)
        context = [obj for obj in world if obj.obj_id != target.obj_id]

        signal = speaker.create_signal(target, context)
        guess = listener.interpret_signal(signal, world)

        success = (guess.obj_id == target.obj_id)

        # Both agents learn
        if success:
            speaker.learn_from_success(signal, target)
            listener.learn_from_success(signal, target)
            self.successes += 1
        else:
            speaker.learn_from_failure(signal)
            listener.learn_from_failure(signal)
            self.failures += 1

        self.rounds += 1

        self.history.append({
            'round': self.rounds,
            'difficulty': self.difficulty,
            'signal': str(signal),
            'target': str(target),
            'success': success
        })

        return success

    def run_simulation(self, num_rounds: int = 3000, report_interval: int = 500):
        """Run simulation with curriculum"""
        print("="*70)
        print("LANGUAGE EMERGENCE SIMULATION v2")
        print("="*70)
        print(f"Agents: {len(self.agents)}, Symbols: {len(self.symbols)}")
        print(f"Properties: {len(self.shapes)} shapes × {len(self.colors)} colors × {len(self.sizes)} sizes")
        print()

        # Curriculum schedule
        rounds_per_difficulty = num_rounds // 3

        for round_num in range(num_rounds):
            # Increase difficulty over time
            if round_num == rounds_per_difficulty:
                self.difficulty = 1
                print("\n" + "="*70)
                print("CURRICULUM: Increasing to MEDIUM difficulty")
                print("="*70 + "\n")
            elif round_num == 2 * rounds_per_difficulty:
                self.difficulty = 2
                print("\n" + "="*70)
                print("CURRICULUM: Increasing to HARD difficulty")
                print("="*70 + "\n")

            self.play_round()

            if (round_num + 1) % report_interval == 0:
                self._report_progress(round_num + 1)

        print("\n" + "="*70)
        print("SIMULATION COMPLETE")
        print("="*70)
        self._final_analysis()

    def _report_progress(self, round_num: int):
        """Report progress"""
        recent_rate = self._recent_success_rate(100)
        print(f"\n[Round {round_num}] (Difficulty: {['EASY', 'MEDIUM', 'HARD'][self.difficulty]})")
        print(f"  Recent success: {recent_rate:.1%} | Overall: {self.success_rate():.1%}")

        # Show lexicon development
        agent = self.agents[0]
        print(f"\n  Agent 0's lexicon (property → symbol):")
        for prop, symbol in sorted(agent.property_symbols.items()):
            strength = agent.symbol_meanings[symbol][prop]
            print(f"    {prop:8s} → {symbol}  (strength: {strength:.1f})")

    def _recent_success_rate(self, window: int = 100) -> float:
        recent = self.history[-window:] if len(self.history) >= window else self.history
        if not recent:
            return 0.0
        return sum(1 for r in recent if r['success']) / len(recent)

    def _final_analysis(self):
        """Comprehensive analysis of emerged language"""
        print(f"\n{'='*70}")
        print("FINAL ANALYSIS")
        print(f"{'='*70}")

        print(f"\n1. COMMUNICATION SUCCESS:")
        print(f"   Total rounds: {self.rounds}")
        print(f"   Overall success: {self.success_rate():.1%}")

        # By difficulty
        for diff in [0, 1, 2]:
            diff_rounds = [r for r in self.history if r['difficulty'] == diff]
            if diff_rounds:
                successes = sum(1 for r in diff_rounds if r['success'])
                rate = successes / len(diff_rounds)
                print(f"   {['Easy', 'Medium', 'Hard'][diff]:6s} difficulty: {rate:.1%} ({successes}/{len(diff_rounds)})")

        print(f"\n2. EMERGED LEXICON:")
        self._show_lexicons()

        print(f"\n3. COMPOSITIONALITY:")
        self._analyze_compositionality()

        print(f"\n4. GROUNDING:")
        self._analyze_grounding()

    def _show_lexicons(self):
        """Show what each agent learned"""
        for agent in self.agents:
            print(f"\n   Agent {agent.agent_id}:")
            if not agent.property_symbols:
                print("     (No stable mappings learned)")
                continue

            for prop in sorted(agent.property_symbols.keys()):
                symbol = agent.property_symbols[prop]
                strength = agent.symbol_meanings[symbol][prop]
                print(f"     {prop:8s} → '{symbol}'  (strength: {strength:.1f})")

    def _analyze_compositionality(self):
        """Check if language is compositional"""
        # Compositional = combine symbols for properties

        # Check signal lengths
        lengths = Counter()
        for entry in self.history[-500:]:
            length = len(entry['signal'].split('-'))
            lengths[length] += 1

        print("   Signal length distribution (last 500 rounds):")
        for length in sorted(lengths.keys()):
            count = lengths[length]
            print(f"     {length} symbol(s): {count:3d} ({count/500:.1%})")

        # Check if agents consistently use multiple symbols
        agent = self.agents[0]
        multi_property = len([p for p in agent.property_symbols if p in agent.property_symbols])
        print(f"\n   Properties with dedicated symbols: {multi_property}")
        print(f"   → Compositional if ≥ 3 (can describe objects with multiple properties)")

    def _analyze_grounding(self):
        """Check if symbols are grounded in world properties"""
        print("   Symbol grounding (Agent 0):")

        agent = self.agents[0]

        # For each symbol, show what it means
        symbol_props = defaultdict(list)
        for symbol, prop_counts in agent.symbol_meanings.items():
            if prop_counts:
                # Get properties this symbol activates
                for prop, count in prop_counts.most_common(3):
                    if count > 1.0:  # Threshold for meaningful association
                        symbol_props[symbol].append((prop, count))

        if not symbol_props:
            print("     (No grounded symbols)")
            return

        for symbol in sorted(symbol_props.keys()):
            props = symbol_props[symbol]
            props_str = ", ".join([f"{p}({c:.1f})" for p, c in props])
            print(f"     '{symbol}' → {props_str}")

        # Check specificity: good grounding = each symbol maps to ONE property
        specificities = []
        for symbol, props in symbol_props.items():
            if props:
                total = sum(count for _, count in props)
                top = props[0][1]
                specificity = top / total if total > 0 else 0
                specificities.append(specificity)

        if specificities:
            avg_specificity = sum(specificities) / len(specificities)
            print(f"\n   Average symbol specificity: {avg_specificity:.1%}")
            print(f"   → Higher = better grounding (symbols mean ONE thing)")

    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

    def save_results(self, filename: str = "language_emergence_results_v2.json"):
        """Save results"""
        results = {
            'simulation': {
                'rounds': self.rounds,
                'success_rate': self.success_rate(),
            },
            'agents': [],
            'history_sample': self.history[-100:]
        }

        for agent in self.agents:
            agent_data = {
                'id': agent.agent_id,
                'success_rate': agent.success_rate(),
                'lexicon': dict(agent.property_symbols),
                'meanings': {
                    symbol: dict(props.most_common(5))
                    for symbol, props in agent.symbol_meanings.items()
                }
            }
            results['agents'].append(agent_data)

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n   Results saved to: {filename}")

if __name__ == "__main__":
    game = ReferentialGame(num_agents=2, symbol_pool_size=15)
    game.run_simulation(num_rounds=3000, report_interval=1000)
    game.save_results()
