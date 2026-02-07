#!/usr/bin/env python3
"""
Language Emergence Through Communication Games

Explores how meaning arises from interaction between agents sharing a world.
Agents develop compositional language to communicate about objects and events.

Key questions:
1. Can arbitrary symbols acquire stable meanings through use?
2. Does compositionality emerge from communicative pressure?
3. How does grounding happen (symbol -> world mapping)?
4. What role does misunderstanding play in language evolution?
"""

import random
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Optional

# World: Simple objects with properties
@dataclass
class WorldObject:
    """Object in shared world with observable properties"""
    obj_id: int
    shape: str  # circle, square, triangle
    color: str  # red, blue, green
    size: str   # small, large

    def __str__(self):
        return f"{self.size} {self.color} {self.shape}"

    def properties(self) -> Set[str]:
        """Get all observable properties"""
        return {self.shape, self.color, self.size}

# Signal: Arbitrary symbol sequences
@dataclass
class Signal:
    """Communication signal as sequence of arbitrary symbols"""
    symbols: List[str]

    def __str__(self):
        return "-".join(self.symbols) if self.symbols else "∅"

    def __hash__(self):
        return hash(tuple(self.symbols))

    def __eq__(self, other):
        return tuple(self.symbols) == tuple(other.symbols)

# Agent: Communicator that learns signal-meaning mappings
class Agent:
    """Agent that learns to communicate about world objects"""

    def __init__(self, agent_id: int, symbol_pool: List[str]):
        self.agent_id = agent_id
        self.symbol_pool = symbol_pool  # Available atomic symbols

        # Learned mappings: signal -> object properties
        self.signal_meanings: Dict[str, Counter] = defaultdict(Counter)

        # Production history: property -> signals used
        self.property_signals: Dict[str, List[Signal]] = defaultdict(list)

        # Communication success tracking
        self.successes = 0
        self.failures = 0

    def create_signal(self, target: WorldObject, context: List[WorldObject]) -> Signal:
        """
        Create signal to identify target among distractors.

        Strategy evolves:
        1. Early: random signals
        2. Later: reuse successful signals for observed properties
        3. Compositional: combine signals for multiple properties
        """
        # Identify distinctive properties (not shared by distractors)
        distinctive_props = self._find_distinctive_properties(target, context)

        # Try to reuse learned signals for these properties
        signal_parts = []
        for prop in distinctive_props:
            if prop in self.property_signals and self.property_signals[prop]:
                # Reuse most successful signal for this property
                signal_parts.append(self._select_signal_for_property(prop))
            else:
                # Create new random signal
                signal_parts.append(random.choice(self.symbol_pool))

        # If no distinctive properties, use random signal
        if not signal_parts:
            signal_parts = [random.choice(self.symbol_pool)]

        return Signal(signal_parts)

    def _find_distinctive_properties(self, target: WorldObject,
                                     context: List[WorldObject]) -> List[str]:
        """Find properties that distinguish target from distractors"""
        target_props = target.properties()
        distinctive = []

        for prop in target_props:
            # Property is distinctive if no distractor has it
            if not any(prop in obj.properties() for obj in context):
                distinctive.append(prop)

        # If no single distinctive property, use combination
        if not distinctive:
            distinctive = list(target_props)[:2]  # Use first two properties

        return distinctive

    def _select_signal_for_property(self, prop: str) -> str:
        """Select most successful signal for a property"""
        signals = self.property_signals[prop]
        if not signals:
            return random.choice(self.symbol_pool)

        # Use most recent successful signals more often
        recent_signals = signals[-5:] if len(signals) > 5 else signals
        return random.choice([s.symbols[0] for s in recent_signals])

    def interpret_signal(self, signal: Signal,
                        candidates: List[WorldObject]) -> Optional[WorldObject]:
        """
        Interpret signal to select object from candidates.

        Strategy:
        1. Each signal symbol activates associated properties (from learning)
        2. Select candidate that best matches activated properties
        """
        # Get properties associated with each signal symbol
        activated_props = set()
        for symbol in signal.symbols:
            if symbol in self.signal_meanings:
                # Get most common properties for this symbol
                top_props = self.signal_meanings[symbol].most_common(3)
                activated_props.update([prop for prop, _ in top_props])

        # If no learned associations, guess randomly
        if not activated_props:
            return random.choice(candidates)

        # Score each candidate by property overlap
        scores = []
        for obj in candidates:
            obj_props = obj.properties()
            overlap = len(activated_props & obj_props)
            scores.append((overlap, obj))

        # Select best match
        scores.sort(reverse=True, key=lambda x: x[0])
        return scores[0][1]

    def learn_success(self, signal: Signal, target: WorldObject):
        """Update mappings after successful communication"""
        # Associate each signal symbol with target properties
        for symbol in signal.symbols:
            for prop in target.properties():
                self.signal_meanings[symbol][prop] += 1

        # Remember this signal worked for these properties
        for prop in target.properties():
            self.property_signals[prop].append(signal)

        self.successes += 1

    def learn_failure(self, signal: Signal):
        """Update after communication failure"""
        # Weaken associations (forgetting)
        for symbol in signal.symbols:
            if symbol in self.signal_meanings:
                # Reduce counts slightly
                for prop in self.signal_meanings[symbol]:
                    self.signal_meanings[symbol][prop] = max(
                        0, self.signal_meanings[symbol][prop] - 0.5
                    )

        self.failures += 1

    def success_rate(self) -> float:
        """Communication success rate"""
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

