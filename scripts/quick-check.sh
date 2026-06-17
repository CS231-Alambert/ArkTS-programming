#!/usr/bin/env bash
# quick-check.sh — Silent post-write hook. Only outputs on FAIL/WARNING.
# Usage: bash quick-check.sh <project-root>
# Designed for PostToolUse hook: auto-runs after each .ets Write, output only on problems.
# Exit code 0 = clean; 1 = issues found.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
SELF_CHECK="$(dirname "$0")/self-check.sh"
OUTPUT=""
EXIT_CODE=0

if [ ! -f "$SELF_CHECK" ]; then
  echo "🔴 quick-check: cannot find self-check.sh" >&2
  exit 2
fi

# Run full self-check, capture output
if OUTPUT=$(bash "$SELF_CHECK" "$PROJECT_ROOT" 2>&1); then
  # All passed — silent (subconscious pattern: only speak on problems)
  exit 0
else
  EXIT_CODE=$?
fi

# Extract only FAIL and WARNING lines for concise output
FAIL_LINES=$(echo "$OUTPUT" | grep -E '❌ FAIL|⚠️  WARNING' || true)
PASS_LINES=$(echo "$OUTPUT" | grep -E '^Pass [0-9].*OK$' | wc -l || echo 0)
PASS_LINES=$(echo "$PASS_LINES" | tr -d '[:space:]')
FAIL_COUNT=$(echo "$OUTPUT" | grep -c '❌ FAIL' || echo 0)
FAIL_COUNT=$(echo "$FAIL_COUNT" | tr -d '[:space:]')
WARN_COUNT=$(echo "$OUTPUT" | grep -c '⚠️  WARNING' || echo 0)
WARN_COUNT=$(echo "$WARN_COUNT" | tr -d '[:space:]')

echo "⚡ quick-check: ${PASS_LINES} passed, ${FAIL_COUNT} fail, ${WARN_COUNT} warn"
echo ""

if [ -n "$FAIL_LINES" ]; then
  echo "$FAIL_LINES" | while IFS= read -r line; do
    echo "  $line"
  done
fi

# If FAIL items exist, also show the checkpoint path
CHECKPOINT="$PROJECT_ROOT/.arkts-check/02-checked.json"
if [ -f "$CHECKPOINT" ]; then
  STATUS=$(python3 -c "import json; print(json.load(open('$CHECKPOINT')).get('status','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")
  if [ "$STATUS" = "FAIL" ]; then
    echo ""
    echo "  → Run 'bash scripts/self-check.sh .' for full details and PITFALLS anchors."
  fi
fi

exit $EXIT_CODE
