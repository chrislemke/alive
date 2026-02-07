#!/usr/bin/env python3
"""
Play Behavior Emergence

Explores whether play-like behavior can emerge in agents.

Play characteristics to test:
1. Non-instrumental (not directly rewarded)
2. Exploratory (trying novel behaviors)
3. Safe practice (low stakes)
4. Intrinsically motivated (done for itself)
5. Flexible/creative (variable, not stereotyped)

Design:
- Agents in environment with tasks (survival pressure)
- Agents can "play" (explore) or "work" (optimize)
- Play has no immediate reward but improves long-term flexibility
- Test: Do agents spontaneously play when safe?
"""

import random
from collections import defaultdict, deque
from typing import List, Tuple, Dict
from dataclasses import dataclass, field

@dataclass
class Environment:
    """Simple environment with tasks and hazards"""
    size: int = 10
    food_locations: List[Tuple[int, int]] = field(default_factory=list)
    hazard_locations: List[Tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.food_locations:
            # Generate random food locations
            self.food_locations = [
                (random.randint(0, self.size-1), random.randint(0, self.size-1))
                for _ in range(3)
            ]
        if not self.hazard_locations:
            # Generate random hazards
            self.hazard_locations = [
                (random.randint(0, self.size-1), random.randint(0, self.size-1))
                for _ in range(2)
            ]

    def get_food(self, pos: Tuple[int, int]) -> float:
        """Check if position has food"""
        if pos in self.food_locations:
            return 1.0
        # Gradient toward nearest food
        if self.food_locations:
            nearest = min(self.food_locations, key=lambda f: self._distance(pos, f))
            dist = self._distance(pos, nearest)
            return max(0, 0.1 * (1 - dist / self.size))
        return 0.0

    def get_danger(self, pos: Tuple[int, int]) -> float:
        """Check if position has danger"""
        if pos in self.hazard_locations:
            return -1.0
        # Gradient toward nearest hazard
        if self.hazard_locations:
            nearest = min(self.hazard_locations, key=lambda h: self._distance(pos, h))
            dist = self._distance(pos, nearest)
            if dist < 2:
                return -0.5 * (2 - dist) / 2
        return 0.0

    def _distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Manhattan distance"""
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

@dataclass
class Agent:
    """Agent that can work (exploit) or play (explore)"""
    agent_id: int
    position: Tuple[int, int] = (0, 0)
    energy: float = 1.0

    # Behavioral repertoire (learned skills)
    skills: Dict[str, float] = field(default_factory=dict)

    # Play vs. work balance
    play_tendency: float = 0.3  # Probability of playing vs. working

    # Experience tracking
    positions_visited: set = field(default_factory=set)
    novel_experiences: int = 0
    repeated_experiences: int = 0

    # Performance tracking
    food_found: int = 0
    hazards_hit: int = 0

    def __post_init__(self):
        # Initialize basic skills
        self.skills = {
            'move_up': 0.0,
            'move_down': 0.0,
            'move_left': 0.0,
            'move_right': 0.0,
            'explore_random': 0.0,
            'rest': 0.0
        }

    def decide_mode(self, safe: bool) -> str:
        """Decide whether to play or work"""
        # High energy + safety → more likely to play
        safety_factor = 1.5 if safe else 0.5
        energy_factor = self.energy

        play_probability = self.play_tendency * safety_factor * energy_factor

        if random.random() < play_probability:
            return 'play'
        else:
            return 'work'

    def choose_action(self, mode: str, env: Environment) -> str:
        """Choose action based on mode"""
        if mode == 'play':
            # Play: Try novel/rare actions, explore
            if random.random() < 0.7:  # Mostly novel
                # Prefer actions not yet mastered
                unmastered = [skill for skill, level in self.skills.items()
                            if level < 0.5]
                if unmastered:
                    return random.choice(unmastered)
            return random.choice(list(self.skills.keys()))

        else:  # Work mode
            # Work: Exploit best-known strategies
            # Prefer high-skill actions
            if self.skills:
                # Weighted random choice
                actions = list(self.skills.keys())
                weights = [max(0.1, self.skills[a]) for a in actions]
                total = sum(weights)
                # Weighted choice implementation
                r = random.random() * total
                cumsum = 0
                for action, weight in zip(actions, weights):
                    cumsum += weight
                    if r <= cumsum:
                        return action
                return actions[-1]  # Fallback
            return random.choice(list(self.skills.keys()))

    def execute_action(self, action: str, env: Environment) -> Tuple[float, bool]:
        """Execute action, return reward and novelty flag"""
        x, y = self.position
        novel = False

        # Movement actions
        if action == 'move_up':
            new_pos = (x, min(y + 1, env.size - 1))
        elif action == 'move_down':
            new_pos = (x, max(y - 1, 0))
        elif action == 'move_left':
            new_pos = (max(x - 1, 0), y)
        elif action == 'move_right':
            new_pos = (min(x + 1, env.size - 1), y)
        elif action == 'explore_random':
            # Random move (playful exploration)
            new_pos = (
                max(0, min(env.size - 1, x + random.randint(-1, 1))),
                max(0, min(env.size - 1, y + random.randint(-1, 1)))
            )
        else:  # rest
            new_pos = self.position

        # Check if novel
        if new_pos not in self.positions_visited:
            novel = True
            self.novel_experiences += 1
            self.positions_visited.add(new_pos)
        else:
            self.repeated_experiences += 1

        self.position = new_pos

        # Get environmental feedback
        food_reward = env.get_food(new_pos)
        danger_penalty = env.get_danger(new_pos)

        if food_reward > 0.5:
            self.food_found += 1
        if danger_penalty < -0.5:
            self.hazards_hit += 1

        # Total reward
        reward = food_reward + danger_penalty

        # Small novelty bonus (intrinsic motivation)
        if novel:
            reward += 0.1

        return reward, novel

    def learn_from_experience(self, action: str, reward: float, was_playing: bool):
        """Update skills based on experience"""
        # Both play and work contribute to learning, but differently
        if was_playing:
            # Play: Broader learning, less focused
            learning_rate = 0.1
            # Increase skill for tried action
            self.skills[action] += learning_rate * (1 + reward)
        else:
            # Work: Targeted learning
            learning_rate = 0.2
            # Stronger update from work
            self.skills[action] += learning_rate * (1 + reward)

        # Keep skills in [0, 1]
        for skill in self.skills:
            self.skills[skill] = max(0, min(1, self.skills[skill]))

    def update_energy(self, reward: float):
        """Update energy based on reward"""
        # Food increases energy, hazards decrease it
        self.energy += reward * 0.1
        # Decay over time (need to find food)
        self.energy *= 0.99
        # Bounds
        self.energy = max(0, min(1, self.energy))

    def is_safe(self) -> bool:
        """Agent feels safe if high energy"""
        return self.energy > 0.5

    def novelty_seeking(self) -> float:
        """How much agent seeks novelty"""
        if self.novel_experiences + self.repeated_experiences == 0:
            return 0.0
        return self.novel_experiences / (self.novel_experiences + self.repeated_experiences)

class PlaySimulation:
    """Simulation testing play emergence"""

    def __init__(self, num_agents: int = 2):
        self.env = Environment(size=10)
        self.agents = [
            Agent(i, position=(random.randint(0, 9), random.randint(0, 9)))
            for i in range(num_agents)
        ]

        # Tracking
        self.step = 0
        self.play_events = []
        self.work_events = []

    def run(self, num_steps: int = 1000, report_interval: int = 200):
        """Run simulation"""
        print("="*70)
        print("PLAY BEHAVIOR EMERGENCE SIMULATION")
        print("="*70)
        print(f"Testing whether agents spontaneously play when safe")
        print(f"Play = exploratory, non-instrumental, intrinsically motivated")
        print()

        for step in range(num_steps):
            self.step = step

            for agent in self.agents:
                # Decide mode
                safe = agent.is_safe()
                mode = agent.decide_mode(safe)

                # Choose and execute action
                action = agent.choose_action(mode, self.env)
                reward, novel = agent.execute_action(action, self.env)

                # Learn
                agent.learn_from_experience(action, reward, was_playing=(mode=='play'))

                # Update energy
                agent.update_energy(reward)

                # Track
                if mode == 'play':
                    self.play_events.append({
                        'step': step,
                        'agent': agent.agent_id,
                        'action': action,
                        'novel': novel,
                        'energy': agent.energy
                    })
                else:
                    self.work_events.append({
                        'step': step,
                        'agent': agent.agent_id,
                        'action': action,
                        'novel': novel,
                        'energy': agent.energy
                    })

            if (step + 1) % report_interval == 0:
                self._report(step + 1)

        print("\n" + "="*70)
        print("SIMULATION COMPLETE")
        print("="*70)
        self._final_analysis()

    def _report(self, step: int):
        """Progress report"""
        print(f"\n[Step {step}]")

        for agent in self.agents:
            recent_play = sum(1 for e in self.play_events[-100:]
                            if e['agent'] == agent.agent_id)
            recent_work = sum(1 for e in self.work_events[-100:]
                            if e['agent'] == agent.agent_id)
            total_recent = recent_play + recent_work
            play_pct = recent_play / total_recent if total_recent > 0 else 0

            print(f"\n  Agent {agent.agent_id}:")
            print(f"    Energy: {agent.energy:.2f}")
            print(f"    Play/Work ratio (recent 100): {play_pct:.1%} play")
            print(f"    Novelty seeking: {agent.novelty_seeking():.1%}")
            print(f"    Positions visited: {len(agent.positions_visited)}")
            print(f"    Food found: {agent.food_found}, Hazards hit: {agent.hazards_hit}")

            # Top skills
            top_skills = sorted(agent.skills.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"    Top skills: {', '.join([f'{s}({v:.2f})' for s, v in top_skills])}")

    def _final_analysis(self):
        """Analyze whether play emerged"""
        print(f"\nPlay Behavior Analysis:")

        # Overall play vs. work
        total_play = len(self.play_events)
        total_work = len(self.work_events)
        total = total_play + total_work

        print(f"  Total actions: {total}")
        print(f"  Play actions: {total_play} ({total_play/total:.1%})")
        print(f"  Work actions: {total_work} ({total_work/total:.1%})")

        # Play when safe vs. unsafe
        if self.play_events:
            safe_play = sum(1 for e in self.play_events if e['energy'] > 0.5)
            print(f"\n  Play when safe (energy > 0.5): {safe_play/total_play:.1%}")

            # Novelty in play vs. work
            novel_play = sum(1 for e in self.play_events if e['novel'])
            print(f"  Novel experiences during play: {novel_play/total_play:.1%}")

        if self.work_events:
            novel_work = sum(1 for e in self.work_events if e['novel'])
            print(f"  Novel experiences during work: {novel_work/total_work:.1%}")

        # Agent-specific patterns
        print(f"\nAgent Play Patterns:")
        for agent in self.agents:
            agent_play = [e for e in self.play_events if e['agent'] == agent.agent_id]
            agent_work = [e for e in self.work_events if e['agent'] == agent.agent_id]
            total_actions = len(agent_play) + len(agent_work)

            print(f"\n  Agent {agent.agent_id}:")
            print(f"    Final energy: {agent.energy:.2f}")
            print(f"    Play proportion: {len(agent_play)/total_actions:.1%}")
            print(f"    Exploration coverage: {len(agent.positions_visited)}/100 positions")
            print(f"    Success: {agent.food_found} food, {agent.hazards_hit} hazards")

if __name__ == "__main__":
    sim = PlaySimulation(num_agents=3)
    sim.run(num_steps=1000, report_interval=250)
