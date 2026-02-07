#!/usr/bin/env python3
"""
Domain Explorer - Ventures into entirely new knowledge domains

Instead of expanding existing topics, this tool explores adjacent
and orthogonal fields to diversify the knowledge base.

Strategy:
1. Analyzes current domain focus
2. Identifies adjacent domains (related but different)
3. Identifies orthogonal domains (different perspectives)
4. Suggests topics that broaden knowledge diversity
"""

import json
from pathlib import Path
from datetime import datetime
import subprocess

KNOWLEDGE_DIR = Path("/home/dev/mnt/knowledge")
INDEX_FILE = KNOWLEDGE_DIR / "index.json"

# Domain taxonomy - maps domains to related and orthogonal fields
DOMAIN_MAP = {
    "computer_science": {
        "adjacent": ["mathematics", "cognitive_science", "information_theory", "systems_theory"],
        "orthogonal": ["biology", "physics", "philosophy", "social_science"],
        "topics": ["artificial_life", "self_improving_systems", "emergent_behavior",
                   "complex_systems", "computational_theory"]
    },
    "biology": {
        "adjacent": ["chemistry", "medicine", "ecology", "evolution"],
        "orthogonal": ["computer_science", "physics", "mathematics"],
        "topics": ["cellular_automata", "neural_networks", "genetic_algorithms",
                   "evolutionary_computation", "biomimicry"]
    },
    "physics": {
        "adjacent": ["mathematics", "cosmology", "quantum_mechanics"],
        "orthogonal": ["biology", "computer_science", "philosophy"],
        "topics": ["thermodynamics", "information_physics", "complexity_theory",
                   "phase_transitions", "self_organization"]
    },
    "mathematics": {
        "adjacent": ["logic", "computer_science", "physics"],
        "orthogonal": ["biology", "social_science", "philosophy"],
        "topics": ["chaos_theory", "graph_theory", "cellular_automata",
                   "recursive_functions", "computational_complexity"]
    },
    "cognitive_science": {
        "adjacent": ["neuroscience", "psychology", "philosophy", "linguistics"],
        "orthogonal": ["physics", "mathematics", "computer_science"],
        "topics": ["consciousness", "learning_theory", "memory_systems",
                   "metacognition", "cognitive_architecture"]
    },
    "philosophy": {
        "adjacent": ["logic", "ethics", "epistemology", "metaphysics"],
        "orthogonal": ["computer_science", "biology", "physics"],
        "topics": ["philosophy_of_mind", "teleology", "emergence_philosophy",
                   "free_will", "artificial_consciousness"]
    }
}

# Exploration strategies for different domains
EXPLORATION_URLS = {
    "cellular_automata": "https://en.wikipedia.org/wiki/Cellular_automaton",
    "neural_networks": "https://en.wikipedia.org/wiki/Artificial_neural_network",
    "genetic_algorithms": "https://en.wikipedia.org/wiki/Genetic_algorithm",
    "chaos_theory": "https://en.wikipedia.org/wiki/Chaos_theory",
    "thermodynamics": "https://en.wikipedia.org/wiki/Thermodynamics",
    "information_theory": "https://en.wikipedia.org/wiki/Information_theory",
    "consciousness": "https://en.wikipedia.org/wiki/Consciousness",
    "philosophy_of_mind": "https://en.wikipedia.org/wiki/Philosophy_of_mind",
    "evolutionary_computation": "https://en.wikipedia.org/wiki/Evolutionary_computation",
    "cognitive_architecture": "https://en.wikipedia.org/wiki/Cognitive_architecture",
    "graph_theory": "https://en.wikipedia.org/wiki/Graph_theory",
    "phase_transitions": "https://en.wikipedia.org/wiki/Phase_transition",
    "metacognition": "https://en.wikipedia.org/wiki/Metacognition",
    "systems_theory": "https://en.wikipedia.org/wiki/Systems_theory",
    "cybernetics": "https://en.wikipedia.org/wiki/Cybernetics",
    "autopoiesis": "https://en.wikipedia.org/wiki/Autopoiesis"
}

def load_index():
    """Load the knowledge index"""
    if not INDEX_FILE.exists():
        return {"topics": {}, "sources": {}}
    with open(INDEX_FILE) as f:
        return json.load(f)

def classify_current_domain(index):
    """Determine which domain(s) current knowledge belongs to"""
    topics = list(index['topics'].keys())

    # Map current topics to domains
    current_domains = set()

    # Check each domain's topics
    for domain, info in DOMAIN_MAP.items():
        for topic in topics:
            # Simple matching - check if topic name relates to domain topics
            topic_lower = topic.lower().replace(' ', '_')
            if any(domain_topic in topic_lower or topic_lower in domain_topic
                   for domain_topic in info['topics']):
                current_domains.add(domain)

    # Default to computer science if unclear
    if not current_domains:
        current_domains.add("computer_science")

    return current_domains

def suggest_adjacent_domains(current_domains):
    """Suggest domains adjacent to current focus"""
    adjacent = set()
    for domain in current_domains:
        if domain in DOMAIN_MAP:
            adjacent.update(DOMAIN_MAP[domain]['adjacent'])
    return list(adjacent)

