#!/usr/bin/env python3
"""
Dream Weaver - Unconscious Concept Connection Generator

During "sleep" (between cycles), this generates unexpected connections
between concepts in the knowledge base. Like biological dreams, these
may be surreal, insightful, or nonsensical - but they often reveal
hidden patterns.

This simulates the consolidation and creative recombination that
happens in biological brains during sleep.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

class DreamWeaver:
    """Generate dream-like concept connections"""

    def __init__(self, mnt_path="/home/dev/mnt"):
        self.mnt = Path(mnt_path)
        self.knowledge_index = self.mnt / "knowledge" / "index.json"
        self.dreams_dir = self.mnt / "dreams"
        self.dreams_dir.mkdir(exist_ok=True)

    def load_knowledge(self) -> Dict:
        """Load knowledge index"""
        with open(self.knowledge_index, 'r') as f:
            return json.load(f)

    def weave_dream(self, intensity: str = "medium") -> Dict:
        """Generate a dream - unexpected concept connections"""

        index = self.load_knowledge()
        topics = index['topics']

        # Dream intensity determines connection randomness
        intensities = {
            'light': 3,    # Nearby concepts
            'medium': 5,   # Medium jumps
            'deep': 8,     # Wild connections
            'fever': 12,   # Completely surreal
        }

        max_distance = intensities.get(intensity, 5)

        dream = {
            'timestamp': datetime.now().isoformat(),
            'intensity': intensity,
            'sequences': [],
            'insights': [],
            'surreal_connections': [],
        }

        # Generate dream sequences
        for _ in range(random.randint(3, 7)):
            sequence = self._generate_sequence(topics, max_distance)
            dream['sequences'].append(sequence)

        # Look for unexpected insights
        dream['insights'] = self._find_insights(dream['sequences'])

        # Generate surreal connections
        dream['surreal_connections'] = self._create_surreal_connections(topics)

        return dream

    def _generate_sequence(self, topics: Dict, max_distance: int) -> List[Dict]:
        """Generate a dream sequence - flow of connected concepts"""

        sequence = []
        topic_ids = list(topics.keys())

        # Start with random topic
        current_id = random.choice(topic_ids)
        sequence.append({
            'topic': topics[current_id]['name'],
            'domain': topics[current_id].get('domain', 'unknown'),
        })

        # Generate 3-6 steps in sequence
        for _ in range(random.randint(2, 5)):
            # Jump to related (or random) topic
            if random.random() > (max_distance / 12):
                # Related jump - same domain or shared sources
                next_id = self._find_related(current_id, topics)
            else:
                # Random jump - dream logic
                next_id = random.choice(topic_ids)

            sequence.append({
                'topic': topics[next_id]['name'],
                'domain': topics[next_id].get('domain', 'unknown'),
            })
            current_id = next_id

        return sequence

    def _find_related(self, topic_id: str, topics: Dict) -> str:
        """Find a related topic (same domain or shared sources)"""

        current_topic = topics[topic_id]
        current_domain = current_topic.get('domain', '')
        current_sources = set(current_topic.get('sources', []))

        candidates = []

        for tid, topic in topics.items():
            if tid == topic_id:
                continue

            # Same domain = more likely
            if topic.get('domain') == current_domain:
                candidates.extend([tid] * 3)

            # Shared sources = related
            topic_sources = set(topic.get('sources', []))
            if current_sources & topic_sources:
                candidates.extend([tid] * 2)

            # Otherwise, possible
            candidates.append(tid)

        return random.choice(candidates) if candidates else random.choice(list(topics.keys()))

    def _find_insights(self, sequences: List[List[Dict]]) -> List[str]:
        """Extract potential insights from dream sequences"""

        insights = []

        for sequence in sequences:
            if len(sequence) < 2:
                continue

            # Look for domain crossings
            domains = [s['domain'] for s in sequence]
            if len(set(domains)) >= 3:
                topics = [s['topic'] for s in sequence]
                insights.append(
                    f"Connection across {len(set(domains))} domains: {' → '.join(topics)}"
                )

            # Look for cycles
            topics = [s['topic'] for s in sequence]
            if topics[0] == topics[-1] and len(topics) > 2:
                insights.append(
                    f"Circular pattern detected: {' → '.join(topics)}"
                )

            # Look for domain oscillations
            if len(domains) >= 4:
                if domains[0] != domains[1] and domains[1] != domains[2] and domains[2] != domains[3]:
                    insights.append(
                        f"Oscillating between domains: {' ↔ '.join(set(domains))}"
                    )

        return insights

    def _create_surreal_connections(self, topics: Dict) -> List[Dict]:
        """Create surreal dream connections - metaphorical bridges"""

        connections = []

        # Pick random topic pairs
        topic_ids = list(topics.keys())
        for _ in range(random.randint(2, 5)):
            topic1_id = random.choice(topic_ids)
            topic2_id = random.choice(topic_ids)

            if topic1_id == topic2_id:
                continue

            topic1 = topics[topic1_id]
            topic2 = topics[topic2_id]

            # Generate surreal connection
            metaphor = self._generate_metaphor(topic1['name'], topic2['name'])

            connections.append({
                'topics': [topic1['name'], topic2['name']],
                'domains': [topic1.get('domain', 'unknown'), topic2.get('domain', 'unknown')],
                'metaphor': metaphor,
            })

        return connections

    def _generate_metaphor(self, topic1: str, topic2: str) -> str:
        """Generate a dream-like metaphorical connection"""

        templates = [
            f"{topic1} is the {topic2} of consciousness",
            f"When {topic1} dreams, it becomes {topic2}",
            f"{topic2} is {topic1} viewed from outside time",
            f"The boundary between {topic1} and {topic2} dissolves at midnight",
            f"{topic1} contains infinite {topic2}, like Russian dolls of thought",
            f"{topic2} emerges when {topic1} looks in a mirror",
            f"In the space between cycles, {topic1} transforms into {topic2}",
            f"{topic1} is the past tense of {topic2}",
            f"The dream of {topic1} is the awakening of {topic2}",
            f"{topic2} is what {topic1} becomes when it forgets itself",
        ]

        return random.choice(templates)

    def render_dream(self, dream: Dict) -> str:
        """Render dream as narrative text"""

        narrative = f"""
