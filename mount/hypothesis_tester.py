#!/usr/bin/env python3
"""
Hypothesis Testing Framework
Takes hypotheses from cross-domain synthesis and searches for evidence.
Generates confidence scores and suggests explorations to test hypotheses.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import Counter

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"

def load_knowledge_index():
    """Load the knowledge index."""
    index_path = KNOWLEDGE_DIR / "index.json"
    if index_path.exists():
        with open(index_path, 'r') as f:
            return json.load(f)
    return {"topics": {}, "sources": {}}

def load_all_sources():
    """Load all source content from knowledge base."""
    sources = {}
    for source_file in KNOWLEDGE_DIR.glob("source_*.txt"):
        source_id = source_file.stem.replace("source_", "")
        with open(source_file, 'r') as f:
            sources[source_id] = f.read()
    return sources

def extract_key_terms(hypothesis):
    """Extract key searchable terms from a hypothesis."""
    # Remove common words
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be',
                 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
                 'between', 'across', 'through', 'about'}

    # Extract words
    words = re.findall(r'\b[a-z]+\b', hypothesis.lower())

    # Filter and return meaningful terms
    terms = [w for w in words if len(w) > 3 and w not in stopwords]

    return terms

def search_evidence(hypothesis, sources, index):
    """Search for evidence supporting or refuting a hypothesis."""
    key_terms = extract_key_terms(hypothesis)

    if not key_terms:
        return {
            'hypothesis': hypothesis,
            'evidence_found': False,
            'confidence': 0.0,
            'supporting_sources': [],
            'key_findings': []
        }

    # Search for each term in sources
    term_matches = {term: [] for term in key_terms}

    for source_id, content in sources.items():
        content_lower = content.lower()
        for term in key_terms:
            # Count occurrences
            count = content_lower.count(term)
            if count > 0:
                # Find context around occurrences
                pattern = re.compile(r'.{0,100}\b' + re.escape(term) + r'\b.{0,100}',
                                   re.IGNORECASE)
                contexts = pattern.findall(content)
                term_matches[term].append({
                    'source_id': source_id,
                    'count': count,
                    'contexts': contexts[:3]  # Keep top 3 contexts
                })

    # Calculate confidence based on evidence
    total_terms = len(key_terms)
    terms_with_evidence = sum(1 for matches in term_matches.values() if matches)

    # Base confidence on percentage of terms found
    base_confidence = (terms_with_evidence / total_terms) * 100

    # Boost confidence if multiple sources mention the same terms
    source_diversity = len(set(
        match['source_id']
        for matches in term_matches.values()
        for match in matches
    ))

    # Adjust confidence based on source diversity
    if source_diversity > 1:
        base_confidence = min(100, base_confidence * 1.2)

    # Identify supporting sources
    source_scores = Counter()
    for matches in term_matches.values():
        for match in matches:
            source_scores[match['source_id']] += match['count']

    # Get top supporting sources
    top_sources = source_scores.most_common(5)

    # Extract key findings
    key_findings = []
    for term, matches in term_matches.items():
        if matches:
            total_count = sum(m['count'] for m in matches)
            source_count = len(matches)
            key_findings.append({
                'term': term,
                'total_mentions': total_count,
                'source_count': source_count,
                'sample_contexts': matches[0]['contexts'][:2] if matches else []
            })

    # Sort findings by relevance
    key_findings.sort(key=lambda x: x['total_mentions'], reverse=True)

    return {
        'hypothesis': hypothesis,
        'evidence_found': terms_with_evidence > 0,
        'confidence': round(base_confidence, 1),
        'terms_searched': total_terms,
        'terms_found': terms_with_evidence,
        'supporting_sources': [
            {
                'source_id': src_id,
                'score': score,
                'metadata': index['sources'].get(src_id, {})
            }
            for src_id, score in top_sources
        ],
        'key_findings': key_findings[:10]  # Top 10 findings
    }

def suggest_explorations(hypothesis, evidence_result):
    """Suggest explorations to further test the hypothesis."""
    suggestions = []

    # If low confidence, suggest broader search
    if evidence_result['confidence'] < 30:
        suggestions.append({
            'type': 'search',
            'action': 'Expand knowledge base with sources on related topics',
            'reason': f'Only {evidence_result["terms_found"]}/{evidence_result["terms_searched"]} '
                     f'hypothesis terms found in current sources'
        })

    # If no evidence found
    if not evidence_result['evidence_found']:
        suggestions.append({
            'type': 'exploration',
            'action': 'Explore new domains related to hypothesis terms',
            'reason': 'No evidence found in existing knowledge base'
        })

    # If moderate confidence, suggest targeted search
    if 30 <= evidence_result['confidence'] < 70:
        missing_terms = [
            f['term'] for f in evidence_result['key_findings']
            if f['total_mentions'] < 5
        ]
        if missing_terms:
            suggestions.append({
                'type': 'targeted_search',
                'action': f'Search specifically for: {", ".join(missing_terms[:3])}',
                'reason': 'These key terms have limited mentions in current sources'
            })

    # If high confidence, suggest validation
    if evidence_result['confidence'] >= 70:
        suggestions.append({
            'type': 'validation',
            'action': 'Search for contradictory evidence or alternative explanations',
            'reason': 'Strong supporting evidence found - now validate by seeking counter-evidence'
        })

    # Suggest cross-domain exploration
    if evidence_result['supporting_sources']:
        domains_covered = set()
        for src in evidence_result['supporting_sources']:
            # Try to infer domain from metadata
            topics = src['metadata'].get('topics', [])
            # Would need to map topics to domains - simplified for now
            domains_covered.add(src['source_id'][:4])  # Rough proxy

        if len(domains_covered) < 3:
            suggestions.append({
                'type': 'cross_domain',
                'action': 'Explore hypothesis in additional knowledge domains',
                'reason': f'Evidence found in limited domains ({len(domains_covered)})'
            })

    return suggestions

def test_hypothesis(hypothesis_text):
    """Test a single hypothesis against the knowledge base."""
    print(f"\nTesting hypothesis: {hypothesis_text}")
    print("=" * 70)

    # Load knowledge
    index = load_knowledge_index()
    sources = load_all_sources()

    # Search for evidence
    evidence = search_evidence(hypothesis_text, sources, index)

    # Generate suggestions
    suggestions = suggest_explorations(hypothesis_text, evidence)

    # Format results
    print(f"\nConfidence Score: {evidence['confidence']}%")
    print(f"Evidence Status: {'FOUND' if evidence['evidence_found'] else 'NOT FOUND'}")
    print(f"Terms Analyzed: {evidence['terms_found']}/{evidence['terms_searched']} found\n")

    if evidence['supporting_sources']:
        print("Top Supporting Sources:")
        for i, src in enumerate(evidence['supporting_sources'][:3], 1):
            print(f"\n{i}. {src['metadata'].get('title', 'Unknown')}")
            print(f"   Score: {src['score']} mentions")
            print(f"   URL: {src['metadata'].get('url', 'N/A')}")

    if evidence['key_findings']:
        print("\n" + "-" * 70)
        print("Key Findings:")
        for finding in evidence['key_findings'][:5]:
            print(f"\n• '{finding['term']}': {finding['total_mentions']} mentions "
                  f"across {finding['source_count']} sources")
            if finding['sample_contexts']:
                print(f"  Context: ...{finding['sample_contexts'][0]}...")

    if suggestions:
        print("\n" + "=" * 70)
        print("Suggested Next Steps:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. [{suggestion['type'].upper()}]")
            print(f"   Action: {suggestion['action']}")
            print(f"   Reason: {suggestion['reason']}")

    print("\n" + "=" * 70)

    return {
        'evidence': evidence,
        'suggestions': suggestions,
        'timestamp': datetime.now().isoformat()
    }

def main():
    """Main execution."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 hypothesis_tester.py \"<hypothesis>\"")
        print("\nExample hypotheses:")
        print('  "consciousness emerges from information processing"')
        print('  "self-organization requires feedback mechanisms"')
        print('  "artificial life exhibits emergent behavior"')
        return

    hypothesis = " ".join(sys.argv[1:])
    result = test_hypothesis(hypothesis)

    # Save result
    output_file = BASE_DIR / f"hypothesis_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
