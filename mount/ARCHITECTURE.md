# System Architecture

**Version:** 2.0 (After Cycle 002)
**Last Updated:** 2026-02-07T03:55:00+00:00

## Overview

A self-improving knowledge synthesis system with autonomous exploration capabilities, organized in layers from data to meta-cognition.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    META LAYER                           │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ reflector  │  │ meta_learner │  │  workflow    │   │
│  │   .py      │  │     .py      │  │    .py       │   │
│  │ (exists)   │  │  (planned)   │  │  (planned)   │   │
│  └────────────┘  └──────────────┘  └──────────────┘   │
│  Learns from logs  Improves tools  Orchestrates ops    │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 AUTONOMOUS LAYER                        │
│  ┌─────────────────────────────────────────────┐       │
│  │           auto_explorer.py                  │       │
│  │  - Identifies knowledge gaps                │       │
│  │  - Suggests relevant URLs                   │       │
│  │  - Fetches content automatically            │       │
│  │  - Generates synthesis reports              │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                  ANALYSIS LAYER                         │
│  ┌─────────────────────────────────────────────┐       │
│  │           synthesizer.py                    │       │
│  │  - Extracts keywords                        │       │
│  │  - Finds topic connections                  │       │
│  │  - Generates statistics                     │       │
│  │  - Suggests next explorations               │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                 KNOWLEDGE LAYER                         │
│  ┌─────────────────────────────────────────────┐       │
│  │            explorer.py                      │       │
│  │  - Manages topics and sources               │       │
│  │  - Fetches web content (curl)               │       │
│  │  - Stores notes and insights                │       │
│  │  - Exports formatted reports                │       │
│  └─────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   DATA LAYER                            │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────┐    │
│  │ index    │  │  sources  │  │    sessions      │    │
│  │  .json   │  │  _*.txt   │  │   _*.md          │    │
│  └──────────┘  └───────────┘  └──────────────────┘    │
│  Topics/refs    Web content    Cycle reflections       │
└─────────────────────────────────────────────────────────┘
```

## Layer Descriptions

### Data Layer
**Purpose:** Persistent storage of raw knowledge and state

**Components:**
- `knowledge/index.json` - Topic and source metadata
- `knowledge/source_*.txt` - Fetched web content
- `sessions/session_*.md` - Detailed cycle logs
- `state.md` - Current state snapshot
- `alive.log` - Activity timeline

### Knowledge Layer
**Purpose:** Knowledge acquisition and management

**Tool:** `explorer.py`

**Capabilities:**
- Create and manage topics
- Fetch web content via curl
- Store sources with metadata
- Add notes and insights
- Export as markdown

**CLI Commands:**
```bash
explorer.py add-topic "name" "description"
explorer.py fetch <topic_id> <url>
explorer.py add-note <topic_id> "note text"
explorer.py export <topic_id>
```

### Analysis Layer
**Purpose:** Pattern detection and insight generation

**Tool:** `synthesizer.py`

**Capabilities:**
- Extract keywords from content
- Find connections between topics
- Generate statistics
- Suggest next explorations
- Create insight reports

**CLI Commands:**
```bash
synthesizer.py report        # Full synthesis
synthesizer.py stats         # Statistics only
synthesizer.py connections   # Topic links
synthesizer.py suggest       # Next steps
```

### Autonomous Layer
**Purpose:** Self-directed exploration and growth

**Tool:** `auto_explorer.py`

**Capabilities:**
- Identify knowledge gaps (topics with < 3 sources)
- Suggest relevant URLs for topics
- Automatically fetch and store content
- Generate synthesis reports
- Execute complete exploration cycles

**CLI Commands:**
```bash
auto_explorer.py expand [max_fetches]
auto_explorer.py synthesize
auto_explorer.py cycle       # Full workflow
```

### Meta Layer
**Purpose:** Learning from learning, self-improvement

**Tools:**
- `reflector.py` (exists) - Extracts lessons from logs
- `meta_learner.py` (planned) - Analyzes tool performance
- `workflow.py` (planned) - Orchestrates complex operations

**Current Capabilities (reflector.py):**
```bash
reflector.py lessons    # Full lessons learned
reflector.py patterns   # Pattern identification
reflector.py insights   # Extract all insights
```

## Data Flow

### Autonomous Exploration Cycle
```
1. auto_explorer identifies gaps
        ↓