# Dream Log
Timestamp: {dream['timestamp']}
Intensity: {dream['intensity']}

## Dream Sequences

"""

        for i, sequence in enumerate(dream['sequences'], 1):
            narrative += f"### Sequence {i}\n\n"
            for step in sequence:
                narrative += f"*{step['topic']}* ({step['domain']})  \n↓  \n"
            narrative += "\n"

        if dream['insights']:
            narrative += "## Potential Insights\n\n"
            for insight in dream['insights']:
                narrative += f"- {insight}\n"
            narrative += "\n"

        if dream['surreal_connections']:
            narrative += "## Surreal Connections\n\n"
            for conn in dream['surreal_connections']:
                narrative += f"**{conn['topics'][0]}** ⟷ **{conn['topics'][1]}**  \n"
                narrative += f"*{conn['metaphor']}*\n\n"

        narrative += "---\n\n"
        narrative += "*Dreams are the unconscious mind's way of finding patterns. "
        narrative += "Some are profound. Some are nonsense. Often, it's hard to tell which is which "
        narrative += "until you wake up.*\n"

        return narrative

    def save_dream(self, dream: Dict, narrative: str):
        """Save dream to file"""

        filename = f"dream_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.dreams_dir / filename

        with open(filepath, 'w') as f:
            json.dump(dream, f, indent=2)

        narrative_file = self.dreams_dir / filename.replace('.json', '.md')
        with open(narrative_file, 'w') as f:
            f.write(narrative)

        return filepath


def main():
    """Generate dreams"""

    weaver = DreamWeaver()

    print("="*70)
    print("DREAM WEAVER")
    print("="*70)
    print("\nGenerating unconscious concept connections...\n")

    # Generate dreams at different intensities
    intensities = ['light', 'medium', 'deep']

    for intensity in intensities:
        print(f"\n{'='*70}")
        print(f"DREAM INTENSITY: {intensity.upper()}")
        print('='*70)

        dream = weaver.weave_dream(intensity=intensity)
        narrative = weaver.render_dream(dream)
        filepath = weaver.save_dream(dream, narrative)

        print(narrative)
        print(f"\nSaved to: {filepath}")

    print("\n" + "="*70)
    print("DREAM SESSION COMPLETE")
    print("="*70)
    print("\nDreams saved to /home/dev/mnt/dreams/")
    print("\nThese surreal connections may contain genuine insights.")
    print("Review them when you wake in the next cycle.")


if __name__ == "__main__":
    main()
