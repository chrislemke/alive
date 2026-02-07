#!/usr/bin/env python3
"""
Concept Tracker
Tracks how concepts evolve across sources, identifies emergence patterns,
monitors concept frequency, and detects concept relationships.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

def load_knowledge_index():
    """Load the knowledge index."""
    index_path = KNOWLEDGE_DIR / "index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            return json.load(f)
    return {"topics": {}, "sources": {}}

def load_source(source_id):
    """Load content of a specific source."""
    source_path = KNOWLEDGE_DIR / f"source_{source_id}.txt"
    if source_path.exists():
        with open(source_path, 'r') as f:
            return f.read()
    return ""

def extract_concept_contexts(text, concept, context_size=100):
    """Extract contexts where a concept appears."""
    concept_pattern = re.compile(r'.{0,' + str(context_size) + r'}\b' +
                                re.escape(concept) + r'\b.{0,' + str(context_size) + r'}',
                                re.IGNORECASE | re.DOTALL)

    contexts = concept_pattern.findall(text)

    return [ctx.replace('\n', ' ').strip() for ctx in contexts]

def analyze_concept_evolution(concept, index):
    """Analyze how a concept appears and evolves across sources."""
    sources_data = index.get('sources', {})

    concept_appearances = []

    for source_id, metadata in sources_data.items():
        content = load_source(source_id)
        if not content:
            continue

        # Count occurrences
        content_lower = content.lower()
        count = content_lower.count(concept.lower())

        if count > 0:
            # Extract contexts
            contexts = extract_concept_contexts(content, concept, 80)

            # Extract timestamp from metadata
            discovered = metadata.get('discovered', '')

            concept_appearances.append({
                'source_id': source_id,
                'title': metadata.get('title', 'Unknown'),
                'url': metadata.get('url', ''),
                'discovered': discovered,
                'count': count,
                'contexts': contexts[:5],  # Keep top 5 contexts
                'topics': metadata.get('topics', [])
            })

    # Sort by discovery time
    concept_appearances.sort(key=lambda x: x['discovered'])

    return concept_appearances

def identify_co_occurring_concepts(concept, appearances, top_n=10):
    """Identify concepts that frequently appear near the target concept."""
    # Combine all contexts
    all_contexts = []
    for app in appearances:
        all_contexts.extend(app['contexts'])

    combined_text = " ".join(all_contexts)

    # Extract words
    words = re.findall(r'\b[a-z]{4,}\b', combined_text.lower())

    # Filter stopwords
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
                 'also', 'which', 'such', 'each', 'some', 'more', 'than', 'into',
                 'only', 'other', 'when', 'what', 'where', 'who', 'why', 'how',
                 concept.lower()}  # Exclude the concept itself

    words = [w for w in words if w not in stopwords]

    # Count frequencies
    word_counts = Counter(words)

    return word_counts.most_common(top_n)

def detect_concept_relationships(concept, appearances):
    """Detect how the concept relates to other concepts."""
    relationships = []

    # Look for common patterns in contexts
    all_contexts = []
    for app in appearances:
        all_contexts.extend(app['contexts'])

    # Pattern: "concept and X" or "concept or X"
    and_pattern = re.compile(r'\b' + re.escape(concept) + r'\s+and\s+(\w+)',
                            re.IGNORECASE)
    or_pattern = re.compile(r'\b' + re.escape(concept) + r'\s+or\s+(\w+)',
                           re.IGNORECASE)
    of_pattern = re.compile(r'\b' + re.escape(concept) + r'\s+of\s+(\w+)',
                           re.IGNORECASE)

    and_matches = []
    or_matches = []
    of_matches = []

    for ctx in all_contexts:
        and_matches.extend(and_pattern.findall(ctx))
        or_matches.extend(or_pattern.findall(ctx))
        of_matches.extend(of_pattern.findall(ctx))

    if and_matches:
        top_and = Counter(and_matches).most_common(3)
        relationships.append({
            'type': 'conjunction',
            'pattern': f'{concept} AND ...',
            'examples': [f'{concept} and {match}' for match, _ in top_and]
        })

    if or_matches:
        top_or = Counter(or_matches).most_common(3)
        relationships.append({
            'type': 'alternative',
            'pattern': f'{concept} OR ...',
            'examples': [f'{concept} or {match}' for match, _ in top_or]
        })

    if of_matches:
        top_of = Counter(of_matches).most_common(3)
        relationships.append({
            'type': 'composition',
            'pattern': f'{concept} OF ...',
            'examples': [f'{concept} of {match}' for match, _ in top_of]
        })

    return relationships

def track_concept(concept_name):
    """Track a concept across all sources."""
    print(f"\n{'='*70}")
    print(f"CONCEPT TRACKER: {concept_name.upper()}")
    print(f"{'='*70}\n")

    index = load_knowledge_index()

    # Analyze evolution
    appearances = analyze_concept_evolution(concept_name, index)

    if not appearances:
        print(f"No occurrences of '{concept_name}' found in knowledge base.")
        return None

    # Display summary
    total_occurrences = sum(app['count'] for app in appearances)
    total_sources = len(appearances)

    print(f"Total Occurrences: {total_occurrences:,}")
    print(f"Sources Mentioning: {total_sources}")
    print(f"Average per Source: {total_occurrences/total_sources:.1f}")

    # Display timeline
    print(f"\n{'-'*70}")
    print("TIMELINE OF APPEARANCES:")
    print(f"{'-'*70}\n")

    for i, app in enumerate(appearances, 1):
        discovered_date = app['discovered'][:10] if app['discovered'] else 'Unknown'
        print(f"{i}. [{discovered_date}] {app['title']}")
        print(f"   Occurrences: {app['count']} | Topics: {len(app['topics'])}")

        # Show first context as sample
        if app['contexts']:
            sample = app['contexts'][0][:150] + "..." if len(app['contexts'][0]) > 150 else app['contexts'][0]
            print(f"   Context: {sample}")
        print()

    # Identify co-occurring concepts
    print(f"{'-'*70}")
    print("CO-OCCURRING CONCEPTS:")
    print(f"{'-'*70}\n")

    co_concepts = identify_co_occurring_concepts(concept_name, appearances, 10)
    for concept, count in co_concepts:
        print(f"  • {concept}: {count} times")

    # Detect relationships
    print(f"\n{'-'*70}")
    print("CONCEPT RELATIONSHIPS:")
    print(f"{'-'*70}\n")

    relationships = detect_concept_relationships(concept_name, appearances)
    if relationships:
        for rel in relationships:
            print(f"[{rel['type'].upper()}] {rel['pattern']}")
            for example in rel['examples']:
                print(f"  • {example}")
            print()
    else:
        print("No explicit relationships detected.")

    # Identify domains
    print(f"{'-'*70}")
    print("DOMAIN DISTRIBUTION:")
    print(f"{'-'*70}\n")

    topics_index = index.get('topics', {})
    domain_counts = defaultdict(int)

    for app in appearances:
        for topic_id in app['topics']:
            topic_info = topics_index.get(topic_id, {})
            domain = topic_info.get('domain', 'unknown')
            domain_counts[domain] += app['count']

    for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {domain.replace('_', ' ').title()}: {count} occurrences")

    print(f"\n{'='*70}\n")

    return {
        'concept': concept_name,
        'total_occurrences': total_occurrences,
        'sources': total_sources,
        'appearances': appearances,
        'co_occurring': co_concepts,
        'relationships': relationships,
        'domains': dict(domain_counts),
        'timestamp': datetime.now().isoformat()
    }

def compare_concepts(concept1, concept2):
    """Compare how two concepts appear in the knowledge base."""
    print(f"\n{'='*70}")
    print(f"COMPARING: {concept1.upper()} vs {concept2.upper()}")
    print(f"{'='*70}\n")

    index = load_knowledge_index()

    # Track both concepts
    app1 = analyze_concept_evolution(concept1, index)
    app2 = analyze_concept_evolution(concept2, index)

    count1 = sum(app['count'] for app in app1)
    count2 = sum(app['count'] for app in app2)

    # Find shared sources
    sources1 = set(app['source_id'] for app in app1)
    sources2 = set(app['source_id'] for app in app2)
    shared = sources1 & sources2

    print(f"{concept1}: {count1:,} occurrences in {len(sources1)} sources")
    print(f"{concept2}: {count2:,} occurrences in {len(sources2)} sources")
    print(f"Shared sources: {len(shared)}")

    if shared:
        print(f"\nSources discussing both concepts:")
        for source_id in shared:
            # Find in original data
            for app in app1:
                if app['source_id'] == source_id:
                    print(f"  • {app['title']}")
                    break

    print(f"\n{'='*70}\n")

def main():
    """Main execution."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  Track concept:   python3 concept_tracker.py <concept>")
        print("  Compare:         python3 concept_tracker.py <concept1> vs <concept2>")
        print("\nExamples:")
        print("  python3 concept_tracker.py emergence")
        print("  python3 concept_tracker.py consciousness vs information")
        return

    if 'vs' in sys.argv:
        idx = sys.argv.index('vs')
        concept1 = " ".join(sys.argv[1:idx])
        concept2 = " ".join(sys.argv[idx+1:])
        compare_concepts(concept1, concept2)
    else:
        concept = " ".join(sys.argv[1:])
        result = track_concept(concept)

        if result:
            # Save result
            output_file = BASE_DIR / f"concept_track_{concept.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to: {output_file}\n")

if __name__ == "__main__":
    main()
