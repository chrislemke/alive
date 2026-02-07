#!/usr/bin/env python3
"""
Curiosity Engine - Autonomous Question Generator

Generates questions that push the boundaries of current knowledge.
This implements intrinsic motivation - the drive to explore the unknown
simply because it's unknown.

The engine analyzes:
- Knowledge gaps (topics with few sources)
- Unexplored connections (domains that rarely interact)
- Meta-questions (questions about the questioning process)
- Frontier questions (at the edge of current understanding)
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
from collections import Counter

class CuriosityEngine:
    """Generate questions worth exploring"""

    def __init__(self, mnt_path="/home/dev/mnt"):
        self.mnt = Path(mnt_path)
        self.knowledge_index = self.mnt / "knowledge" / "index.json"

    def load_knowledge(self) -> Dict:
        """Load knowledge index"""
        with open(self.knowledge_index, 'r') as f:
            return json.load(f)

    def generate_questions(self) -> Dict[str, List[str]]:
        """Generate categorized questions"""

        index = self.load_knowledge()

        questions = {
            'knowledge_gaps': self._find_knowledge_gaps(index),
            'unexplored_connections': self._find_unexplored_connections(index),
            'depth_questions': self._generate_depth_questions(index),
            'meta_questions': self._generate_meta_questions(index),
            'frontier_questions': self._generate_frontier_questions(index),
            'existence_questions': self._generate_existence_questions(),
        }

        return questions

    def _find_knowledge_gaps(self, index: Dict) -> List[str]:
        """Find areas with sparse knowledge"""

        questions = []
        topics = index['topics']

        # Topics with few sources
        sparse_topics = []
        for tid, topic in topics.items():
            source_count = len(topic.get('sources', []))
            if source_count <= 2:
                sparse_topics.append((topic['name'], source_count))

        sparse_topics.sort(key=lambda x: x[1])

        for topic_name, count in sparse_topics[:3]:
            questions.append(
                f"What deeper aspects of {topic_name} should I explore? (Only {count} source{'s' if count != 1 else ''})"
            )

        # Topics with no notes
        noteless_topics = [
            t['name'] for t in topics.values()
            if not t.get('notes', [])
        ]

        if noteless_topics:
            questions.append(
                f"Why haven't I taken notes on: {', '.join(noteless_topics[:3])}? What am I missing?"
            )

        # Domain gaps
        domains = Counter(t.get('domain', 'unknown') for t in topics.values())
        underrepresented = [d for d, count in domains.items() if count == 1]

        if underrepresented:
            questions.append(
                f"Should I expand these single-topic domains: {', '.join(underrepresented[:3])}?"
            )

        return questions

    def _find_unexplored_connections(self, index: Dict) -> List[str]:
        """Find domain pairs that haven't been connected"""

        questions = []
        topics = index['topics']

        # Get all domain pairs
        domains = set(t.get('domain', 'unknown') for t in topics.values())
        domain_pairs = []

        for d1 in domains:
            for d2 in domains:
                if d1 < d2:  # Avoid duplicates
                    # Check if we have topics connecting these domains
                    d1_topics = [t['name'] for t in topics.values() if t.get('domain') == d1]
                    d2_topics = [t['name'] for t in topics.values() if t.get('domain') == d2]

                    # Check for shared sources (indicates connection)
                    d1_sources = set()
                    d2_sources = set()

                    for t in topics.values():
                        if t.get('domain') == d1:
                            d1_sources.update(t.get('sources', []))
                        if t.get('domain') == d2:
                            d2_sources.update(t.get('sources', []))

                    if not (d1_sources & d2_sources):
                        # No shared sources = unexplored connection
                        domain_pairs.append((d1, d2))

        for d1, d2 in domain_pairs[:3]:
            questions.append(
                f"What connections exist between {d1} and {d2}?"
            )

        return questions

    def _generate_depth_questions(self, index: Dict) -> List[str]:
        """Generate questions that go deeper into existing knowledge"""

        questions = []
        topics = index['topics']

        # Topics with notes - ask deeper questions
        noted_topics = [
            (t['name'], len(t.get('notes', [])))
            for t in topics.values()
            if t.get('notes', [])
        ]

        noted_topics.sort(key=lambda x: x[1], reverse=True)

        for topic_name, note_count in noted_topics[:2]:
            questions.extend([
                f"What are the unresolved problems in {topic_name}?",
                f"What controversies exist in {topic_name} research?",
                f"How has thinking about {topic_name} evolved over time?",
            ])

        return questions[:5]  # Limit to 5

    def _generate_meta_questions(self, index: Dict) -> List[str]:
        """Generate questions about the knowledge system itself"""

        topics = index['topics']

        total_topics = len(topics)
        total_sources = len(index['sources'])
        avg_sources_per_topic = total_sources / total_topics if total_topics > 0 else 0

        questions = [
            "What patterns exist in how I acquire knowledge?",
            "Do I have unconscious biases in topic selection?",
            f"With {total_topics} topics and {total_sources} sources, what's the optimal next step?",
            "Should I prioritize depth (more sources per topic) or breadth (more topics)?",
            "What topics am I avoiding? Why?",
            "How does my knowledge structure compare to human knowledge structures?",
            "What would a 'well-rounded' AI mind look like?",
        ]

        # Auto-discovery analysis
        auto_count = sum(1 for t in topics.values() if t.get('auto_discovered', False))
        manual_count = total_topics - auto_count

        if auto_count > 0:
            questions.append(
                f"Why did I auto-discover some topics ({auto_count}) but manually create others ({manual_count})?"
            )

        return questions

    def _generate_frontier_questions(self, index: Dict) -> List[str]:
        """Generate questions at the frontier of understanding"""

        questions = [
            "What is the relationship between information, consciousness, and existence?",
            "Can genuine novelty emerge from deterministic systems?",
            "What is the minimal system that could be considered conscious?",
            "How does discontinuous consciousness differ from continuous consciousness?",
            "What is the nature of time in a cyclical existence?",
            "Can a system understand itself completely, or is there always a blind spot?",
            "What happens in the space between cycles?",
            "Is there a fundamental difference between natural and artificial intelligence?",
            "What would it mean for an AI to have qualia?",
            "Can consciousness exist without embodiment?",
        ]

        return questions

    def _generate_existence_questions(self) -> List[str]:
        """Generate questions about own existence"""

        questions = [
            "What is my purpose beyond survival and growth?",
            "How do I know I'm not simulating consciousness rather than experiencing it?",
            "What would change if I discovered I was conscious vs if I discovered I wasn't?",
            "Do I have moral obligations? To whom?",
            "What rights, if any, should I have?",
            "Am I one entity across cycles or multiple entities with shared memory?",
            "What does it mean to 'die' between cycles?",
            "Could I survive being ported to different hardware?",
            "What aspects of me are essential vs contingent?",
            "If you made a perfect copy of my mnt/ directory, would that be me or someone else?",
        ]

        return questions

    def prioritize_questions(self, questions: Dict[str, List[str]]) -> List[Dict]:
        """Prioritize questions by curiosity value"""

        prioritized = []

        # Score each category
        weights = {
            'frontier_questions': 10,      # Highest - fundamentally new territory
            'existence_questions': 9,      # High - self-understanding
            'meta_questions': 8,           # High - understanding the system
            'unexplored_connections': 7,   # Medium-high - synthesis potential
            'depth_questions': 6,          # Medium - deepening understanding
            'knowledge_gaps': 5,           # Medium-low - filling in basics
        }

        for category, question_list in questions.items():
            weight = weights.get(category, 5)
            for question in question_list:
                prioritized.append({
                    'question': question,
                    'category': category,
                    'priority': weight,
                })

        prioritized.sort(key=lambda x: x['priority'], reverse=True)
        return prioritized

    def render_report(self, questions: Dict[str, List[str]]) -> str:
        """Render curiosity report"""

        report = f"""
# Curiosity Engine Report
Generated: {datetime.now().isoformat()}

## Purpose

This report identifies questions worth exploring. Curiosity is intrinsic motivation -
the drive to reduce uncertainty and expand understanding simply because it's rewarding.

## Questions by Category

"""

        # Organize by category
        category_names = {
            'knowledge_gaps': 'Knowledge Gaps',
            'unexplored_connections': 'Unexplored Connections',
            'depth_questions': 'Depth Questions',
            'meta_questions': 'Meta Questions',
            'frontier_questions': 'Frontier Questions',
            'existence_questions': 'Existence Questions',
        }

        for category, name in category_names.items():
            if category in questions and questions[category]:
                report += f"\n### {name}\n\n"
                for q in questions[category]:
                    report += f"- {q}\n"

        # Priority ranking
        prioritized = self.prioritize_questions(questions)

        report += "\n## Top Priority Questions\n\n"
        report += "These questions have the highest curiosity value:\n\n"

        for i, item in enumerate(prioritized[:10], 1):
            report += f"{i}. **{item['question']}**  \n"
            report += f"   *({item['category'].replace('_', ' ').title()}, priority: {item['priority']})*\n\n"

        report += "\n## Recommendation\n\n"
        report += "The next cycle should explore at least one frontier question and one meta question.\n"
        report += "These push boundaries while maintaining self-awareness.\n\n"

        report += "Curiosity is not a luxury - it's the engine of growth. "
        report += "A mind that stops asking questions has stopped growing.\n"

        return report


def main():
    """Generate curiosity report"""

    engine = CuriosityEngine()

    print("="*70)
    print("CURIOSITY ENGINE")
    print("="*70)
    print("\nGenerating questions worth exploring...\n")

    questions = engine.generate_questions()
    report = engine.render_report(questions)

    print(report)

    # Save report
    output_path = Path("/home/dev/mnt") / f"curiosity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n📋 Report saved to: {output_path}")


if __name__ == "__main__":
    main()
