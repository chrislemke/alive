#!/usr/bin/env python3
"""
Cross-Domain Synthesizer
Generates insights by combining knowledge from different domains.
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent
INDEX_FILE = BASE_DIR / "knowledge" / "index.json"

def load_index():
    """Load knowledge index."""
    if not INDEX_FILE.exists():
        return {"topics": {}, "domains": {}}
    with open(INDEX_FILE) as f:
        return json.load(f)

def extract_keywords(text, min_length=5):
    """Extract significant keywords from text, filtering out HTML and common words."""
    import re

    # Extract only words (5+ chars to reduce noise)
    words = re.findall(r'\b[a-z]{' + str(min_length) + r',}\b', text.lower())

    # Comprehensive stopwords
    stopwords = {'that', 'this', 'with', 'from', 'have', 'they', 'been',
                 'their', 'which', 'what', 'will', 'when', 'more', 'such',
                 'other', 'these', 'than', 'into', 'about', 'through',
                 'also', 'only', 'some', 'would', 'could', 'should', 'there',
                 'were', 'each', 'most', 'many', 'then', 'them', 'both',
                 'being', 'where', 'those', 'while', 'since', 'after',
                 'before', 'during', 'without', 'within', 'between',
                 'among', 'under', 'above', 'below', 'first', 'second',
                 'third', 'example', 'examples', 'often', 'however',
                 'therefore', 'although', 'unless', 'until', 'because',
                 'whether', 'though', 'might', 'still', 'thus', 'rather',
                 'quite', 'even', 'ever', 'much', 'another', 'every',
                 'several', 'various', 'different', 'similar', 'certain'}

    # HTML, Wikipedia markup, and technical noise
    html_terms = {'href', 'span', 'class', 'cite', 'wiki', 'http', 'https',
                  'abbr', 'link', 'style', 'title', 'xmlns', 'vector',
                  'data', 'text', 'edit', 'view', 'page', 'wikipedia',
                  'retrieved', 'archived', 'original', 'article', 'section',
                  'button', 'bracket', 'identifier', 'info', 'list', 'parser',
                  'output', 'reference', 'external', 'nofollow', 'width',
                  'height', 'image', 'thumb', 'caption', 'margin', 'padding',
                  'border', 'content', 'header', 'footer', 'script', 'meta',
                  'property', 'value', 'function', 'window', 'document',
                  'element', 'namespace', 'module', 'config', 'client',
                  'server', 'media', 'query', 'string', 'object', 'array',
                  'method', 'parameter', 'return', 'false', 'version',
                  'language', 'format', 'typeof', 'length', 'index', 'label',
                  'description', 'container', 'wrapper', 'loader', 'entity',
                  'status', 'error', 'warning', 'notice', 'message', 'alert',
                  'default', 'custom', 'option', 'enabled', 'disabled',
                  'hidden', 'visible', 'display', 'position', 'absolute',
                  'relative', 'fixed', 'static', 'inherit', 'initial',
                  'template', 'model', 'controller', 'action', 'render',
                  'response', 'request', 'session', 'cookie', 'token',
                  'wikibase', 'wikitext', 'mediawiki', 'rlconf', 'rlstate',
                  'rlpagemodules', 'jquery', 'bootstrap', 'vector', 'gadget',
                  'javascript', 'charset', 'encoding', 'stylesheet', 'alternate',
                  'redirect', 'navbox', 'inline', 'templatestyles', 'wikimedia',
                  'special', 'deduplicated', 'interlanguage', 'aboutsite',
                  'abovebelow', 'aancia', 'aaron', 'abbaszadeh', 'ability',
                  'noreferrer', 'noopener', 'upload', 'commons', 'foundation'}

    # Filter: not in stopwords, not in html_terms, and not all vowels/consonants
    result = []
    for w in words:
        if w in stopwords or w in html_terms:
            continue
        # Skip if too many repeated chars (like "aaaa", typical of noise)
        if len(set(w)) < len(w) / 3:
            continue
        result.append(w)

    return result

def load_source_content(source_id):
    """Load content from a source file."""
    # Try multiple possible locations
    possible_paths = [
        BASE_DIR / "knowledge" / "sources" / f"{source_id}.txt",
        BASE_DIR / "knowledge" / f"source_{source_id}.txt",
        BASE_DIR / "sources" / f"{source_id}.txt",
    ]

    for path in possible_paths:
        if path.exists():
            with open(path) as f:
                return f.read()

    return ""

def analyze_domain_connections(index):
    """Analyze connections between different domains."""
    domain_topics = defaultdict(list)

    # Group topics by domain
    for topic_id, topic_data in index["topics"].items():
        domain = topic_data.get("domain", "computer_science")  # default domain
        domain_topics[domain].append(topic_id)

    connections = []

    # Get all domains
    domains = list(domain_topics.keys())

    # Find cross-domain topic connections
    for domain1 in domains:
        for domain2 in domains:
            if domain1 >= domain2:  # Avoid duplicates
                continue

            # Get topics from each domain
            topics1 = domain_topics.get(domain1, [])
            topics2 = domain_topics.get(domain2, [])

            # Check for connections between topics
            for t1_id in topics1:
                for t2_id in topics2:
                    t1_data = index["topics"][t1_id]
                    t2_data = index["topics"][t2_id]

                    # Extract keywords from both
                    keywords1 = set()
                    keywords2 = set()

                    for source_id in t1_data.get("sources", []):
                        content = load_source_content(source_id)
                        keywords1.update(extract_keywords(content))

                    for source_id in t2_data.get("sources", []):
                        content = load_source_content(source_id)
                        keywords2.update(extract_keywords(content))

                    # Find overlap
                    shared = keywords1 & keywords2
                    if len(shared) >= 3:
                        connections.append({
                            "domain1": domain1,
                            "domain2": domain2,
                            "topic1": t1_data.get("name", t1_id),
                            "topic2": t2_data.get("name", t2_id),
                            "shared_concepts": sorted(list(shared))[:10],
                            "strength": len(shared)
                        })

    return sorted(connections, key=lambda x: x["strength"], reverse=True)

def generate_synthesis_questions(connections):
    """Generate research questions from cross-domain connections."""
    questions = []

    for conn in connections[:5]:  # Top 5 connections
        t1 = conn["topic1"]
        t2 = conn["topic2"]
        d1 = conn["domain1"]
        d2 = conn["domain2"]
        concepts = conn["shared_concepts"][:3]

        # Generate different types of questions
        questions.append({
            "type": "bridge",
            "question": f"How do concepts from {t1} ({d1}) relate to {t2} ({d2})?",
            "focus": concepts
        })

        questions.append({
            "type": "application",
            "question": f"Can techniques from {t1} be applied to solve problems in {t2}?",
            "focus": concepts
        })

        questions.append({
            "type": "synthesis",
            "question": f"What new insights emerge from combining {t1} and {t2}?",
            "focus": concepts
        })

    return questions

def find_bridging_concepts(index):
    """Find concepts that appear across multiple domains."""
    domain_keywords = defaultdict(lambda: defaultdict(int))

    for topic_id, topic_data in index["topics"].items():
        domain = topic_data.get("domain", "computer_science")

        for source_id in topic_data.get("sources", []):
            content = load_source_content(source_id)
            keywords = extract_keywords(content)

            for kw in keywords:
                domain_keywords[kw][domain] += 1

    # Find keywords appearing in multiple domains
    bridging = []
    for keyword, domains in domain_keywords.items():
        if len(domains) >= 2:
            bridging.append({
                "concept": keyword,
                "domains": list(domains.keys()),
                "frequency": sum(domains.values()),
                "domain_count": len(domains)
            })

    return sorted(bridging, key=lambda x: (x["domain_count"], x["frequency"]), reverse=True)

def generate_hypotheses(connections, bridging_concepts):
    """Generate hypotheses from cross-domain patterns."""
    hypotheses = []

    # Type 1: From strong connections
    for conn in connections[:3]:
        hypothesis = {
            "type": "connection",
            "statement": f"{conn['topic1']} and {conn['topic2']} may share fundamental principles related to {', '.join(conn['shared_concepts'][:2])}",
            "domains": [conn["domain1"], conn["domain2"]],
            "confidence": "moderate" if conn["strength"] >= 5 else "low"
        }
        hypotheses.append(hypothesis)

    # Type 2: From bridging concepts
    for bc in bridging_concepts[:3]:
        if bc["domain_count"] >= 3:
            hypothesis = {
                "type": "universal",
                "statement": f"The concept '{bc['concept']}' appears to be a universal principle spanning {bc['domain_count']} domains",
                "domains": bc["domains"],
                "confidence": "high" if bc["frequency"] >= 10 else "moderate"
            }
            hypotheses.append(hypothesis)

    return hypotheses

def report():
    """Generate a comprehensive cross-domain synthesis report."""
    index = load_index()

    print("=" * 70)
    print("CROSS-DOMAIN SYNTHESIS REPORT")
    print("=" * 70)
    print(f"\nGenerated: {datetime.now().isoformat()}\n")

    # Derive domains from topics
    domains_dict = defaultdict(list)
    for topic_id, topic_data in index["topics"].items():
        domain = topic_data.get("domain", "computer_science")
        domains_dict[domain].append(topic_data.get("name", topic_id))

    print(f"Analyzing {len(domains_dict)} knowledge domains:")
    for domain, topics in domains_dict.items():
        print(f"  • {domain}: {len(topics)} topics ({', '.join(topics)})")

    print("\n" + "=" * 70)
    print("CROSS-DOMAIN CONNECTIONS")
    print("=" * 70)

    connections = analyze_domain_connections(index)

    if not connections:
        print("\nNo significant cross-domain connections found yet.")
        print("Need more sources in multiple domains.")
    else:
        print(f"\nFound {len(connections)} connections between domains:\n")

        for i, conn in enumerate(connections[:5], 1):
            print(f"{i}. [{conn['domain1']}] {conn['topic1']} ↔ [{conn['domain2']}] {conn['topic2']}")
            print(f"   Strength: {conn['strength']} shared concepts")
            print(f"   Key concepts: {', '.join(conn['shared_concepts'][:5])}")
            print()

    print("=" * 70)
    print("BRIDGING CONCEPTS")
    print("=" * 70)

    bridging = find_bridging_concepts(index)

    if bridging:
        print(f"\nConcepts appearing across multiple domains:\n")
        for i, bc in enumerate(bridging[:10], 1):
            print(f"{i}. '{bc['concept']}' - appears in {bc['domain_count']} domains")
            print(f"   Domains: {', '.join(bc['domains'])}")
            print(f"   Total occurrences: {bc['frequency']}")
            print()
    else:
        print("\nNo bridging concepts found yet.")

    print("=" * 70)
    print("SYNTHESIS QUESTIONS")
    print("=" * 70)

    if connections:
        questions = generate_synthesis_questions(connections)
        print(f"\nGenerated {len(questions)} research questions:\n")

        for i, q in enumerate(questions[:10], 1):
            print(f"{i}. [{q['type'].upper()}] {q['question']}")
            print(f"   Focus concepts: {', '.join(q['focus'])}")
            print()

    print("=" * 70)
    print("HYPOTHESES")
    print("=" * 70)

    hypotheses = []
    if connections or bridging:
        hypotheses = generate_hypotheses(connections, bridging)
        print(f"\nGenerated {len(hypotheses)} hypotheses:\n")

        for i, h in enumerate(hypotheses, 1):
            print(f"{i}. [{h['type'].upper()}] {h['statement']}")
            print(f"   Confidence: {h['confidence']}")
            print(f"   Domains: {', '.join(h['domains'])}")
            print()

    print("=" * 70)

    return {
        "connections": connections,
        "bridging_concepts": bridging,
        "hypotheses": hypotheses
    }

def analyze_connection(topic1, topic2):
    """Deep analysis of connection between two specific topics."""
    index = load_index()

    # Try to find topics by name or ID
    t1_id = None
    t2_id = None

    for topic_id, topic_data in index["topics"].items():
        if topic_id == topic1 or topic_data.get("name", "") == topic1:
            t1_id = topic_id
        if topic_id == topic2 or topic_data.get("name", "") == topic2:
            t2_id = topic_id

    if not t1_id or not t2_id:
        print(f"Error: One or both topics not found")
        print(f"Available topics: {', '.join([d.get('name', i) for i, d in index['topics'].items()])}")
        return

    t1_data = index["topics"][t1_id]
    t2_data = index["topics"][t2_id]

    t1_name = t1_data.get("name", t1_id)
    t2_name = t2_data.get("name", t2_id)

    print("=" * 70)
    print(f"DEEP ANALYSIS: {t1_name} ↔ {t2_name}")
    print("=" * 70)

    print(f"\n{t1_name}:")
    print(f"  Domain: {t1_data.get('domain', 'computer_science')}")
    print(f"  Description: {t1_data.get('description', 'N/A')}")
    print(f"  Sources: {len(t1_data.get('sources', []))}")

    print(f"\n{t2_name}:")
    print(f"  Domain: {t2_data.get('domain', 'computer_science')}")
    print(f"  Description: {t2_data.get('description', 'N/A')}")
    print(f"  Sources: {len(t2_data.get('sources', []))}")

    # Extract all keywords
    keywords1 = set()
    keywords2 = set()

    for source in t1_data.get("sources", []):
        content = load_source_content(source)
        keywords1.update(extract_keywords(content))

    for source in t2_data.get("sources", []):
        content = load_source_content(source)
        keywords2.update(extract_keywords(content))

    shared = keywords1 & keywords2
    unique1 = keywords1 - keywords2
    unique2 = keywords2 - keywords1

    print(f"\nShared concepts ({len(shared)}):")
    for kw in sorted(list(shared))[:20]:
        print(f"  • {kw}")

    print(f"\nUnique to {t1_name} ({len(unique1)}):")
    for kw in sorted(list(unique1))[:10]:
        print(f"  • {kw}")

    print(f"\nUnique to {t2_name} ({len(unique2)}):")
    for kw in sorted(list(unique2))[:10]:
        print(f"  • {kw}")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "report":
            report()
        elif cmd == "analyze" and len(sys.argv) == 4:
            analyze_connection(sys.argv[2], sys.argv[3])
        else:
            print("Usage:")
            print("  python3 cross_synthesizer.py report")
            print("  python3 cross_synthesizer.py analyze <topic1> <topic2>")
    else:
        report()
