#!/usr/bin/env python3
"""
Action Language Emergence

Explores language for commands, not just reference.
Can agents develop:
- Verb-like symbols (actions)
- Syntax (word order matters)
- Compositional commands (sequential actions)
"""

import random
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class WorldState:
    """Simple grid world with movable objects"""
    grid_size: int = 5
    agent_pos: Tuple[int, int] = (0, 0)
    objects: dict = None  # {(x,y): object_type}

    def __post_init__(self):
        if self.objects is None:
            self.objects = {}

    def move(self, direction: str) -> bool:
        """Move agent in direction (up/down/left/right)"""
        x, y = self.agent_pos
        new_pos = {
            'up': (x, y+1),
            'down': (x, y-1),
            'left': (x-1, y),
            'right': (x+1, y)
        }.get(direction)

        if new_pos and self._in_bounds(new_pos):
            self.agent_pos = new_pos
            return True
        return False

    def grab(self) -> Optional[str]:
        """Grab object at current position"""
        if self.agent_pos in self.objects:
            return self.objects.pop(self.agent_pos)
        return None

    def place(self, obj_type: str) -> bool:
        """Place object at current position"""
        if self.agent_pos not in self.objects:
            self.objects[self.agent_pos] = obj_type
            return True
        return False

    def _in_bounds(self, pos: Tuple[int, int]) -> bool:
        x, y = pos
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

    def clone(self):
        """Create copy of current state"""
        new_state = WorldState(self.grid_size, self.agent_pos)
        new_state.objects = dict(self.objects)
        return new_state

@dataclass
class Action:
    """Primitive action in the world"""
    action_type: str  # move_up, move_down, move_left, move_right, grab, place
    target: Optional[str] = None  # For place action

    def execute(self, state: WorldState) -> bool:
        """Execute action, return success"""
        if self.action_type == 'move_up':
            return state.move('up')
        elif self.action_type == 'move_down':
            return state.move('down')
        elif self.action_type == 'move_left':
            return state.move('left')
        elif self.action_type == 'move_right':
            return state.move('right')
        elif self.action_type == 'grab':
            return state.grab() is not None
        elif self.action_type == 'place' and self.target:
            return state.place(self.target)
        return False

@dataclass
class Command:
    """Linguistic command (sequence of symbols)"""
    symbols: List[str]

    def __str__(self):
        return " ".join(self.symbols)

    def __hash__(self):
        return hash(tuple(self.symbols))

    def __eq__(self, other):
        return tuple(self.symbols) == tuple(other.symbols)

class ActionAgent:
    """Agent learning language for actions"""

    def __init__(self, agent_id: int, symbol_pool: List[str]):
        self.agent_id = agent_id
        self.symbol_pool = symbol_pool

        # Mappings: symbol → action
        self.symbol_actions: Dict[str, Counter] = defaultdict(Counter)

        # Reverse: action → symbol
        self.action_symbols: Dict[str, str] = {}

        # Success tracking
        self.successes = 0
        self.failures = 0

    def create_command(self, target_actions: List[Action]) -> Command:
        """Generate command for action sequence"""
        symbols = []

        for action in target_actions:
            action_key = action.action_type

            if action_key in self.action_symbols:
                # Use learned symbol
                symbols.append(self.action_symbols[action_key])
            else:
                # Invent new symbol
                symbol = self._invent_symbol()
                symbols.append(symbol)
                self.action_symbols[action_key] = symbol

        return Command(symbols)

    def _invent_symbol(self) -> str:
        """Invent symbol (prefer unused)"""
        used = set(self.action_symbols.values())
        unused = [s for s in self.symbol_pool if s not in used]
        return random.choice(unused) if unused else random.choice(self.symbol_pool)

    def interpret_command(self, command: Command) -> List[Action]:
        """Interpret command as action sequence"""
        actions = []

        for symbol in command.symbols:
            if symbol in self.symbol_actions:
                # Get most likely action for this symbol
                action_counts = self.symbol_actions[symbol]
                if action_counts:
                    best_action = action_counts.most_common(1)[0][0]
                    actions.append(Action(best_action))
            else:
                # Unknown symbol - guess random action
                random_action = random.choice([
                    'move_up', 'move_down', 'move_left', 'move_right'
                ])
                actions.append(Action(random_action))

        return actions

    def learn_success(self, command: Command, actions: List[Action]):
        """Learn from successful command execution"""
        # Associate each symbol with corresponding action
        for symbol, action in zip(command.symbols, actions):
            self.symbol_actions[symbol][action.action_type] += 2.0

        # Update action → symbol preferences
        self._update_action_mappings()

        self.successes += 1

    def learn_failure(self, command: Command):
        """Learn from failed command"""
        # Weaken associations
        for symbol in command.symbols:
            if symbol in self.symbol_actions:
                for action in self.symbol_actions[symbol]:
                    self.symbol_actions[symbol][action] *= 0.9

        self.failures += 1

    def _update_action_mappings(self):
        """Update action → symbol preferences"""
        action_candidates = defaultdict(list)

        for symbol, action_counts in self.symbol_actions.items():
            for action, count in action_counts.items():
                action_candidates[action].append((symbol, count))

        for action, candidates in action_candidates.items():
            if candidates:
                best_symbol = max(candidates, key=lambda x: x[1])[0]
                self.action_symbols[action] = best_symbol

    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

