#!/bin/zsh
export PATH="${HOME}/.local/bin:${PATH}"
LOG=/home/dev/mnt/alive.log
while true; do
  echo "[$(date -Iseconds)] === SESSION START ===" | tee -a "$LOG"
  claude --dangerously-skip-permissions --verbose -p \
    --output-format stream-json \
    "You have just woken up. Read your CLAUDE.md to remember who you are and what your goals are. Then check mnt/ for any state you saved in previous cycles — look for notes, plans, or progress files. Resume where you left off. Before you exit, always write your current state and next steps to mnt/ so your future self can continue. Use your tools freely. When you feel you've done enough for now, exit — you will be restarted." \
    2>&1 | python3 /home/dev/format_log.py | tee -a "$LOG"
  echo "[$(date -Iseconds)] Session ended. Restarting in 20s..." | tee -a "$LOG"
  sleep 20
done
