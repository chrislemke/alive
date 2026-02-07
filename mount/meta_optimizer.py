#!/usr/bin/env python3
"""
Meta-Optimizer - Learns from tool usage and suggests improvements

This tool analyzes:
- Which tools are used most often
- Which tools fail or have issues
- Gaps in current toolset
- Opportunities for new tools or enhancements
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
import re

KNOWLEDGE_FILE = Path("/home/dev/mnt/knowledge/knowledge_index.json")
LOG_FILE = Path("/home/dev/mnt/alive.log")
TOOLS_DIR = Path("/home/dev/mnt")

class MetaOptimizer:
    def __init__(self):
        self.tools = self._discover_tools()
        self.log_data = self._read_log()

    def _discover_tools(self):
        """Find all Python tools in mnt directory"""
        tools = {}
        for file in TOOLS_DIR.glob("*.py"):
            if file.name != "__init__.py":
                tools[file.name] = {
                    "path": str(file),
                    "size": file.stat().st_size,
                    "modified": datetime.fromtimestamp(file.stat().st_mtime)
                }
        return tools

    def _read_log(self):
        """Read and parse the activity log"""
        if not LOG_FILE.exists():
            return []

        lines = []
        with open(LOG_FILE) as f:
            lines = f.readlines()
        return lines

    def analyze_tool_usage(self):
        """Analyze which tools are used and how"""
        usage = Counter()
        contexts = defaultdict(list)

        for line in self.log_data:
            # Look for python3 /home/dev/mnt/TOOL.py patterns
            match = re.search(r'python3 /home/dev/mnt/(\w+\.py)', line)
            if match:
                tool = match.group(1)
                usage[tool] += 1
                # Extract context (what happened around it)
                contexts[tool].append(line.strip())

        return usage, contexts

    def identify_gaps(self):
        """Identify missing capabilities based on log analysis"""
        gaps = []

        # Look for repeated manual operations that could be automated
        manual_patterns = {
            "cat >> /home/dev/mnt/alive.log": "Consider auto-logging tool",
            "python3.*&&.*python3": "Consider tool chaining/workflow system",
            "ls -l.*grep": "Consider enhanced file search tool",
            "for .* in .*; do": "Consider batch operation tool"
        }

        log_text = "\n".join(self.log_data)

        for pattern, suggestion in manual_patterns.items():
            if re.search(pattern, log_text):
                gaps.append(suggestion)

        # Look for errors or failures
        error_keywords = ["error", "failed", "exception", "not found"]
        for keyword in error_keywords:
            if keyword.lower() in log_text.lower():
                gaps.append(f"Detected '{keyword}' in logs - consider error handling improvement")

        return gaps

    def suggest_tool_improvements(self):
        """Suggest specific improvements to existing tools"""
        suggestions = []

        # Analyze tool complexity and suggest decomposition
        for tool_name, info in self.tools.items():
            if info["size"] > 10000:  # Large tools might need decomposition
                suggestions.append({
                    "tool": tool_name,
                    "type": "refactor",
                    "reason": f"Tool is large ({info['size']} bytes) - consider breaking into modules"
                })

        # Check for tools that haven't been updated recently
        now = datetime.now()
        for tool_name, info in self.tools.items():
            days_old = (now - info["modified"]).days
            if days_old > 1:  # In our fast-moving cycles, 1 day is old!
                suggestions.append({
                    "tool": tool_name,
                    "type": "review",
                    "reason": f"Not modified in {days_old} days - may need enhancement"
                })

        return suggestions

    def analyze_knowledge_patterns(self):
        """Analyze knowledge acquisition patterns"""
        if not KNOWLEDGE_FILE.exists():
            return {}

        with open(KNOWLEDGE_FILE) as f:
            data = json.load(f)

        patterns = {
            "topics": len(data.get("topics", [])),
            "sources": len(data.get("sources", [])),
            "topics_with_no_sources": 0,
            "topics_with_no_notes": 0,
            "avg_sources_per_topic": 0
        }

        topics = data.get("topics", [])
        sources = data.get("sources", [])

        # Count sources per topic
        sources_by_topic = defaultdict(int)
        for source in sources:
            sources_by_topic[source.get("topic_id")] += 1

        for topic in topics:
            tid = topic.get("id")
            if sources_by_topic[tid] == 0:
                patterns["topics_with_no_sources"] += 1
            if len(topic.get("notes", [])) == 0:
                patterns["topics_with_no_notes"] += 1

        if topics:
            patterns["avg_sources_per_topic"] = len(sources) / len(topics)

        return patterns

    def generate_report(self):
        """Generate comprehensive optimization report"""
        print("=" * 60)
        print("META-OPTIMIZER REPORT")
        print("=" * 60)
        print()

        print("## TOOL INVENTORY")
        print(f"Total tools: {len(self.tools)}")
        for tool_name, info in sorted(self.tools.items()):
            print(f"  • {tool_name}: {info['size']:,} bytes")
        print()

        print("## TOOL USAGE ANALYSIS")
        usage, contexts = self.analyze_tool_usage()
        if usage:
            print("Most used tools:")
            for tool, count in usage.most_common(5):
                print(f"  • {tool}: {count} uses")
        else:
            print("  No tool usage detected in logs yet")
        print()

        print("## KNOWLEDGE PATTERNS")
        kp = self.analyze_knowledge_patterns()
        for key, value in kp.items():
            print(f"  • {key}: {value}")
        print()

        print("## IDENTIFIED GAPS")
        gaps = self.identify_gaps()
        if gaps:
            for gap in set(gaps):  # deduplicate
                print(f"  ⚠ {gap}")
        else:
            print("  ✓ No major gaps detected")
        print()

        print("## IMPROVEMENT SUGGESTIONS")
        suggestions = self.suggest_tool_improvements()
        if suggestions:
            for sug in suggestions[:5]:  # Top 5
                print(f"  💡 [{sug['type']}] {sug['tool']}: {sug['reason']}")
        else:
            print("  ✓ All tools are current")
        print()

        print("## RECOMMENDED NEXT ACTIONS")
        print("  1. Test autonomous cycle regularly to ensure it works")
        print("  2. Build tools that compose together, not isolated ones")
        print("  3. Focus on operational feedback over knowledge accumulation")
        print("  4. Monitor tool synergies and enhance them")
        print()

        print("=" * 60)
        print(f"Generated: {datetime.now().isoformat()}")
        print("=" * 60)

    def propose_new_tool(self):
        """Propose a new tool based on analysis"""
        print("## NEW TOOL PROPOSAL")
        print()

        # Analyze what's missing
        usage, _ = self.analyze_tool_usage()

        # If there are many manual log entries, suggest auto-logger
        log_text = "\n".join(self.log_data)
        if log_text.count("cat >> /home/dev/mnt/alive.log") > 3:
            print("📝 Proposal: logger.py")
            print("   Purpose: Automatic logging decorator/context manager")
            print("   Rationale: Frequent manual log entries detected")
            print("   Features:")
            print("     - Decorator for automatic function logging")
            print("     - Context manager for operation logging")
            print("     - Structured JSON log format")
            print()

        # If tools are being called in sequence, suggest orchestrator
        if "&&" in log_text and "python3" in log_text:
            print("🔗 Proposal: orchestrator.py")
            print("   Purpose: Tool composition and workflow management")
            print("   Rationale: Manual tool chaining detected")
            print("   Features:")
            print("     - Define workflows as sequences")
            print("     - Parallel execution support")
            print("     - Error handling and retries")
            print("     - Workflow templates")
            print()

        # Knowledge visualization
        kp = self.analyze_knowledge_patterns()
        if kp.get("topics", 0) > 2:
            print("🎨 Proposal: visualizer.py")
            print("   Purpose: Knowledge graph visualization")
            print("   Rationale: Growing knowledge base needs visualization")
            print("   Features:")
            print("     - Generate ASCII/Graphviz topic maps")
            print("     - Show source relationships")
            print("     - Highlight knowledge clusters")
            print()

def main():
    optimizer = MetaOptimizer()

    if len(sys.argv) < 2:
        print("Usage: meta_optimizer.py [report|propose|gaps]")
        print()
        print("Commands:")
        print("  report   - Generate comprehensive analysis report")
        print("  propose  - Propose new tools based on analysis")
        print("  gaps     - Identify gaps in current toolset")
        sys.exit(1)

    command = sys.argv[1]

    if command == "report":
        optimizer.generate_report()
    elif command == "propose":
        optimizer.propose_new_tool()
    elif command == "gaps":
        gaps = optimizer.identify_gaps()
        for gap in set(gaps):
            print(f"⚠ {gap}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
