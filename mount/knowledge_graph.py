#!/usr/bin/env python3
"""
Knowledge Graph Visualizer
Generates visual representations of topic connections and relationships.
Shows relationship strengths, clusters, and identifies gaps in knowledge.
"""

import json
import os
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

def load_knowledge_index():
    """Load the knowledge index."""
    index_path = KNOWLEDGE_DIR / "index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            return json.load(f)
    return {"topics": {}}

def load_topic_sources(topic_data, source_ids, all_sources):
    """Load all sources for a topic."""
    sources = []
    for source_id in source_ids:
        # Load the actual source content
        source_file = KNOWLEDGE_DIR / f"source_{source_id}.txt"
        if source_file.exists():
            with open(source_file, 'r') as f:
                content = f.read()
                # Get metadata from index
                metadata = all_sources.get(source_id, {})
                sources.append({
                    'id': source_id,
                    'content': content,
                    'title': metadata.get('title', ''),
                    'url': metadata.get('url', '')
                })
    return sources

def extract_concepts(text):
    """Extract key concepts from text (simple word frequency approach)."""
    # Remove common words
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
                 'these', 'those', 'it', 'its', 'their', 'there', 'they'}

    words = text.lower().split()
    concepts = [w.strip('.,!?;:()[]{}"\'-') for w in words if len(w) > 3]
    concepts = [c for c in concepts if c not in stopwords and c.isalpha()]

    return Counter(concepts)

def calculate_topic_similarity(topic1_sources, topic2_sources):
    """Calculate similarity between two topics based on shared concepts."""
    # Combine all text from topic 1
    text1 = " ".join([s.get('content', '') for s in topic1_sources])
    # Combine all text from topic 2
    text2 = " ".join([s.get('content', '') for s in topic2_sources])

    concepts1 = extract_concepts(text1)
    concepts2 = extract_concepts(text2)

    # Calculate intersection
    common = set(concepts1.keys()) & set(concepts2.keys())

    if not common:
        return 0, set()

    # Weight by frequency
    similarity = sum(min(concepts1[c], concepts2[c]) for c in common)

    return similarity, common

def build_knowledge_graph():
    """Build a graph of all topics and their connections."""
    index = load_knowledge_index()
    topics = index.get("topics", {})
    all_sources = index.get("sources", {})

    # Load all topic data
    topic_data = {}
    for topic_slug, topic_info in topics.items():
        source_ids = topic_info.get('sources', [])
        sources = load_topic_sources(topic_info, source_ids, all_sources)
        topic_data[topic_slug] = {
            'name': topic_info.get('name', topic_slug),
            'domain': topic_info.get('domain', 'unknown'),
            'sources': sources,
            'source_count': len(sources)
        }

    # Calculate all pairwise connections
    connections = []
    topic_list = list(topic_data.keys())

    for i, topic1 in enumerate(topic_list):
        for topic2 in topic_list[i+1:]:
            similarity, common_concepts = calculate_topic_similarity(
                topic_data[topic1]['sources'],
                topic_data[topic2]['sources']
            )

            if similarity > 0:
                connections.append({
                    'topic1': topic1,
                    'topic2': topic2,
                    'strength': similarity,
                    'common_concepts': len(common_concepts),
                    'top_concepts': list(sorted(common_concepts)[:5])
                })

    # Sort by strength
    connections.sort(key=lambda x: x['strength'], reverse=True)

    return topic_data, connections