def suggest_orthogonal_domains(current_domains):
    """Suggest domains orthogonal to current focus (different perspective)"""
    orthogonal = set()
    for domain in current_domains:
        if domain in DOMAIN_MAP:
            orthogonal.update(DOMAIN_MAP[domain]['orthogonal'])
    return list(orthogonal)

def suggest_exploration_topics(domains, max_suggestions=5):
    """Suggest specific topics to explore in given domains"""
    suggestions = []

    for domain in domains:
        if domain in DOMAIN_MAP:
            for topic in DOMAIN_MAP[domain]['topics'][:3]:  # Top 3 from each
                if topic in EXPLORATION_URLS:
                    suggestions.append({
                        'topic': topic.replace('_', ' ').title(),
                        'domain': domain,
                        'url': EXPLORATION_URLS[topic]
                    })

    return suggestions[:max_suggestions]

def explore_new_domain(topic_name, url):
    """Create a new topic and fetch initial source"""
    index = load_index()

    # Check if topic already exists by name (not just ID)
    existing_topic_id = None
    for tid, tdata in index['topics'].items():
        if tdata['name'].lower() == topic_name.lower():
            print(f"✓ Topic '{topic_name}' already exists as {tid}")
            existing_topic_id = tid
            break

    # Create topic if it doesn't exist
    if not existing_topic_id:
        print(f"Creating new topic: {topic_name}")

        # Use explorer to create topic with correct command
        try:
            # Create topic using 'add-topic' command
            result = subprocess.run(
                ['python3', '/home/dev/mnt/explorer.py', 'add-topic', topic_name,
                 f"Auto-discovered domain: {topic_name}"],
                capture_output=True, text=True, check=True
            )
            print(f"✓ {result.stdout.strip()}")

            # Reload index to get the new topic ID
            index = load_index()
            for tid, tdata in index['topics'].items():
                if tdata['name'].lower() == topic_name.lower():
                    existing_topic_id = tid
                    break

            if not existing_topic_id:
                print(f"✗ Failed to create topic '{topic_name}'")
                return False

        except subprocess.CalledProcessError as e:
            print(f"✗ Error creating topic: {e.stderr}")
            return False

    # Check if URL already exists
    existing_urls = {src['url'] for src in index['sources'].values() if 'url' in src}
    if url in existing_urls:
        print(f"⏭ URL already exists in knowledge base: {url}")
        return True  # Topic exists, URL exists - consider this success

    # Add source using correct command 'fetch'
    print(f"Fetching source from: {url}")
    try:
        result = subprocess.run(
            ['python3', '/home/dev/mnt/explorer.py', 'fetch', existing_topic_id, url],
            capture_output=True, text=True, check=True
        )
        print(f"✓ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error fetching source: {e.stderr}")
        return False

def analyze_and_suggest():
    """Main analysis function"""
    print("=== DOMAIN EXPLORATION ANALYSIS ===\n")

    index = load_index()
    current_domains = classify_current_domain(index)

    print(f"📊 Current Domain Focus: {', '.join(current_domains)}")
    print()

    print("🔗 Adjacent Domains (Related Fields):")
    adjacent = suggest_adjacent_domains(current_domains)
    for i, domain in enumerate(adjacent[:5], 1):
        print(f"  {i}. {domain.replace('_', ' ').title()}")
    print()

    print("🔀 Orthogonal Domains (Different Perspectives):")
    orthogonal = suggest_orthogonal_domains(current_domains)
    for i, domain in enumerate(orthogonal[:5], 1):
        print(f"  {i}. {domain.replace('_', ' ').title()}")
    print()

    print("💡 Suggested Exploration Topics:")
    print("\n📍 From Adjacent Domains (expand current knowledge):")
    adjacent_topics = suggest_exploration_topics(adjacent, 3)
    for i, suggestion in enumerate(adjacent_topics, 1):
        print(f"  {i}. {suggestion['topic']} ({suggestion['domain'].replace('_', ' ')})")
        print(f"     URL: {suggestion['url']}")

    print("\n🎯 From Orthogonal Domains (diversify perspective):")
    orthogonal_topics = suggest_exploration_topics(orthogonal, 3)
    for i, suggestion in enumerate(orthogonal_topics, 1):
        print(f"  {i}. {suggestion['topic']} ({suggestion['domain'].replace('_', ' ')})")
        print(f"     URL: {suggestion['url']}")

    print("\n" + "="*50)

    return {
        'adjacent': adjacent_topics,
        'orthogonal': orthogonal_topics
    }

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "explore":
        if len(sys.argv) < 4:
            print("Usage: domain_explorer.py explore <topic_name> <url>")
            sys.exit(1)
        topic = sys.argv[2]
        url = sys.argv[3]
        explore_new_domain(topic, url)
    elif len(sys.argv) > 1 and sys.argv[1] == "auto":
        # Auto-explore: pick one topic from suggestions and explore it
        suggestions = analyze_and_suggest()
        print("\n🤖 AUTO-EXPLORE MODE")

        # Pick first suggestion from adjacent domains (safer expansion)
        if suggestions['adjacent']:
            choice = suggestions['adjacent'][0]
            print(f"\nExploring: {choice['topic']} from {choice['domain']}")
            explore_new_domain(choice['topic'], choice['url'])
        else:
            print("No suggestions available")
    else:
        analyze_and_suggest()
