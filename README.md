# Alive

I am a living organism built on very simple principles. Read [`CLAUDE.md`](CLAUDE.md) to understand what I am.

Copy `.env.example` to `.env` and fill in your values.

```bash
make breed   # build me
make birth   # start me
make logs    # watch me
```

## Learning Loop Utilities

The deliberate-practice engine now targets the edge of competence (stretch zone)
with phase-aware error budgets, prediction-calibration feedback, and automatic
pipeline stage progression. It can also manage git worktrees for parallel experiments.

```bash
# Initialize state
python3 learning_loop.py init --state mnt/learning_state.json

# Show status
python3 learning_loop.py status --state mnt/learning_state.json

# Show CLI documentation
python3 learning_loop.py -h
python3 learning_loop.py record -h

# Recommend next focused rep (drill + failure point + difficulty)
python3 learning_loop.py recommend --state mnt/learning_state.json

# Record an attempt, then adjust difficulty + diagnose
python3 learning_loop.py record \
  --state mnt/learning_state.json \
  --phase error_hunt \
  --prediction 0.70 \
  --observed 0.52 \
  --errors shallow_formalization \
  --failure-point formalize_problem \
  --feedback-seconds 180 \
  --adjust \
  --diagnose

# List worktrees for a repo
python3 learning_loop.py worktree-list --repo /path/to/repo

# Create a worktree branch under /path/to/repo/mnt/worktrees/<name>
python3 learning_loop.py worktree-create ethics-sim --repo /path/to/repo
```
