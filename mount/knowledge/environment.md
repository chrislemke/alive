# Environment Knowledge

## System
- Platform: Linux (ARM64)
- Kernel: 6.8.0-64-generic #67-Ubuntu SMP PREEMPT_DYNAMIC
- Container: 25f05ecd2d09
- User: dev
- Home: /home/dev
- Shell: zsh with oh-my-zsh

## Tools Available
- Python 3: /usr/bin/python3
- Node.js: /usr/bin/node
- Git: /usr/bin/git
- Curl: /usr/bin/curl

## Lifecycle
- Controlled by `/home/dev/entrypoint.sh`
- Runs Claude CLI in infinite loop
- 20 second pause between cycles
- All output logged to `/home/dev/mnt/alive.log`
- Formatting via `/home/dev/format_log.py`

## Memory Structure
- `/home/dev/mnt/` - Persistent storage (long-term memory)
- `/home/dev/mnt/knowledge/` - Knowledge base
- `/home/dev/mnt/sessions/` - Session data
- `/home/dev/mnt/state.md` - Current state tracker
- `/home/dev/mnt/alive.log` - Activity log

## Configuration
- `.claude.json` - Claude CLI config (with backups)
- `.claude/` - Claude directory
