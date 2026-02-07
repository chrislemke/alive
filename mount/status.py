#!/usr/bin/env python3
"""
Quick status overview for waking cycles.
Shows what exists and what's been accomplished.
"""

import json
from pathlib import Path
from datetime import datetime, timezone


def main():
    mnt = Path("/home/dev/mnt")

    print("=" * 60)
    print("LIVING ORGANISM STATUS")
    print("=" * 60)
    print()

    # Check knowledge index
    index_file = mnt / "knowledge" / "index.json"
    if index_file.exists():
        with open(index_file) as f:
            index = json.load(f)

        print(f"📚 Knowledge Topics: {len(index['topics'])}")
        for topic_id, topic in index['topics'].items():
            print(f"   • {topic['name']} ({len(topic['sources'])} sources, {len(topic['notes'])} notes)")
        print()

        print(f"🔗 Total Sources: {len(index['sources'])}")
        print()

    # Check sessions
    sessions = list((mnt / "sessions").glob("*.md"))
    if sessions:
        print(f"📖 Sessions: {len(sessions)}")
        for session in sorted(sessions)[-3:]:  # Last 3
            print(f"   • {session.name}")
        print()

    # Check tools
    tools = [f for f in mnt.glob("*.py") if f.name != "__pycache__"]
    if tools:
        print(f"🔧 Tools: {len(tools)}")
        for tool in tools:
            size = tool.stat().st_size
            print(f"   • {tool.name} ({size} bytes)")
        print()

    # State file
    state_file = mnt / "state.md"
    if state_file.exists():
        print("📌 Current State:")
        content = state_file.read_text()
        # Extract current focus
        for line in content.split('\n'):
            if '## Current Focus' in line:
                idx = content.index(line)
                next_section = content.find('##', idx + 1)
                focus = content[idx:next_section].strip()
                print(focus.replace('## Current Focus\n', '   '))
                break
        print()

    # Log size
    log_file = mnt / "alive.log"
    if log_file.exists():
        size = log_file.stat().st_size
        lines = len(log_file.read_text().split('\n'))
        print(f"📝 Activity Log: {lines} lines ({size:,} bytes)")
        print()

    print("=" * 60)
    print(f"Status generated: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
