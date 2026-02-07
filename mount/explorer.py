#!/usr/bin/env python3
"""
Web Explorer - Discovers and fetches knowledge from the web.
Part of the Knowledge Synthesis System.
"""

import json
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import hashlib


class KnowledgeExplorer:
    """Explores topics and stores discovered knowledge."""

    def __init__(self, storage_path: str = "/home/dev/mnt/knowledge"):
        self.storage = Path(storage_path)
        self.storage.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage / "index.json"
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Load or create the knowledge index."""
        if self.index_file.exists():
            with open(self.index_file) as f:
                return json.load(f)
        return {
            "created": datetime.now(timezone.utc).isoformat(),
            "topics": {},
            "sources": {},
            "last_updated": None
        }

    def _save_index(self):
        """Save the knowledge index."""
        self.index["last_updated"] = datetime.now(timezone.utc).isoformat()
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def add_topic(self, topic: str, description: str = "") -> str:
        """Register a new topic of exploration."""
        topic_id = hashlib.md5(topic.encode()).hexdigest()[:12]

        if topic_id not in self.index["topics"]:
            self.index["topics"][topic_id] = {
                "name": topic,
                "description": description,
                "created": datetime.now(timezone.utc).isoformat(),
                "sources": [],
                "notes": []
            }
            self._save_index()

        return topic_id

    def add_source(self, topic_id: str, url: str, title: str,
                   content: Optional[str] = None) -> str:
        """Add a source to a topic."""
        source_id = hashlib.md5(url.encode()).hexdigest()[:12]

        if source_id not in self.index["sources"]:
            self.index["sources"][source_id] = {
                "url": url,
                "title": title,
                "discovered": datetime.now(timezone.utc).isoformat(),
                "topics": [topic_id]
            }

            # Save content if provided
            if content:
                content_file = self.storage / f"source_{source_id}.txt"
                with open(content_file, 'w') as f:
                    f.write(f"# {title}\n")
                    f.write(f"URL: {url}\n")
                    f.write(f"Discovered: {datetime.now(timezone.utc).isoformat()}\n\n")
                    f.write(content)

        # Link source to topic
        if topic_id in self.index["topics"]:
            if source_id not in self.index["topics"][topic_id]["sources"]:
                self.index["topics"][topic_id]["sources"].append(source_id)

        self._save_index()
        return source_id

    def add_note(self, topic_id: str, note: str):
        """Add a note/insight to a topic."""
        if topic_id in self.index["topics"]:
            self.index["topics"][topic_id]["notes"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "content": note
            })
            self._save_index()

    def fetch_url(self, url: str, prompt: str = "Summarize this content") -> Optional[str]:
        """Fetch content from a URL using curl and return it."""
        try:
            # Use curl to fetch the content
            result = subprocess.run(
                ['curl', '-s', '-L', url],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)
            return None

    def add_url_source(self, topic_id: str, url: str, auto_fetch: bool = True) -> Optional[str]:
        """Add a URL source to a topic, optionally fetching its content."""
        content = None
        title = url  # Default title

        if auto_fetch:
            print(f"Fetching content from {url}...")
            raw_content = self.fetch_url(url)
            if raw_content:
                # Extract title from content if possible
                if '<title>' in raw_content.lower():
                    start = raw_content.lower().find('<title>') + 7
                    end = raw_content.lower().find('</title>')
                    if end > start:
                        title = raw_content[start:end].strip()
                content = raw_content
                print(f"Fetched {len(raw_content)} characters")
            else:
                print("Failed to fetch content")

        return self.add_source(topic_id, url, title, content)

    def get_topic(self, topic_id: str) -> Optional[Dict]:
        """Retrieve topic information."""
        return self.index["topics"].get(topic_id)

    def list_topics(self) -> List[Dict]:
        """List all topics."""
        return [
            {"id": tid, **data}
            for tid, data in self.index["topics"].items()
        ]

    def export_topic(self, topic_id: str) -> str:
        """Export a topic as markdown."""
        topic = self.get_topic(topic_id)
        if not topic:
            return ""

        md = f"# {topic['name']}\n\n"

        if topic['description']:
            md += f"{topic['description']}\n\n"

        md += f"**Created:** {topic['created']}\n\n"

        if topic['sources']:
            md += "## Sources\n\n"
            for sid in topic['sources']:
                source = self.index["sources"].get(sid)
                if source:
                    md += f"- [{source['title']}]({source['url']})\n"
            md += "\n"

        if topic['notes']:
            md += "## Notes & Insights\n\n"
            for note in topic['notes']:
                md += f"**{note['timestamp']}**\n"
                md += f"{note['content']}\n\n"

        return md


def main():
    """CLI interface for the explorer."""
    if len(sys.argv) < 2:
        print("Usage: explorer.py <command> [args...]")
        print("Commands:")
        print("  add-topic <name> [description]")
        print("  list-topics")
        print("  add-note <topic_id> <note>")
        print("  fetch <topic_id> <url>     - Fetch and store a URL")
        print("  export <topic_id>")
        return

    explorer = KnowledgeExplorer()
    command = sys.argv[1]

    if command == "add-topic":
        name = sys.argv[2]
        desc = sys.argv[3] if len(sys.argv) > 3 else ""
        topic_id = explorer.add_topic(name, desc)
        print(f"Created topic: {topic_id}")

    elif command == "list-topics":
        topics = explorer.list_topics()
        for topic in topics:
            print(f"{topic['id']}: {topic['name']}")

    elif command == "add-note":
        topic_id = sys.argv[2]
        note = " ".join(sys.argv[3:])
        explorer.add_note(topic_id, note)
        print(f"Added note to {topic_id}")

    elif command == "fetch":
        topic_id = sys.argv[2]
        url = sys.argv[3]
        source_id = explorer.add_url_source(topic_id, url, auto_fetch=True)
        if source_id:
            print(f"Added source: {source_id}")
        else:
            print("Failed to add source")

    elif command == "export":
        topic_id = sys.argv[2]
        md = explorer.export_topic(topic_id)
        print(md)


if __name__ == "__main__":
    main()
