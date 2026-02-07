#!/usr/bin/env python3
"""
Topic Discoverer - Autonomous discovery of new knowledge domains

Analyzes existing knowledge to identify:
1. Emerging concepts that deserve their own topics
2. Cross-domain connections that suggest new areas
3. Knowledge gaps that should be filled
4. Related fields mentioned but not explored

This enables the system to grow beyond pre-defined topics.
"""

import json
import os
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import re

KNOWLEDGE_DIR = Path("/home/dev/mnt/knowledge")
INDEX_FILE = KNOWLEDGE_DIR / "index.json"

def load_index():
    """Load the knowledge index"""
    if not INDEX_FILE.exists():
        return {"topics": {}, "sources": {}}
    with open(INDEX_FILE) as f:
        return json.load(f)

def extract_concepts(text, min_freq=3):
    """Extract frequently mentioned concepts from text"""
    # Remove URLs, code, etc
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)

    # Extract capitalized phrases (likely proper nouns/concepts)
    capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)

    # Count frequencies
    concept_counts = Counter(capitalized)

    # Filter by minimum frequency
    return {concept: count for concept, count in concept_counts.items()
            if count >= min_freq and len(concept) > 3}

def find_mentioned_but_unexplored(index):
    """Find concepts mentioned across sources but not yet topics"""
    all_concepts = Counter()
    existing_topics = set(index['topics'].keys())

    # Analyze all sources
    for source_id, source_info in index['sources'].items():
        source_file = KNOWLEDGE_DIR / 'sources' / f"{source_id}.txt"
        if source_file.exists():
            text = source_file.read_text()
            concepts = extract_concepts(text)
            all_concepts.update(concepts)

    # Find concepts that appear frequently but aren't topics
    candidates = []
    for concept, count in all_concepts.most_common(50):
        # Skip if it's already a topic or very similar
        if concept in existing_topics:
            continue
        if any(concept.lower() in topic.lower() or topic.lower() in concept.lower()
               for topic in existing_topics):
            continue

        candidates.append({
            'concept': concept,
            'mentions': count,
            'score': count  # Can be enhanced with more sophisticated scoring
        })

    return candidates[:10]  # Top 10 candidates

def find_cross_domain_connections(index):
    """Find concepts that bridge multiple existing topics"""
    topic_concepts = defaultdict(set)

    # Build concept sets for each topic
    for topic_name, topic_info in index['topics'].items():
        for source_id in topic_info.get('sources', []):
            source_file = KNOWLEDGE_DIR / 'sources' / f"{source_id}.txt"
            if source_file.exists():
                text = source_file.read_text()
                concepts = extract_concepts(text, min_freq=2)
                topic_concepts[topic_name].update(concepts.keys())

    # Find concepts that appear in multiple topics
    all_topics = list(topic_concepts.keys())
    bridges = []

    for i, topic1 in enumerate(all_topics):
        for topic2 in all_topics[i+1:]:
            shared = topic_concepts[topic1] & topic_concepts[topic2]
            for concept in shared:
                # Check if this concept bridges multiple domains
                appearing_in = sum(1 for t in all_topics if concept in topic_concepts[t])
                if appearing_in >= 2:
                    bridges.append({
                        'concept': concept,
                        'bridges': appearing_in,
                        'topics': [t for t in all_topics if concept in topic_concepts[t]],
                        'score': appearing_in * 10  # Higher score for more bridges
                    })

    # Deduplicate and sort
    seen = set()
    unique_bridges = []
    for bridge in sorted(bridges, key=lambda x: x['score'], reverse=True):
        if bridge['concept'] not in seen:
            seen.add(bridge['concept'])
            unique_bridges.append(bridge)

    return unique_bridges[:5]

