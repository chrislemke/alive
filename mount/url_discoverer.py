#!/usr/bin/env python3
"""
URL Discoverer - Extract Wikipedia links from existing sources for unbounded exploration

This tool transforms the system from bounded to unbounded autonomy by:
1. Parsing existing source content for Wikipedia URLs
2. Filtering for quality and relevance
3. Suggesting new URLs for exploration
4. Enabling self-sustaining knowledge growth

Design principles:
- Extract only Wikipedia URLs (trusted, structured source)
- Avoid already-fetched URLs (check against index)
- Score by relevance (proximity to key terms)
- Prioritize cross-domain connections
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from urllib.parse import urlparse, unquote

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
INDEX_FILE = KNOWLEDGE_DIR / "index.json"

def load_index():
    """Load knowledge index"""
    if not INDEX_FILE.exists():
        return {"topics": {}, "sources": {}, "notes": {}}
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

def get_existing_urls(index):
    """Get set of all URLs already in the knowledge base"""
    urls = set()
    for source_id, source in index.get("sources", {}).items():
        if "url" in source:
            urls.add(source["url"])
    return urls

def extract_wikipedia_urls(content):
    """Extract Wikipedia URLs from HTML/markdown content"""
    # Pattern for Wikipedia URLs
    patterns = [
        r'href="(https?://en\.wikipedia\.org/wiki/[^"]+)"',
        r'href="(/wiki/[^"]+)"',
        r'\[.*?\]\((https?://en\.wikipedia\.org/wiki/[^)]+)\)',
    ]

    urls = set()
    for pattern in patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            # Normalize URL
            if match.startswith('/wiki/'):
                url = f"https://en.wikipedia.org{match}"
            else:
                url = match

            # Clean URL (remove fragments, query params for now)
            url = url.split('#')[0]
            url = url.split('?')[0]

            # Filter out special pages and metadata
            path = urlparse(url).path
            if any(skip in path.lower() for skip in [
                'file:', 'special:', 'help:', 'category:',
                'talk:', 'user:', 'wikipedia:', 'template:',
                'portal:', 'book:', 'main_page', '(identifier)',
                'wikimedia', 'mediawiki', 'meta:', 'project:'
            ]):
                continue

            # Must be actual article path
            if not path.startswith('/wiki/') or path.count('/') > 2:
                continue

            urls.add(url)

    return urls

def score_url_relevance(url, key_terms=None):
    """Score URL by relevance to key terms"""
    if key_terms is None:
        key_terms = [
            'emergence', 'consciousness', 'information', 'system',
            'theory', 'complexity', 'self', 'evolution', 'neural',
            'quantum', 'cognitive', 'intelligence', 'chaos', 'fractal',
            'autopoiesis', 'entropy', 'organization', 'life'
        ]

    # Extract title from URL
    path = urlparse(url).path
    title = path.split('/wiki/')[-1] if '/wiki/' in path else path
    title = unquote(title).lower().replace('_', ' ')

    # Count key term matches
    score = 0
    for term in key_terms:
        if term.lower() in title:
            score += 10  # High weight for title match

    # Bonus for compound terms
    if any(char.isupper() for char in unquote(path.split('/wiki/')[-1])):
        score += 2  # CamelCase suggests technical topic

    return score

def discover_urls(max_suggestions=50):
    """Discover new URLs from existing sources"""
    print("Discovering URLs from existing knowledge base...")
    print("=" * 70)

    index = load_index()
    existing_urls = get_existing_urls(index)

    print(f"Existing sources: {len(existing_urls)}")

    # Collect all URLs from all sources
    discovered_urls = set()
    url_sources = defaultdict(list)  # Track which sources mention each URL

    for source_id, source in index.get("sources", {}).items():
        # Read content from source file
        source_file = KNOWLEDGE_DIR / f"source_{source_id}.txt"
        if not source_file.exists():
            continue

        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract URLs from this source
        urls = extract_wikipedia_urls(content)

        for url in urls:
            if url not in existing_urls:  # Only new URLs
                discovered_urls.add(url)
                url_sources[url].append(source.get("title", source_id))

    print(f"Discovered URLs: {len(discovered_urls)}")
    print()

    # Score and rank URLs
    scored_urls = []
    for url in discovered_urls:
        score = score_url_relevance(url)
        # Bonus for multiple mentions
        score += len(url_sources[url]) * 5

        scored_urls.append({
            "url": url,
            "score": score,
            "mentioned_in": url_sources[url][:3],  # Top 3 sources
            "mention_count": len(url_sources[url])
        })

    # Sort by score
    scored_urls.sort(key=lambda x: x["score"], reverse=True)

    # Display top suggestions
    print("TOP URL SUGGESTIONS")
    print("-" * 70)

    for i, item in enumerate(scored_urls[:max_suggestions], 1):
        title = item["url"].split('/wiki/')[-1].replace('_', ' ')
        print(f"\n{i}. {title}")
        print(f"   URL: {item['url']}")
        print(f"   Score: {item['score']} | Mentions: {item['mention_count']}")
        if item["mentioned_in"]:
            print(f"   Found in: {', '.join(item['mentioned_in'][:2])}")

    # Save results
    output_file = Path(__file__).parent / f"url_discovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "existing_urls": len(existing_urls),
            "discovered_urls": len(discovered_urls),
            "suggestions": scored_urls[:max_suggestions]
        }, f, indent=2)

    print()
    print("=" * 70)
    print(f"Results saved to: {output_file}")

    return scored_urls[:max_suggestions]

def suggest_for_topic(topic_name, max_suggestions=10):
    """Suggest URLs specifically relevant to a topic"""
    print(f"Finding URL suggestions for topic: {topic_name}")
    print("=" * 70)

    index = load_index()
    existing_urls = get_existing_urls(index)

    # Find the topic
    topic = None
    for tid, t in index.get("topics", {}).items():
        if t["name"].lower() == topic_name.lower():
            topic = t
            break

    if not topic:
        print(f"Topic '{topic_name}' not found.")
        return []

    # Get URLs from topic's existing sources
    topic_sources = topic.get("sources", [])
    discovered_urls = set()

    for source_id in topic_sources:
        # Read content from source file
        source_file = KNOWLEDGE_DIR / f"source_{source_id}.txt"
        if not source_file.exists():
            continue

        with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        urls = extract_wikipedia_urls(content)
        discovered_urls.update(urls)

    # Filter out existing
    new_urls = discovered_urls - existing_urls

    # Score by topic relevance
    topic_terms = topic_name.lower().split() + topic.get("description", "").lower().split()
    scored_urls = []
    for url in new_urls:
        score = score_url_relevance(url, topic_terms)
        scored_urls.append({"url": url, "score": score})

    scored_urls.sort(key=lambda x: x["score"], reverse=True)

    print(f"Found {len(new_urls)} new URLs related to {topic_name}")
    print()

    for i, item in enumerate(scored_urls[:max_suggestions], 1):
        title = item["url"].split('/wiki/')[-1].replace('_', ' ')
        print(f"{i}. {title} (score: {item['score']})")
        print(f"   {item['url']}")

    return scored_urls[:max_suggestions]

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "topic" and len(sys.argv) > 2:
            topic_name = sys.argv[2]
            max_suggestions = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            suggest_for_topic(topic_name, max_suggestions)
        else:
            print("Usage:")
            print("  python3 url_discoverer.py              # Discover all URLs")
            print("  python3 url_discoverer.py topic <name> # Suggest for specific topic")
    else:
        discover_urls()

if __name__ == "__main__":
    main()
