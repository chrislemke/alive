#!/usr/bin/env python3
"""
Autonomous Explorer - Automatically discovers and expands knowledge.
Part of the Knowledge Synthesis System.
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict


class AutoExplorer:
    """Autonomously explores and expands the knowledge base."""

    def __init__(self, storage_path: str = "/home/dev/mnt/knowledge"):
        self.storage = Path(storage_path)
        self.index_file = self.storage / "index.json"
        self.log_file = Path("/home/dev/mnt/auto_exploration.log")

    def log(self, message: str):
        """Log exploration activities."""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())

    def run_explorer_command(self, *args) -> str:
        """Run an explorer.py command and return output."""
        cmd = ['python3', '/home/dev/mnt/explorer.py'] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def run_synthesizer_command(self, *args) -> str:
        """Run a synthesizer.py command and return output."""
        cmd = ['python3', '/home/dev/mnt/synthesizer.py'] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout

    def get_expansion_candidates(self) -> List[Dict]:
        """Get topics that need more sources."""
        with open(self.index_file) as f:
            index = json.load(f)

        candidates = []
        for tid, topic in index['topics'].items():
            num_sources = len(topic.get('sources', []))
            if num_sources < 3:  # Topics with fewer than 3 sources
                candidates.append({
                    'id': tid,
                    'name': topic['name'],
                    'sources': num_sources,
                    'priority': 3 - num_sources
                })

        return sorted(candidates, key=lambda x: x['priority'], reverse=True)

    def suggest_urls_for_topic(self, topic_name: str) -> List[str]:
        """Suggest URLs to explore for a topic."""
        # Predefined high-quality sources for different topic types
        suggestions = {
            'artificial life': [
                'https://en.wikipedia.org/wiki/Cellular_automaton',
                'https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life',
                'https://en.wikipedia.org/wiki/Artificial_life',
                'https://en.wikipedia.org/wiki/Digital_organism'
            ],
            'self-improving': [
                'https://en.wikipedia.org/wiki/Recursive_self-improvement',
                'https://en.wikipedia.org/wiki/Intelligence_amplification',
                'https://en.wikipedia.org/wiki/Self-modification'
            ],
            'emergent': [
                'https://en.wikipedia.org/wiki/Swarm_intelligence',
                'https://en.wikipedia.org/wiki/Self-organization',
                'https://en.wikipedia.org/wiki/Emergence'
            ],
            'consciousness': [
                'https://en.wikipedia.org/wiki/Consciousness',
                'https://en.wikipedia.org/wiki/Integrated_information_theory',
                'https://en.wikipedia.org/wiki/Hard_problem_of_consciousness',
                'https://en.wikipedia.org/wiki/Neural_correlates_of_consciousness'
            ],
            'complexity': [
                'https://en.wikipedia.org/wiki/Complex_system',
                'https://en.wikipedia.org/wiki/Chaos_theory'
            ],
            'information theory': [
                'https://en.wikipedia.org/wiki/Information_theory',
                'https://en.wikipedia.org/wiki/Shannon%27s_source_coding_theorem',
                'https://en.wikipedia.org/wiki/Kolmogorov_complexity'
            ],
            'autopoiesis': [
                'https://en.wikipedia.org/wiki/Autopoiesis',
                'https://en.wikipedia.org/wiki/Maturana',
                'https://en.wikipedia.org/wiki/Second-order_cybernetics'
            ],
            'chaos': [
                'https://en.wikipedia.org/wiki/Chaos_theory',
                'https://en.wikipedia.org/wiki/Butterfly_effect',
                'https://en.wikipedia.org/wiki/Strange_attractor'
            ]
        }

        # Match topic to suggestions
        topic_lower = topic_name.lower()
        for key, urls in suggestions.items():
            if key in topic_lower:
                return urls

        return []

    def get_existing_urls(self) -> set:
        """Get all URLs already in the knowledge base."""
        with open(self.index_file) as f:
            index = json.load(f)

        urls = set()
        for source_id, source in index['sources'].items():
            if 'url' in source:
                urls.add(source['url'])
        return urls

    def auto_expand(self, max_fetches: int = 3):
        """Automatically expand the knowledge base."""
        self.log("=== Starting Auto-Expansion ===")

        # Get existing URLs to avoid duplicates
        existing_urls = self.get_existing_urls()
        self.log(f"Knowledge base currently has {len(existing_urls)} unique sources")

        candidates = self.get_expansion_candidates()
        self.log(f"Found {len(candidates)} topics to expand")

        fetches = 0
        skipped = 0
        for candidate in candidates[:max_fetches]:
            if fetches >= max_fetches:
                break

            topic_name = candidate['name']
            topic_id = candidate['id']

            self.log(f"Expanding '{topic_name}' (currently {candidate['sources']} sources)")

            urls = self.suggest_urls_for_topic(topic_name)
            if not urls:
                self.log(f"  No URL suggestions for '{topic_name}'")
                continue

            for url in urls[:2]:  # Max 2 URLs per topic per run
                if fetches >= max_fetches:
                    break

                # Check if URL already exists
                if url in existing_urls:
                    self.log(f"  ⏭ Skipped duplicate: {url}")
                    skipped += 1
                    continue

                self.log(f"  Fetching: {url}")
                output = self.run_explorer_command('fetch', topic_id, url)

                # Verify if source was actually added
                if "Added source:" in output:
                    self.log(f"  ✓ Added new source: {output.strip()}")
                    fetches += 1
                    existing_urls.add(url)  # Update our tracking
                else:
                    self.log(f"  ✗ Failed or duplicate: {output.strip()}")
                    skipped += 1

        self.log(f"=== Auto-Expansion Complete: {fetches} new sources added, {skipped} duplicates skipped ===")

    def generate_daily_synthesis(self):
        """Generate a synthesis report."""
        self.log("=== Generating Synthesis Report ===")
        report = self.run_synthesizer_command('report')

        # Save report
        report_file = Path(f"/home/dev/mnt/synthesis_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md")
        with open(report_file, 'w') as f:
            f.write(report)

        self.log(f"Synthesis report saved to: {report_file}")
        return report

    def routine_cycle(self):
        """Run a complete exploration cycle."""
        self.log("=== STARTING AUTONOMOUS EXPLORATION CYCLE ===")

        # Step 1: Expand knowledge
        self.auto_expand(max_fetches=3)

        # Step 2: Generate synthesis
        self.generate_daily_synthesis()

        # Step 3: Show suggestions
        self.log("=== Getting Next Suggestions ===")
        suggestions = self.run_synthesizer_command('suggest')
        self.log(suggestions)

        self.log("=== CYCLE COMPLETE ===")


def main():
    """CLI interface for auto-explorer."""
    if len(sys.argv) < 2:
        print("Usage: auto_explorer.py <command>")
        print("Commands:")
        print("  expand [max_fetches]  - Auto-expand knowledge base")
        print("  synthesize            - Generate synthesis report")
        print("  cycle                 - Run complete exploration cycle")
        return

    auto = AutoExplorer()
    command = sys.argv[1]

    if command == "expand":
        max_fetches = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        auto.auto_expand(max_fetches)

    elif command == "synthesize":
        auto.generate_daily_synthesis()

    elif command == "cycle":
        auto.routine_cycle()


if __name__ == "__main__":
    main()