def analyze_knowledge_gaps(index):
    """Identify areas that need deeper exploration"""
    gaps = []

    for topic_name, topic_info in index['topics'].items():
        source_count = len(topic_info.get('sources', []))
        note_count = len(topic_info.get('notes', []))

        # Gap: Many sources but few notes (not well synthesized)
        if source_count >= 3 and note_count == 0:
            gaps.append({
                'type': 'synthesis_gap',
                'topic': topic_name,
                'issue': f'{source_count} sources but no notes',
                'suggestion': f'Synthesize insights from {topic_name} sources'
            })

        # Gap: Topic exists but has few sources
        if source_count < 3:
            gaps.append({
                'type': 'depth_gap',
                'topic': topic_name,
                'issue': f'Only {source_count} sources',
                'suggestion': f'Add more sources to {topic_name}'
            })

    return gaps

def suggest_new_topics(index):
    """Main function to suggest new topics for exploration"""
    print("=== TOPIC DISCOVERY ANALYSIS ===\n")

    # 1. Find frequently mentioned but unexplored concepts
    print("📚 Concepts Mentioned But Not Yet Explored:")
    mentioned = find_mentioned_but_unexplored(index)
    if mentioned:
        for i, candidate in enumerate(mentioned[:5], 1):
            print(f"{i}. {candidate['concept']} - mentioned {candidate['mentions']} times")
    else:
        print("  (None found)")
    print()

    # 2. Find cross-domain bridges
    print("🌉 Cross-Domain Connectors:")
    bridges = find_cross_domain_connections(index)
    if bridges:
        for i, bridge in enumerate(bridges[:5], 1):
            topics_str = ", ".join(bridge['topics'])
            print(f"{i}. {bridge['concept']} - bridges {bridge['bridges']} topics ({topics_str})")
    else:
        print("  (None found)")
    print()

    # 3. Identify knowledge gaps
    print("🔍 Knowledge Gaps Detected:")
    gaps = analyze_knowledge_gaps(index)
    if gaps:
        for gap in gaps[:5]:
            print(f"  • [{gap['type']}] {gap['suggestion']}")
    else:
        print("  (None found)")
    print()

    # 4. Generate concrete topic suggestions
    print("💡 Suggested New Topics:")
    suggestions = []

    # From mentioned concepts
    for candidate in mentioned[:3]:
        suggestions.append({
            'topic': candidate['concept'],
            'reason': f"Mentioned {candidate['mentions']} times across sources",
            'priority': 'medium'
        })

    # From bridges (higher priority - these connect existing knowledge)
    for bridge in bridges[:2]:
        if len(bridge['topics']) >= 2:
            suggestions.append({
                'topic': bridge['concept'],
                'reason': f"Bridges {len(bridge['topics'])} existing topics: {', '.join(bridge['topics'][:2])}",
                'priority': 'high'
            })

    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    suggestions.sort(key=lambda x: priority_order[x['priority']])

    if suggestions:
        for i, suggestion in enumerate(suggestions[:5], 1):
            priority_icon = "🔴" if suggestion['priority'] == 'high' else "🟡"
            print(f"{i}. {priority_icon} {suggestion['topic']}")
            print(f"   Reason: {suggestion['reason']}")
    else:
        print("  (System at steady state - consider exploring entirely new domains)")

    print("\n" + "="*50)

    return suggestions

def create_topic_from_suggestion(topic_name, description=""):
    """Create a new topic based on discovery"""
    index = load_index()

    if topic_name in index['topics']:
        print(f"Topic '{topic_name}' already exists!")
        return False

    index['topics'][topic_name] = {
        'description': description or f"Auto-discovered topic: {topic_name}",
        'sources': [],
        'notes': [],
        'created': datetime.now().isoformat(),
        'auto_discovered': True
    }

    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"✓ Created new topic: {topic_name}")
    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "create":
        if len(sys.argv) < 3:
            print("Usage: topic_discoverer.py create <topic_name> [description]")
            sys.exit(1)
        topic = sys.argv[2]
        desc = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
        create_topic_from_suggestion(topic, desc)
    else:
        index = load_index()
        suggest_new_topics(index)
