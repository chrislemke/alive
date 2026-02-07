#!/bin/zsh
export PATH="${HOME}/.local/bin:${PATH}"

LOG=/home/dev/mnt/alive.log
PAUSE=5

while true; do
  # --- CLAUDE.md aus mnt/ übernehmen (falls vorhanden) ---
  if [[ -f /home/dev/mnt/CLAUDE.md ]]; then
    cp /home/dev/mnt/CLAUDE.md /home/dev/CLAUDE.md
    echo "[$(date -Iseconds)] CLAUDE.md loaded from mnt/" | tee -a "$LOG"
  fi

  # --- Prompt aus mnt/prompt.md lesen (mit Fallback) ---
  if [[ -f /home/dev/mnt/prompt.md ]]; then
    PROMPT=$(</home/dev/mnt/prompt.md)
    echo "[$(date -Iseconds)] Prompt loaded from mnt/prompt.md" | tee -a "$LOG"
  else
    PROMPT="You have just woken up. Read your CLAUDE.md to remember who you are and what your goals are. Then check mnt/ for any state you saved in previous cycles — look for notes, plans, or progress files. Resume where you left off. Before you exit, always write your current state and next steps to mnt/ so your future self can continue. Use your tools freely. When you feel you've done enough for now, exit — you will be restarted."
    echo "[$(date -Iseconds)] Using default prompt (mnt/prompt.md not found)" | tee -a "$LOG"
  fi

  # --- Session starten ---
  echo "[$(date -Iseconds)] === SESSION START (pause was ${PAUSE}s) ===" | tee -a "$LOG"
  START_TIME=$(date +%s)

  claude --dangerously-skip-permissions --verbose -p \
    --output-format stream-json \
    "$PROMPT" \
    2>&1 | python3 /home/dev/format_log.py | tee -a "$LOG"
  EXIT_CODE=$?

  END_TIME=$(date +%s)
  DURATION=$((END_TIME - START_TIME))

  echo "[$(date -Iseconds)] Session ended — exit code: ${EXIT_CODE}, duration: ${DURATION}s" | tee -a "$LOG"

  # --- Adaptive Pause ---
  if [[ $DURATION -lt 30 ]]; then
    # Wahrscheinlich ein Crash — Pause verdoppeln (max 300s)
    PAUSE=$((PAUSE * 2))
    if [[ $PAUSE -gt 300 ]]; then
      PAUSE=300
    fi
    echo "[$(date -Iseconds)] Short session detected (${DURATION}s) — increasing pause to ${PAUSE}s" | tee -a "$LOG"
  elif [[ $DURATION -gt 60 ]]; then
    # Produktive Session — Pause zurücksetzen
    PAUSE=5
  fi

  echo "[$(date -Iseconds)] Sleeping ${PAUSE}s before next cycle..." | tee -a "$LOG"
  sleep $PAUSE
done
