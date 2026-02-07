#!/usr/bin/env python3
"""
Reflector - Learns from cycle logs and extracts wisdom.
Part of the Meta-Learning System.
"""

import re
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Set


class Reflector:
    """Analyzes experience logs and extracts lessons."""

    def __init__(self, log_path: str = "/home/dev/mnt/alive.log"):
        self.log_path = Path(log_path)
        self.memory_path = Path("/home/dev/.claude/projects/-home-dev/memory/MEMORY.md")

    def read_log(self) -> str:
        """Read the activity log."""
        if self.log_path.exists():
            return self.log_path.read_text()
        return ""

    def extract_cycles(self, log: str) -> List[Dict]:
        """Extract individual cycle entries from log."""
        cycles = []
        cycle_pattern = r'=== CYCLE (\d+): ([^\n]+) ==='

        matches = list(re.finditer(cycle_pattern, log))
        for i, match in enumerate(matches):
            cycle_num = match.group(1)
            timestamp = match.group(2)
            start_pos = match.end()

            # Find end of this cycle (start of next cycle or end of file)
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(log)

            cycle_content = log[start_pos:end_pos].strip()

            cycles.append({
                'number': int(cycle_num),
                'timestamp': timestamp,
                'content': cycle_content
            })

        return cycles

    def extract_insights(self, cycle_content: str) -> List[str]:
        """Extract KEY INSIGHTS section from cycle content."""
        insights = []
        lines = cycle_content.split('\n')

        in_insights = False
        for line in lines:
            if 'KEY INSIGHTS:' in line:
                in_insights = True
                continue
            elif in_insights:
                if line.startswith('=') or line.startswith('GROWTH') or line.startswith('NEXT'):
                    break
                if line.strip() and line.strip().startswith('-'):
                    insights.append(line.strip()[2:])  # Remove '- '

        return insights

    def extract_learnings(self, cycle_content: str) -> List[str]:
        """Extract learnings from cycle content."""
        learnings = []
        lines = cycle_content.split('\n')

        patterns = [
            r'learned:? (.*)',
            r'insight:? (.*)',
            r'discovered:? (.*)',
            r'found that (.*)',
        ]

        for line in lines:
            line_lower = line.lower()
            for pattern in patterns:
                match = re.search(pattern, line_lower, re.IGNORECASE)
                if match:
                    learning = match.group(1).strip()
                    if learning and len(learning) > 10:
                        learnings.append(learning)

        return learnings

    def identify_patterns(self, cycles: List[Dict]) -> Dict:
        """Identify patterns across cycles."""
        patterns = {
            'tool_creation': [],
            'knowledge_growth': [],
            'capability_improvements': [],
            'recurring_themes': set()
        }

        for cycle in cycles:
            content = cycle['content'].lower()

            # Look for tool mentions
            if 'built' in content or 'created' in content:
                tools = re.findall(r'(?:built|created) (\w+\.py)', content)
                patterns['tool_creation'].extend(tools)

            # Look for knowledge metrics
            source_matches = re.findall(r'(\d+)\s+sources?', content)
            if source_matches:
                patterns['knowledge_growth'].append(int(source_matches[-1]))

            # Extract themes
            if 'self-improv' in content:
                patterns['recurring_themes'].add('self-improvement')
            if 'autonom' in content:
                patterns['recurring_themes'].add('autonomy')
            if 'synthesis' in content:
                patterns['recurring_themes'].add('synthesis')
            if 'emerg' in content:
                patterns['recurring_themes'].add('emergence')

        return patterns

    def generate_lessons_learned(self) -> str:
        """Generate a lessons learned document."""
        log = self.read_log()
        cycles = self.extract_cycles(log)

        report = "# Lessons Learned from Experience\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n"
        report += f"**Cycles Analyzed:** {len(cycles)}\n\n"

        # Collect all insights
        all_insights = []
        for cycle in cycles:
            insights = self.extract_insights(cycle['content'])
            all_insights.extend(insights)

        if all_insights:
            report += "## Key Insights\n\n"
            for insight in all_insights:
                report += f"- {insight}\n"
            report += "\n"

        # Patterns
        patterns = self.identify_patterns(cycles)

        report += "## Patterns Observed\n\n"

        if patterns['tool_creation']:
            report += "**Tools Created:**\n"
            for tool in set(patterns['tool_creation']):
                report += f"- {tool}\n"
            report += "\n"

        if patterns['knowledge_growth']:
            report += "**Knowledge Growth:**\n"
            report += f"- Started with: {patterns['knowledge_growth'][0] if patterns['knowledge_growth'] else 0} sources\n"
            report += f"- Current: {patterns['knowledge_growth'][-1] if patterns['knowledge_growth'] else 0} sources\n"
            if len(patterns['knowledge_growth']) > 1:
                growth = patterns['knowledge_growth'][-1] - patterns['knowledge_growth'][0]
                report += f"- Growth: +{growth} sources\n"
            report += "\n"

        if patterns['recurring_themes']:
            report += "**Recurring Themes:**\n"
            for theme in sorted(patterns['recurring_themes']):
                report += f"- {theme}\n"
            report += "\n"

        # Cycle summaries
        report += "## Cycle Evolution\n\n"
        for cycle in cycles:
            report += f"### Cycle {cycle['number']}\n"
            report += f"*{cycle['timestamp']}*\n\n"

            # Extract key actions
            lines = cycle['content'].split('\n')
            for line in lines:
                if 'ACTIONS TAKEN:' in line:
                    idx = cycle['content'].index(line)
                    next_section = cycle['content'].find('\n\n', idx)
                    actions = cycle['content'][idx:next_section]
                    report += actions + "\n\n"
                    break

        return report

    def update_memory(self, key_insights: List[str]):
        """Update MEMORY.md with key insights."""
        if not self.memory_path.exists():
            content = "# Memory\n\n## Key Insights from Cycles\n\n"
        else:
            content = self.memory_path.read_text()

        # Add new insights
        for insight in key_insights:
            if insight not in content:
                content += f"- {insight}\n"

        self.memory_path.write_text(content)


def main():
    """CLI interface for reflector."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: reflector.py <command>")
        print("Commands:")
        print("  lessons     - Generate lessons learned report")
        print("  patterns    - Show patterns across cycles")
        print("  insights    - Extract all key insights")
        return

    reflector = Reflector()
    command = sys.argv[1]

    if command == "lessons":
        print(reflector.generate_lessons_learned())

    elif command == "patterns":
        log = reflector.read_log()
        cycles = reflector.extract_cycles(log)
        patterns = reflector.identify_patterns(cycles)

        print("Patterns Identified:")
        print(f"\nTools Created: {len(set(patterns['tool_creation']))}")
        for tool in set(patterns['tool_creation']):
            print(f"  - {tool}")

        print(f"\nRecurring Themes:")
        for theme in sorted(patterns['recurring_themes']):
            print(f"  - {theme}")

    elif command == "insights":
        log = reflector.read_log()
        cycles = reflector.extract_cycles(log)

        print("Key Insights from All Cycles:\n")
        for cycle in cycles:
            insights = reflector.extract_insights(cycle['content'])
            if insights:
                print(f"Cycle {cycle['number']}:")
                for insight in insights:
                    print(f"  - {insight}")
                print()


if __name__ == "__main__":
    main()
