#!/usr/bin/env bash
# Activate virtual environment (if present) and run the scheduler once.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"
if [ -d ".venv" ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi
# Run the Python module; forward any extra args.
python -m src.scraper.main --once "$@"
EXITCODE=$?
exit $EXITCODE