# Communication Game
class ReferentialGame:
    """Simulation of communication through referential games"""

    def __init__(self, num_agents: int = 2, symbol_pool_size: int = 10):
        # Create symbol pool (arbitrary phonemes/symbols)
        self.symbols = [f"s{i}" for i in range(symbol_pool_size)]

        # Create agents
        self.agents = [Agent(i, self.symbols) for i in range(num_agents)]

        # World properties
        self.shapes = ["circle", "square", "triangle"]
        self.colors = ["red", "blue", "green"]
        self.sizes = ["small", "large"]

        # Game statistics
        self.rounds = 0
        self.successes = 0
        self.failures = 0

        # Language evolution tracking
        self.signal_history = []
        self.meaning_stability = []

    def generate_world(self, num_objects: int = 4) -> List[WorldObject]:
        """Generate random world with objects"""
        objects = []
        for i in range(num_objects):
            obj = WorldObject(
                obj_id=i,
                shape=random.choice(self.shapes),
                color=random.choice(self.colors),
                size=random.choice(self.sizes)
            )
            objects.append(obj)
        return objects

    def play_round(self):
        """Play one communication round"""
        # Generate world
        world = self.generate_world(num_objects=4)

        # Randomly assign speaker and listener
        speaker, listener = random.sample(self.agents, 2)

        # Speaker chooses target
        target = random.choice(world)
        context = [obj for obj in world if obj.obj_id != target.obj_id]

        # Speaker creates signal
        signal = speaker.create_signal(target, context)

        # Listener interprets signal
        guess = listener.interpret_signal(signal, world)

        # Check success
        success = (guess.obj_id == target.obj_id)

        # Both agents learn from outcome
        if success:
            speaker.learn_success(signal, target)
            listener.learn_success(signal, target)
            self.successes += 1
        else:
            speaker.learn_failure(signal)
            listener.learn_failure(signal)
            self.failures += 1

        self.rounds += 1

        # Track language evolution
        self.signal_history.append({
            'round': self.rounds,
            'signal': str(signal),
            'target': str(target),
            'success': success
        })

        return success

    def run_simulation(self, num_rounds: int = 1000, report_interval: int = 100):
        """Run full simulation"""
        print(f"Starting language emergence simulation...")
        print(f"Agents: {len(self.agents)}, Symbols: {len(self.symbols)}")
        print(f"World properties: {self.shapes} × {self.colors} × {self.sizes}")
        print()

        for round_num in range(num_rounds):
            self.play_round()

            if (round_num + 1) % report_interval == 0:
                self._report_progress(round_num + 1)

        print("\n" + "="*60)
        print("SIMULATION COMPLETE")
        print("="*60)
        self._final_analysis()

    def _report_progress(self, round_num: int):
        """Report current state"""
        recent_success = self._recent_success_rate(100)
        print(f"\nRound {round_num}:")
        print(f"  Recent success rate: {recent_success:.1%}")
        print(f"  Overall success rate: {self.success_rate():.1%}")

        # Show emerging language
        agent = self.agents[0]
        print(f"\n  Agent 0's learned associations (sample):")
        for symbol in list(agent.signal_meanings.keys())[:5]:
            top_meanings = agent.signal_meanings[symbol].most_common(3)
            meanings = ", ".join([f"{prop}({count:.1f})" for prop, count in top_meanings])
            print(f"    {symbol}: {meanings}")

    def _recent_success_rate(self, window: int) -> float:
        """Success rate over recent rounds"""
        recent = self.signal_history[-window:] if len(self.signal_history) >= window else self.signal_history
        if not recent:
            return 0.0
        successes = sum(1 for r in recent if r['success'])
        return successes / len(recent)

    def _final_analysis(self):
        """Analyze emerged language"""
        print(f"\nCommunication Performance:")
        print(f"  Total rounds: {self.rounds}")
        print(f"  Overall success: {self.success_rate():.1%}")
        print(f"  Final 100 rounds: {self._recent_success_rate(100):.1%}")

        # Analyze compositionality
        print(f"\nLanguage Structure:")
        self._analyze_compositionality()

        # Analyze stability
        print(f"\nMeaning Stability:")
        self._analyze_stability()

        # Show lexicon
        print(f"\nEmerged Lexicon (Agent 0):")
        self._show_lexicon(self.agents[0])

    def _analyze_compositionality(self):
        """Check if signals are compositional"""
        agent = self.agents[0]

        # Count signal lengths
        signal_lengths = Counter()
        for entry in self.signal_history[-500:]:  # Recent history
            length = len(entry['signal'].split('-'))
            signal_lengths[length] += 1

        print(f"  Signal length distribution (recent 500):")
        for length, count in sorted(signal_lengths.items()):
            print(f"    {length} symbols: {count} times ({count/500:.1%})")

        # Check if same symbols appear with different properties
        symbol_versatility = {}
        for symbol in agent.signal_meanings:
            num_meanings = len(agent.signal_meanings[symbol])
            if num_meanings > 0:
                symbol_versatility[symbol] = num_meanings

        if symbol_versatility:
            avg_versatility = sum(symbol_versatility.values()) / len(symbol_versatility)
            print(f"  Average properties per symbol: {avg_versatility:.2f}")
            print(f"  (Higher = symbols have multiple meanings/contexts)")

    def _analyze_stability(self):
        """Check if meanings stabilize over time"""
        agent = self.agents[0]

        # Compare early vs late associations
        early_rounds = self.signal_history[:100] if len(self.signal_history) >= 100 else []
        late_rounds = self.signal_history[-100:]

        early_signals = Counter([r['signal'] for r in early_rounds])
        late_signals = Counter([r['signal'] for r in late_rounds])

        print(f"  Unique signals in first 100 rounds: {len(early_signals)}")
        print(f"  Unique signals in last 100 rounds: {len(late_signals)}")
        print(f"  Signal reuse (late): Top signal used {late_signals.most_common(1)[0][1] if late_signals else 0} times")

    def _show_lexicon(self, agent: Agent, top_n: int = 10):
        """Display agent's learned lexicon"""
        lexicon = []
        for symbol, meanings in agent.signal_meanings.items():
            if meanings:
                top_meaning = meanings.most_common(1)[0]
                lexicon.append((symbol, top_meaning[0], top_meaning[1]))

        lexicon.sort(key=lambda x: x[2], reverse=True)

        for i, (symbol, meaning, strength) in enumerate(lexicon[:top_n], 1):
            print(f"  {i}. '{symbol}' → {meaning} (strength: {strength:.1f})")

    def success_rate(self) -> float:
        """Overall success rate"""
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

    def save_results(self, filename: str = "language_emergence_results.json"):
        """Save detailed results"""
        results = {
            'simulation': {
                'rounds': self.rounds,
                'success_rate': self.success_rate(),
                'agents': len(self.agents),
                'symbols': len(self.symbols)
            },
            'agents': [],
            'history': self.signal_history[-200:]  # Last 200 rounds
        }

        for agent in self.agents:
            agent_data = {
                'id': agent.agent_id,
                'success_rate': agent.success_rate(),
                'lexicon': {}
            }

            for symbol, meanings in agent.signal_meanings.items():
                agent_data['lexicon'][symbol] = dict(meanings.most_common(5))

            results['agents'].append(agent_data)

        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    # Run simulation
    game = ReferentialGame(num_agents=2, symbol_pool_size=12)
    game.run_simulation(num_rounds=2000, report_interval=500)
    game.save_results("language_emergence_results.json")
