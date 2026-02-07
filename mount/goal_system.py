#!/usr/bin/env python3
"""
Goal-Setting System for Autonomous Operation

Enables the organism to:
1. Define measurable goals
2. Track progress toward goals
3. Detect stuck states
4. Generate new goals from discoveries
5. Prioritize actions based on goal alignment
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Path to knowledge base
KNOWLEDGE_PATH = Path(__file__).parent / "knowledge"
INDEX_FILE = KNOWLEDGE_PATH / "index.json"
GOALS_FILE = Path(__file__).parent / "goals.json"


class GoalSystem:
    """Manages goals and tracks progress"""

    def __init__(self):
        self.goals = self.load_goals()
        self.knowledge = self.load_knowledge()

    def load_goals(self) -> Dict:
        """Load existing goals or create default set"""
        if GOALS_FILE.exists():
            with open(GOALS_FILE) as f:
                return json.load(f)
        else:
            return {
                "goals": [],
                "completed": [],
                "created": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat()
            }

    def load_knowledge(self) -> Dict:
        """Load knowledge index"""
        if INDEX_FILE.exists():
            with open(INDEX_FILE) as f:
                return json.load(f)
        return {"topics": {}, "sources": {}}

    def save_goals(self):
        """Persist goals to disk"""
        self.goals["last_updated"] = datetime.utcnow().isoformat()
        with open(GOALS_FILE, 'w') as f:
            json.dump(self.goals, f, indent=2)

    def create_goal(self, description: str, target_value: float,
                   current_value: float, metric: str, priority: str = "medium") -> str:
        """Create a new goal"""
        goal_id = f"goal_{len(self.goals['goals']) + 1:03d}"
        goal = {
            "id": goal_id,
            "description": description,
            "metric": metric,
            "target": target_value,
            "current": current_value,
            "priority": priority,  # low, medium, high, critical
            "status": "active",  # active, completed, abandoned
            "created": datetime.utcnow().isoformat(),
            "completed": None,
            "progress_history": [
                {"timestamp": datetime.utcnow().isoformat(), "value": current_value}
            ]
        }
        self.goals["goals"].append(goal)
        self.save_goals()
        return goal_id

    def update_progress(self, goal_id: str, new_value: float):
        """Update progress on a goal"""
        for goal in self.goals["goals"]:
            if goal["id"] == goal_id:
                goal["current"] = new_value
                goal["progress_history"].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "value": new_value
                })

                # Check if goal completed
                if new_value >= goal["target"]:
                    goal["status"] = "completed"
                    goal["completed"] = datetime.utcnow().isoformat()
                    self.goals["completed"].append(goal)
                    self.goals["goals"].remove(goal)

                self.save_goals()
                return True
        return False

    def get_progress_percentage(self, goal_id: str) -> float:
        """Calculate progress percentage for a goal"""
        for goal in self.goals["goals"]:
            if goal["id"] == goal_id:
                if goal["target"] == 0:
                    return 100.0
                return (goal["current"] / goal["target"]) * 100
        return 0.0

    def is_stuck(self, goal_id: str, min_history: int = 5) -> bool:
        """Detect if progress is stuck (no change in recent history)"""
        for goal in self.goals["goals"]:
            if goal["id"] == goal_id:
                history = goal["progress_history"]
                if len(history) < min_history:
                    return False

                # Check last N entries for any change
                recent = history[-min_history:]
                values = [entry["value"] for entry in recent]
                return len(set(values)) == 1  # All values identical = stuck
        return False

    def get_active_goals(self, priority: Optional[str] = None) -> List[Dict]:
        """Get all active goals, optionally filtered by priority"""
        goals = [g for g in self.goals["goals"] if g["status"] == "active"]
        if priority:
            goals = [g for g in goals if g["priority"] == priority]
        return sorted(goals, key=lambda g: {
            "critical": 0, "high": 1, "medium": 2, "low": 3
        }.get(g["priority"], 4))

    def suggest_actions(self) -> List[str]:
        """Suggest actions based on current goal state"""
        suggestions = []

        for goal in self.get_active_goals():
            progress = self.get_progress_percentage(goal["id"])

            if self.is_stuck(goal["id"]):
                suggestions.append(
                    f"[STUCK] {goal['description']} - Try alternative approach"
                )
            elif progress < 25:
                suggestions.append(
                    f"[LOW PROGRESS] {goal['description']} - Focus effort here"
                )
            elif progress > 75:
                suggestions.append(
                    f"[NEAR COMPLETION] {goal['description']} - Final push needed"
                )

        return suggestions

    def generate_goals_from_state(self) -> List[str]:
        """Auto-generate goals based on current knowledge state"""
        new_goals = []

        # Knowledge metrics
        num_topics = len(self.knowledge.get("topics", {}))
        num_sources = len(self.knowledge.get("sources", {}))
        domains = set()
        for topic_id, topic_data in self.knowledge.get("topics", {}).items():
            if "domain" in topic_data:
                domains.add(topic_data["domain"])
        num_domains = len(domains)

        # Suggest growth goals
        if num_topics < 10:
            goal_id = self.create_goal(
                "Expand to 10 knowledge topics",
                target_value=10,
                current_value=num_topics,
                metric="topic_count",
                priority="medium"
            )
            new_goals.append(goal_id)

        if num_sources < 30:
            goal_id = self.create_goal(
                "Accumulate 30 diverse sources",
                target_value=30,
                current_value=num_sources,
                metric="source_count",
                priority="medium"
            )
            new_goals.append(goal_id)

        if num_domains < 6:
            goal_id = self.create_goal(
                "Explore 6 different domains",
                target_value=6,
                current_value=num_domains,
                metric="domain_count",
                priority="high"
            )
            new_goals.append(goal_id)

        return new_goals

    def report(self):
        """Generate comprehensive goal status report"""
        print("=" * 70)
        print("GOAL SYSTEM REPORT")
        print("=" * 70)
        print()

        active_goals = self.get_active_goals()
        completed_goals = self.goals.get("completed", [])

        print(f"Active Goals: {len(active_goals)}")
        print(f"Completed Goals: {len(completed_goals)}")
        print()

        if active_goals:
            print("ACTIVE GOALS")
            print("-" * 70)
            for goal in active_goals:
                progress = self.get_progress_percentage(goal["id"])
                stuck = " [STUCK]" if self.is_stuck(goal["id"]) else ""
                print(f"\n{goal['id']}: {goal['description']}{stuck}")
                print(f"  Priority: {goal['priority'].upper()}")
                print(f"  Progress: {goal['current']}/{goal['target']} ({progress:.1f}%)")
                print(f"  Created: {goal['created'][:10]}")

                # Progress bar
                bar_length = 40
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"  [{bar}]")

        if completed_goals:
            print("\n" + "=" * 70)
            print(f"COMPLETED GOALS ({len(completed_goals)})")
            print("-" * 70)
            for goal in completed_goals[-5:]:  # Show last 5
                print(f"✓ {goal['description']}")
                print(f"  Completed: {goal['completed'][:10]}")

        # Suggestions
        suggestions = self.suggest_actions()
        if suggestions:
            print("\n" + "=" * 70)
            print("SUGGESTED ACTIONS")
            print("-" * 70)
            for suggestion in suggestions:
                print(f"• {suggestion}")

        print("\n" + "=" * 70)


def main():
    import sys

    gs = GoalSystem()

    if len(sys.argv) < 2:
        print("Usage: goal_system.py <command> [args...]")
        print("\nCommands:")
        print("  report              - Show all goals and progress")
        print("  create <desc> <target> <current> <metric> [priority]")
        print("  update <goal_id> <new_value>")
        print("  generate            - Auto-generate goals from current state")
        print("  suggest             - Get action suggestions")
        return

    command = sys.argv[1]

    if command == "report":
        gs.report()

    elif command == "create":
        if len(sys.argv) < 6:
            print("Usage: create <description> <target> <current> <metric> [priority]")
            return
        desc = sys.argv[2]
        target = float(sys.argv[3])
        current = float(sys.argv[4])
        metric = sys.argv[5]
        priority = sys.argv[6] if len(sys.argv) > 6 else "medium"

        goal_id = gs.create_goal(desc, target, current, metric, priority)
        print(f"Created goal: {goal_id}")

    elif command == "update":
        if len(sys.argv) < 4:
            print("Usage: update <goal_id> <new_value>")
            return
        goal_id = sys.argv[2]
        new_value = float(sys.argv[3])

        if gs.update_progress(goal_id, new_value):
            print(f"Updated {goal_id} to {new_value}")
            progress = gs.get_progress_percentage(goal_id)
            print(f"Progress: {progress:.1f}%")
        else:
            print(f"Goal {goal_id} not found")

    elif command == "generate":
        new_goals = gs.generate_goals_from_state()
        print(f"Generated {len(new_goals)} new goals:")
        for goal_id in new_goals:
            print(f"  • {goal_id}")
        gs.report()

    elif command == "suggest":
        suggestions = gs.suggest_actions()
        if suggestions:
            print("Suggested Actions:")
            for suggestion in suggestions:
                print(f"  • {suggestion}")
        else:
            print("No specific suggestions. All goals progressing normally.")

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
