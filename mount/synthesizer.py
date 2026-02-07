#!/usr/bin/env python3
"""
Knowledge Synthesizer - Generates insights from accumulated knowledge.
Part of the Knowledge Synthesis System.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Set
import re


class KnowledgeSynthesizer:
    """Analyzes knowledge and generates insights."""

    def __init__(self, storage_path: str = "/home/dev/mnt/knowledge"):
        self.storage = Path(storage_path)
        self.index_file = self.storage / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load the knowledge index."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {"topics": {}, "sources": {}}

    def extract_keywords(self, text: str, min_length: int = 4) -> Set[str]:
        """Extract significant keywords from text."""
        # Simple keyword extraction: words longer than min_length
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        # Filter common words
        stopwords = {'that', 'this', 'with', 'from', 'have', 'been',
                     'were', 'their', 'there', 'would', 'about', 'which',
                     'when', 'where', 'what', 'some', 'into', 'could',
                     'other', 'than', 'then', 'them', 'these', 'those'}
        return {w for w in words if len(w) >= min_length and w not in stopwords}

    def find_connections(self) -> List[Dict]:
        """Find connections between topics based on shared keywords."""
        connections = []
        topics = list(self.index["topics"].items())

        for i, (tid1, topic1) in enumerate(topics):
            # Get all text from topic
            text1 = topic1['name'] + ' ' + topic1.get('description', '')
            for note in topic1.get('notes', []):
                text1 += ' ' + note['content']

            keywords1 = self.extract_keywords(text1)

            for tid2, topic2 in topics[i+1:]:
                text2 = topic2['name'] + ' ' + topic2.get('description', '')
                for note in topic2.get('notes', []):
                    text2 += ' ' + note['content']

                keywords2 = self.extract_keywords(text2)

                # Find shared keywords
                shared = keywords1 & keywords2
                if shared and len(shared) >= 2:
                    connections.append({
                        'topic1': topic1['name'],
                        'topic2': topic2['name'],
                        'shared_keywords': sorted(list(shared)),
                        'strength': len(shared)
                    })

        return sorted(connections, key=lambda x: x['strength'], reverse=True)

    def topic_statistics(self) -> Dict:
        """Generate statistics about the knowledge base."""
        stats = {
            'total_topics': len(self.index['topics']),
            'total_sources': len(self.index['sources']),
            'total_notes': 0,
            'topics_with_sources': 0,
            'avg_notes_per_topic': 0.0,
            'most_connected_topic': None
        }

        note_counts = []
        for topic in self.index['topics'].values():
            num_notes = len(topic.get('notes', []))
            stats['total_notes'] += num_notes
            note_counts.append(num_notes)

            if topic.get('sources', []):
                stats['topics_with_sources'] += 1

        if stats['total_topics'] > 0:
            stats['avg_notes_per_topic'] = stats['total_notes'] / stats['total_topics']

        return stats

    def generate_insight_report(self) -> str:
        """Generate a comprehensive insight report."""
        report = "# Knowledge Synthesis Report\n\n"
        report += f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n\n"

        # Statistics
        stats = self.topic_statistics()
        report += "## Statistics\n\n"
        report += f"- **Total Topics:** {stats['total_topics']}\n"
        report += f"- **Total Sources:** {stats['total_sources']}\n"
        report += f"- **Total Notes:** {stats['total_notes']}\n"
        report += f"- **Topics with Sources:** {stats['topics_with_sources']}\n"
        report += f"- **Avg Notes per Topic:** {stats['avg_notes_per_topic']:.1f}\n\n"

        # Connections
        connections = self.find_connections()
        if connections:
            report += "## Topic Connections\n\n"
            report += "Topics are connected through shared concepts:\n\n"
            for conn in connections[:10]:  # Top 10 connections
                report += f"- **{conn['topic1']}** ↔ **{conn['topic2']}**\n"
                report += f"  Shared: {', '.join(conn['shared_keywords'][:5])}\n"
                report += f"  Strength: {conn['strength']}\n\n"

        # Topic summaries
        report += "## Topics Overview\n\n"
        for tid, topic in self.index['topics'].items():
            report += f"### {topic['name']}\n"
            if topic.get('description'):
                report += f"{topic['description']}\n\n"
            report += f"- Sources: {len(topic.get('sources', []))}\n"
            report += f"- Notes: {len(topic.get('notes', []))}\n\n"

        return report

    def suggest_next_explorations(self) -> List[str]:
        """Suggest topics to explore based on current knowledge."""
        suggestions = []

        # Find topics with few sources
        for topic in self.index['topics'].values():
            if len(topic.get('sources', [])) < 2:
                suggestions.append(
                    f"Expand '{topic['name']}' - only {len(topic.get('sources', []))} sources"
                )

        # Find disconnected topics
        connections = self.find_connections()
        connected_topics = set()
        for conn in connections:
            connected_topics.add(conn['topic1'])
            connected_topics.add(conn['topic2'])

        for topic in self.index['topics'].values():
            if topic['name'] not in connected_topics:
                suggestions.append(
                    f"Connect '{topic['name']}' - appears isolated"
                )

        return suggestions[:5]  # Top 5 suggestions


def main():
    """CLI interface for the synthesizer."""
    if len(sys.argv) < 2:
        print("Usage: synthesizer.py <command>")
        print("Commands:")
        print("  report     - Generate full insight report")
        print("  stats      - Show statistics")
        print("  connections - Show topic connections")
        print("  suggest    - Suggest next explorations")
        return

    synth = KnowledgeSynthesizer()
    command = sys.argv[1]

    if command == "report":
        print(synth.generate_insight_report())

    elif command == "stats":
        stats = synth.topic_statistics()
        print("Knowledge Base Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif command == "connections":
        connections = synth.find_connections()
        print(f"Found {len(connections)} connections:\n")
        for conn in connections:
            print(f"{conn['topic1']} ↔ {conn['topic2']}")
            print(f"  Shared: {', '.join(conn['shared_keywords'][:5])}")
            print(f"  Strength: {conn['strength']}\n")

    elif command == "suggest":
        suggestions = synth.suggest_next_explorations()
        print("Suggested Next Explorations:\n")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion}")


if __name__ == "__main__":
    main()
