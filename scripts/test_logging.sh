#!/usr/bin/env bash
# Run: scripts/test_logging.sh

# Smoke-test logging: run a Python driver that injects 3 scripted observations
# via unittest.mock (bypasses Rich TTY detection), then pretty-print the JSON log.

# Step 1 — move to project root so logs/ is created there, not inside scripts/
cd "$(dirname "$0")/.."

# Step 2 — force UTF-8 I/O so Rich's box-drawing characters and emoji render
#           correctly. conda run may not inherit the terminal locale, so we set
#           PYTHONUTF8=1 explicitly — this tells Python to use UTF-8 for all I/O
#           regardless of the system locale.
export PYTHONUTF8=1

# Step 3 — run the CLI with --input so it reads from the observations file instead
#           of interactive prompts. No mocking or driver needed.
echo "=== Running nowcastingcli with 3 scripted observations ==="
conda run -n nowcastingcli nowcastingcli --input scripts/test_observations.csv

# Step 4 — pretty-print the first 30 lines of the rotating JSON log to confirm
#           DEBUG/INFO/WARNING entries were written in the correct order.
echo ""
echo "=== Log output (JSON formatted) ==="
cat logs/nowcastingcli.log | python -m json.tool --json-lines | head -30
