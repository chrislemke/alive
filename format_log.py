#!/usr/bin/env python3
"""Formats Claude Code stream-json output into human-readable log lines."""

import json
import sys
from datetime import datetime, timezone


def timestamp():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def truncate(s, maxlen=200):
    s = str(s).replace("\n", " ").strip()
    return s[:maxlen] + "..." if len(s) > maxlen else s


def format_event(event):
    t = event.get("type")

    if t == "system":
        session_id = event.get("session_id", "")
        return f"[{timestamp()}] SESSION INIT (id: {session_id[:12]})"

    if t == "assistant":
        message = event.get("message", {})
        lines = []
        for block in message.get("content", []):
            bt = block.get("type")
            if bt == "text":
                text = block.get("text", "")
                lines.append(f"[{timestamp()}] THINKING: {truncate(text, 300)}")
            elif bt == "tool_use":
                name = block.get("name", "?")
                inp = block.get("input", {})
                detail = format_tool_input(name, inp)
                lines.append(f"[{timestamp()}] TOOL CALL: {name} → {detail}")
        return "\n".join(lines) if lines else None

    if t == "tool_result":
        # Show tool name if available, plus truncated output
        name = event.get("tool_name", "")
        content = event.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                b.get("text", "") for b in content if isinstance(b, dict)
            )
        prefix = f"{name}: " if name else ""
        return f"[{timestamp()}] RESULT: {prefix}{truncate(content)}"

    if t == "result":
        cost = event.get("cost_usd", 0)
        duration = event.get("duration_ms", 0)
        dur_s = duration / 1000 if duration else 0
        return f"[{timestamp()}] SESSION END (cost: ${cost:.4f}, duration: {dur_s:.1f}s)"

    return None


def format_tool_input(name, inp):
    if name == "Bash":
        return truncate(inp.get("command", str(inp)))
    if name in ("Read", "Write"):
        return inp.get("file_path", str(inp))
    if name == "Edit":
        fp = inp.get("file_path", "")
        old = truncate(inp.get("old_string", ""), 60)
        return f"{fp} (replacing: {old})"
    if name == "Glob":
        return inp.get("pattern", str(inp))
    if name == "Grep":
        return f'/{inp.get("pattern", "")}/ in {inp.get("path", ".")}'
    if name == "Task":
        return truncate(inp.get("description", inp.get("prompt", str(inp))), 120)
    if name == "WebFetch":
        return inp.get("url", str(inp))
    if name == "WebSearch":
        return inp.get("query", str(inp))
    return truncate(str(inp), 120)


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            print(f"[{timestamp()}] RAW: {truncate(line)}", flush=True)
            continue

        formatted = format_event(event)
        if formatted:
            print(formatted, flush=True)


if __name__ == "__main__":
    main()