def visualize_ascii_graph(topic_data, connections):
    """Generate ASCII art visualization of the knowledge graph."""
    output = []
    output.append("=" * 70)
    output.append("KNOWLEDGE GRAPH VISUALIZATION")
    output.append("=" * 70)
    output.append("")

    # Group topics by domain
    domains = defaultdict(list)
    for topic_slug, data in topic_data.items():
        domains[data['domain']].append((topic_slug, data))

    # Display domains and topics
    output.append("TOPICS BY DOMAIN:")
    output.append("-" * 70)
    for domain, topics in sorted(domains.items()):
        output.append(f"\n[{domain.upper().replace('_', ' ')}]")
        for topic_slug, data in topics:
            output.append(f"  • {data['name']} ({data['source_count']} sources)")

    output.append("\n" + "=" * 70)
    output.append("CONNECTIONS (Strength: shared concept frequency)")
    output.append("=" * 70)

    # Display top connections
    if connections:
        for i, conn in enumerate(connections[:10], 1):
            topic1_name = topic_data[conn['topic1']]['name']
            topic2_name = topic_data[conn['topic2']]['name']
            strength = conn['strength']
            concepts = conn['common_concepts']

            # Create visual strength indicator
            bar_length = min(40, strength // 50)
            bar = "█" * bar_length

            output.append(f"\n{i}. {topic1_name} ↔ {topic2_name}")
            output.append(f"   Strength: {strength:,} | Concepts: {concepts}")
            output.append(f"   {bar}")
            output.append(f"   Top shared: {', '.join(conn['top_concepts'][:3])}")
    else:
        output.append("\nNo connections found yet.")

    output.append("\n" + "=" * 70)
    output.append("GRAPH STATISTICS")
    output.append("=" * 70)
    output.append(f"Total Topics: {len(topic_data)}")
    output.append(f"Total Domains: {len(domains)}")
    output.append(f"Total Connections: {len(connections)}")

    if connections:
        avg_strength = sum(c['strength'] for c in connections) / len(connections)
        output.append(f"Average Connection Strength: {avg_strength:.1f}")
        output.append(f"Strongest Connection: {connections[0]['strength']:,}")
        output.append(f"Weakest Connection: {connections[-1]['strength']:,}")

    # Identify most connected topics
    connection_counts = defaultdict(int)
    for conn in connections:
        connection_counts[conn['topic1']] += 1
        connection_counts[conn['topic2']] += 1

    if connection_counts:
        output.append("\nMost Connected Topics:")
        for topic_slug, count in sorted(connection_counts.items(),
                                       key=lambda x: x[1], reverse=True)[:5]:
            output.append(f"  • {topic_data[topic_slug]['name']}: {count} connections")

    # Identify isolated topics
    all_topics = set(topic_data.keys())
    connected_topics = set()
    for conn in connections:
        connected_topics.add(conn['topic1'])
        connected_topics.add(conn['topic2'])

    isolated = all_topics - connected_topics
    if isolated:
        output.append("\nIsolated Topics (no strong connections):")
        for topic_slug in isolated:
            output.append(f"  • {topic_data[topic_slug]['name']}")

    output.append("\n" + "=" * 70)

    return "\n".join(output)

def generate_graphviz_dot(topic_data, connections):
    """Generate Graphviz DOT format for external visualization."""
    lines = []
    lines.append("graph KnowledgeGraph {")
    lines.append("  layout=fdp;")
    lines.append("  overlap=false;")
    lines.append("  splines=true;")
    lines.append("")

    # Define nodes with domain-based coloring
    domain_colors = {
        'computer_science': '#4A90E2',
        'cognitive_science': '#E24A4A',
        'mathematics': '#50C878',
        'biology': '#F5A623',
        'unknown': '#999999'
    }

    for topic_slug, data in topic_data.items():
        color = domain_colors.get(data['domain'], '#999999')
        label = data['name'].replace(' ', '\\n')
        lines.append(f'  "{topic_slug}" [label="{label}", '
                    f'fillcolor="{color}", style=filled, fontcolor=white];')

    lines.append("")

    # Define edges with weights
    for conn in connections:
        weight = max(1, min(10, conn['strength'] // 100))  # Scale for visibility
        lines.append(f'  "{conn["topic1"]}" -- "{conn["topic2"]}" '
                    f'[weight={weight}, penwidth={weight/2}];')

    lines.append("}")

    return "\n".join(lines)

def main():
    """Main execution."""
    import sys

    print("Building knowledge graph...")
    topic_data, connections = build_knowledge_graph()

    if len(sys.argv) > 1 and sys.argv[1] == 'dot':
        # Generate Graphviz DOT format
        dot = generate_graphviz_dot(topic_data, connections)
        dot_path = BASE_DIR / "knowledge_graph.dot"
        with open(dot_path, 'w') as f:
            f.write(dot)
        print(f"\nGraphviz DOT file saved to: {dot_path}")
        print("Generate visualization with: dot -Tpng knowledge_graph.dot -o graph.png")
    else:
        # Generate ASCII visualization
        viz = visualize_ascii_graph(topic_data, connections)
        print(viz)

        # Save to file
        output_path = BASE_DIR / f"knowledge_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_path, 'w') as f:
            f.write(viz)
        print(f"\nVisualization saved to: {output_path}")

if __name__ == "__main__":
    main()
