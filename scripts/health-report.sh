#!/usr/bin/env bash
# health-report.sh — Cross-session health analysis (Bucket-Seal pattern).
# Reads .arkts-check/history.jsonl and outputs trend summary.
# Usage: bash health-report.sh <project-root>
# When 10+ entries: auto-suggests compaction → LLM-generated health summary.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
HISTORY="$PROJECT_ROOT/.arkts-check/history.jsonl"

if [ ! -f "$HISTORY" ]; then
  echo "📊 No history found. Run self-check.sh first."
  exit 0
fi

echo "=== Project Health Report ==="
echo ""

python3 -c "
import json, sys
from datetime import datetime

entries = []
for line in open('$HISTORY'):
    try: entries.append(json.loads(line.strip()))
    except: pass

if not entries:
    print('No entries yet.')
    sys.exit(0)

total = len(entries)
passed = sum(1 for e in entries if e.get('passed'))
failed = total - passed
pass_rate = (passed / total * 100) if total > 0 else 0

print(f'Total runs:     {total}')
print(f'Passed:         {passed} ({pass_rate:.0f}%)')
print(f'Failed:         {failed} ({100-pass_rate:.0f}%)')
print()

# Trend: last 5 vs previous 5
if total >= 6:
    recent = entries[-5:]
    older = entries[-10:-5]
    recent_pass = sum(1 for e in recent if e.get('passed'))
    older_pass = sum(1 for e in older if e.get('passed'))
    trend = '📈 improving' if recent_pass > older_pass else ('📉 declining' if recent_pass < older_pass else '➡️  stable')
    print(f'Trend (last 5 vs prev 5): {older_pass}/5 → {recent_pass}/5 {trend}')
    print()

# Time span
first_ts = entries[0].get('timestamp', 'unknown')
last_ts = entries[-1].get('timestamp', 'unknown')
print(f'First run:      {first_ts}')
print(f'Last run:       {last_ts}')
print()

# Average errors when failing
fail_entries = [e for e in entries if not e.get('passed')]
if fail_entries:
    avg_errors = sum(e.get('errors', 0) for e in fail_entries) / len(fail_entries)
    print(f'Avg errors/fail: {avg_errors:.1f}')

# Bucket-Seal: suggest compaction at 10
if total >= 10:
    print()
    print('─' * 40)
    print(f'🔔 {total} entries accumulated — Bucket-Seal threshold reached.')
    print('   Consider running a health summary via LLM:')
    print(f'   \"Read {HISTORY} and summarize the top 3 recurring error patterns.\"')
" 2>/dev/null

echo ""
echo "History file: $HISTORY"
[ -f "$HISTORY" ] && echo "Entries: $(wc -l < "$HISTORY")"