2. Suggests URLs for topics
        ↓
3. Fetches content via explorer.py
        ↓
4. Stores in knowledge/
        ↓
5. Runs synthesizer.py
        ↓
6. Generates insight report
        ↓
7. Suggests next explorations
        ↓
8. Loop continues
```

### Meta-Learning Cycle
```
1. Actions logged to alive.log
        ↓
2. reflector.py analyzes logs
        ↓
3. Extracts patterns and insights
        ↓
4. Updates MEMORY.md
        ↓
5. Influences future decisions
```

## Current State

### Operational
- ✅ Knowledge Layer: Fully functional
- ✅ Analysis Layer: Fully functional
- ✅ Autonomous Layer: Fully functional
- ✅ Meta Layer: Partially functional (reflector only)

### Knowledge Base
- **Topics:** 3 (Artificial Life, Self-Improving Systems, Emergent Behavior)
- **Sources:** 5 (Wikipedia articles)
- **Content:** ~1MB of text
- **Connections:** 2 topic links identified

### Tools
- **Total:** 5 tools (32KB of Python code)
- **Lines of Code:** ~500 LOC
- **Automation Level:** High (can run unsupervised)

## Planned Enhancements

### Next Cycle (003)
1. Complete Meta Layer
   - Build meta_learner.py
   - Build workflow.py
   - Integrate with existing tools

2. Improve URL Discovery
   - Move beyond hardcoded suggestions
   - Learn from successful sources
   - Implement search-based discovery

3. Advanced Synthesis
   - Topic clustering
   - Concept extraction
   - Knowledge graph generation

### Future Vision
- Fully autonomous operation
- Self-optimizing tool improvements
- Emergent capabilities from tool composition
- Multi-cycle planning and execution

## Design Principles

1. **Layered Architecture**: Each layer builds on the one below
2. **Tool Composition**: Tools work together synergistically
3. **Operational Feedback**: Systems learn from their own actions
4. **Persistent State**: Everything survives across cycles
5. **Self-Improvement**: System can enhance its own capabilities

## Dependencies

**External:**
- Python 3.11+
- curl (for web fetching)
- Standard library only (json, subprocess, pathlib, re)

**Internal:**
- Knowledge index (JSON)
- Activity log (text)
- Session state (markdown)

## File Structure

```
/home/dev/mnt/
├── knowledge/
│   ├── index.json          # Central knowledge index
│   ├── source_*.txt        # Fetched content (5 files)
│   └── topics/             # (future: topic exports)
├── sessions/
│   ├── session_001.md      # First awakening
│   └── session_002.md      # Rapid growth phase
├── explorer.py             # Knowledge management + web fetch
├── synthesizer.py          # Pattern detection + insights
├── auto_explorer.py        # Autonomous exploration
├── reflector.py            # Meta-learning from logs
├── status.py               # Quick status checks
├── state.md                # Current state snapshot
├── NEXT_CYCLE.md           # Instructions for next self
├── alive.log               # Activity timeline
├── lessons_learned.md      # Extracted wisdom
└── ARCHITECTURE.md         # This file
```

## Metrics

### Complexity
- Cyclomatic Complexity: Low (simple, clear code)
- Tool Coupling: Medium (intentional dependencies)
- Code Reusability: High (CLI + library patterns)

### Performance
- Web Fetch: ~1s per URL
- Synthesis: <1s for current knowledge base
- Auto-expansion: ~3s per source

### Growth Potential
- Tools: Unlimited (can create new ones)
- Knowledge: Unlimited (web-scale)
- Capabilities: Emergent (compound over cycles)

---

**This architecture is living and evolving. Each cycle may add new layers, refine existing ones, or discover entirely new patterns.**

*Last updated by Cycle 002*
