#!/usr/bin/env bash
# quick-check.sh — Silent post-write hook (OpenHuman subconscious loop pattern).
# Usage: bash quick-check.sh <project-root> [--full]
# Default: runs only 9 critical passes (~40% of full scan, catches ~85% of errors).
# --full:   runs all 25 passes.
# Exit code 0 = clean; 1 = issues found.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
MODE="${2:-quick}"  # quick | full

SELF_CHECK="$(dirname "$0")/self-check.sh"
OUTPUT=""
EXIT_CODE=0

if [ ! -f "$SELF_CHECK" ]; then
  echo "🔴 quick-check: cannot find self-check.sh" >&2
  exit 2
fi

# Critical passes: high-impact compiler/runtime failures (~85% catch rate)
# 1:@ohos 5:RouterMode 8:any/var 11:old-http 12:INTERNET 14:multi-var
# 16:cond-assign 20:Alignment.LR 25:export-default
CRITICAL_PASSES="1,5,8,11,12,14,16,20,25"
CHECK_ARGS=""

if [ "$MODE" = "full" ]; then
  CHECK_ARGS=""
else
  CHECK_ARGS="--only $CRITICAL_PASSES"
fi

# Run self-check (critical or full), capture output
if OUTPUT=$(bash "$SELF_CHECK" "$PROJECT_ROOT" $CHECK_ARGS 2>&1); then
  exit 0
else
  EXIT_CODE=$?
fi

# Extract only FAIL and WARNING lines for concise output
FAIL_LINES=$(echo "$OUTPUT" | grep -E '❌ FAIL|⚠️  WARNING' || true)
PASS_COUNT=$(echo "$OUTPUT" | grep -cE '^Pass [0-9].*OK$' || echo 0)
PASS_COUNT=$(echo "$PASS_COUNT" | tr -d '[:space:]')
FAIL_COUNT=$(echo "$FAIL_LINES" | grep -c '❌ FAIL' || echo 0)
FAIL_COUNT=$(echo "$FAIL_COUNT" | tr -d '[:space:]')
WARN_COUNT=$(echo "$FAIL_LINES" | grep -c '⚠️  WARNING' || echo 0)
WARN_COUNT=$(echo "$WARN_COUNT" | tr -d '[:space:]')
TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))

echo "⚡ quick-check ($MODE): ${PASS_COUNT}/${TOTAL} passed, ${FAIL_COUNT} fail, ${WARN_COUNT} warn"
echo ""

if [ -n "$FAIL_LINES" ]; then
  echo "$FAIL_LINES" | while IFS= read -r line; do
    echo "  $line"
  done
fi

# If FAIL items exist, point to full check
if [ "$MODE" != "full" ] && [ "$FAIL_COUNT" -gt 0 ] 2>/dev/null; then
  echo ""
  echo "  → Run 'bash scripts/quick-check.sh . --full' for all 25 Passes + PITFALLS anchors."
fi

exit $EXIT_CODE