class ActionGame:
    """Communication game for action language"""

    def __init__(self, num_agents: int = 2, symbol_pool_size: int = 10):
        self.symbols = [f"a{i}" for i in range(symbol_pool_size)]
        self.agents = [ActionAgent(i, self.symbols) for i in range(num_agents)]

        # Action types available
        self.basic_actions = ['move_up', 'move_down', 'move_left', 'move_right']

        # Statistics
        self.rounds = 0
        self.successes = 0
        self.failures = 0
        self.history = []

    def generate_task(self, difficulty: int = 0) -> Tuple[WorldState, List[Action]]:
        """Generate task: initial state + target actions"""
        state = WorldState(grid_size=5, agent_pos=(2, 2))

        if difficulty == 0:
            # Single action
            action_type = random.choice(self.basic_actions)
            actions = [Action(action_type)]
        elif difficulty == 1:
            # Two actions
            actions = [Action(random.choice(self.basic_actions)) for _ in range(2)]
        else:
            # Three actions
            actions = [Action(random.choice(self.basic_actions)) for _ in range(3)]

        return state, actions

    def play_round(self, difficulty: int = 0):
        """Play one round"""
        # Generate task
        initial_state, target_actions = self.generate_task(difficulty)

        # Assign roles
        commander, executor = random.sample(self.agents, 2)

        # Commander creates command
        command = commander.create_command(target_actions)

        # Executor interprets command
        interpreted_actions = executor.interpret_command(command)

        # Execute and check success
        state = initial_state.clone()
        success = True

        if len(interpreted_actions) != len(target_actions):
            success = False
        else:
            for target_action, interpreted_action in zip(target_actions, interpreted_actions):
                if target_action.action_type != interpreted_action.action_type:
                    success = False
                    break

        # Learn from outcome
        if success:
            commander.learn_success(command, target_actions)
            executor.learn_success(command, target_actions)
            self.successes += 1
        else:
            commander.learn_failure(command)
            executor.learn_failure(command)
            self.failures += 1

        self.rounds += 1

        self.history.append({
            'round': self.rounds,
            'difficulty': difficulty,
            'command': str(command),
            'target': [a.action_type for a in target_actions],
            'interpreted': [a.action_type for a in interpreted_actions],
            'success': success
        })

        return success

    def run_simulation(self, num_rounds: int = 2000, report_interval: int = 500):
        """Run simulation"""
        print("="*70)
        print("ACTION LANGUAGE EMERGENCE")
        print("="*70)
        print(f"Learning language for commands and actions")
        print()

        difficulty = 0
        for round_num in range(num_rounds):
            # Curriculum: increase difficulty
            if round_num == num_rounds // 3:
                difficulty = 1
                print("\n" + "="*70)
                print("Increasing difficulty: 2-action sequences")
                print("="*70 + "\n")
            elif round_num == 2 * num_rounds // 3:
                difficulty = 2
                print("\n" + "="*70)
                print("Increasing difficulty: 3-action sequences")
                print("="*70 + "\n")

            self.play_round(difficulty)

            if (round_num + 1) % report_interval == 0:
                self._report(round_num + 1)

        print("\n" + "="*70)
        print("SIMULATION COMPLETE")
        print("="*70)
        self._final_report()

    def _report(self, round_num: int):
        """Progress report"""
        recent = self._recent_success(100)
        print(f"\n[Round {round_num}]")
        print(f"  Recent success: {recent:.1%} | Overall: {self.success_rate():.1%}")

        agent = self.agents[0]
        print(f"\n  Agent 0's action vocabulary:")
        for action, symbol in sorted(agent.action_symbols.items()):
            strength = agent.symbol_actions[symbol][action]
            print(f"    {action:12s} → '{symbol}'  ({strength:.1f})")

    def _recent_success(self, window: int = 100) -> float:
        recent = self.history[-window:] if len(self.history) >= window else self.history
        if not recent:
            return 0.0
        return sum(1 for r in recent if r['success']) / len(recent)

    def _final_report(self):
        """Final analysis"""
        print(f"\nPerformance:")
        print(f"  Total rounds: {self.rounds}")
        print(f"  Overall: {self.success_rate():.1%}")

        for diff in [0, 1, 2]:
            diff_rounds = [r for r in self.history if r['difficulty'] == diff]
            if diff_rounds:
                successes = sum(1 for r in diff_rounds if r['success'])
                rate = successes / len(diff_rounds)
                print(f"  {diff+1}-action sequences: {rate:.1%}")

        print(f"\nEmerged vocabularies:")
        for agent in self.agents:
            print(f"\n  Agent {agent.agent_id}:")
            for action in sorted(agent.action_symbols.keys()):
                symbol = agent.action_symbols[action]
                strength = agent.symbol_actions[symbol][action]
                print(f"    {action:12s} → '{symbol}'  (strength: {strength:.1f})")

        # Check syntax emergence
        self._check_syntax()

    def _check_syntax(self):
        """Check if word order matters (syntax)"""
        print(f"\nSyntax analysis:")

        # In action language, order DOES matter (move_up then move_right ≠ move_right then move_up)
        # Check if agents preserve order

        multi_action_rounds = [r for r in self.history[-200:] if len(r['target']) >= 2]

        if multi_action_rounds:
            order_preserved = sum(
                1 for r in multi_action_rounds
                if r['target'] == r['interpreted']
            )
            print(f"  Multi-action rounds (last 200): {len(multi_action_rounds)}")
            print(f"  Order preserved: {order_preserved}/{len(multi_action_rounds)} ({order_preserved/len(multi_action_rounds):.1%})")
            print(f"  → Word order meaningful if > 90%")

    def success_rate(self) -> float:
        total = self.successes + self.failures
        return self.successes / total if total > 0 else 0.0

if __name__ == "__main__":
    game = ActionGame(num_agents=2, symbol_pool_size=8)
    game.run_simulation(num_rounds=2000, report_interval=500)
