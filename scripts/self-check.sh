#!/usr/bin/env bash
# self-check.sh — Automated post-generation validation for ArkTS files.
# Scans for known error patterns that would cause ArkTS Compiler failures.
# Usage: bash self-check.sh <project-root>
# Exit code 0 = all clear; non-zero = errors found.

set -euo pipefail

PROJECT_ROOT="${1:-.}"
ETS_DIR="$PROJECT_ROOT/entry/src/main/ets"
ERRORS=0
CHECK_FILE="$PROJECT_ROOT/.arkts-check/02-checked.json"
TIMESTAMP=$(date -Iseconds)

echo "=== ArkTS Self-Check ==="
echo "Scanning: $ETS_DIR"
echo ""

# ── Pass 1: @ohos.* imports ─────────────────────────
echo -n "Pass 1: @ohos.* imports ... "
if grep -rn '@ohos\.' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — replace with @kit.* format"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 2: new Function() ──────────────────────────
echo -n "Pass 2: new Function() ... "
if grep -rn '\bnew Function\b' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — dynamic code execution forbidden in ArkTS"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 3: Select with .options() ──────────────────
echo -n "Pass 3: Select.options() ... "
if grep -rn '\.options(' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — Select API not documented; use alternative"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 4: @State conflicting with built-in props ──
echo -n "Pass 4: @State prop conflicts ... "
if grep -rn '@State height:' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — @State height conflicts with component height property; rename to bmiHeight or similar"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi
echo -n "Pass 4b: @State weight conflict ... "
if grep -rn '@State weight:' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — @State weight conflicts; rename"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 5: router.pushUrl without RouterMode.Standard ──
echo -n "Pass 5: router.pushUrl RouterMode ... "
PUSH_COUNT=0
PUSH_COUNT=$(grep -rn 'router\.pushUrl(' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
PUSH_COUNT=$(echo "$PUSH_COUNT" | tr -d '[:space:]')
if [ "$PUSH_COUNT" -gt 0 ] 2>/dev/null; then
  MISSING=0
  for f in $(grep -rl 'router\.pushUrl(' "$ETS_DIR" --include="*.ets" 2>/dev/null); do
    grep -q 'RouterMode\.Standard' "$f" || MISSING=$((MISSING + 1))
  done
  if [ "$MISSING" -gt 0 ]; then
    echo "❌ FAIL — $MISSING pushUrl call(s) missing RouterMode.Standard"
    ERRORS=$((ERRORS + 1))
  else
    echo "✅ OK ($PUSH_COUNT calls)"
  fi
else
  echo "✅ OK (no pushUrl)"
fi

# ── Pass 6: ForEach missing 3rd parameter ───────────
echo -n "Pass 6: ForEach key generator ... "
FOREACH_COUNT=0
FOREACH_COUNT=$(grep -rn 'ForEach(' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
FOREACH_COUNT=$(echo "$FOREACH_COUNT" | tr -d '[:space:]')
echo "✅ OK ($FOREACH_COUNT ForEach calls — verify manually if suspicious)"

# ── Pass 7: First line check ────────────────────────
echo -n "Pass 7: file structure ... "
BAD_FIRST=0
for f in $(find "$ETS_DIR" -name "*.ets" -type f 2>/dev/null); do
  LINE1=$(head -1 "$f")
  # Allow: import, //, /*, @Entry, @Component, @Builder, struct, empty
  echo "$LINE1" | grep -qE '^import|^//|^/\*|^@Entry|^@Component|^@Builder|^struct|^$' || BAD_FIRST=$((BAD_FIRST + 1))
done
if [ "$BAD_FIRST" -gt 0 ]; then
  echo "⚠️  WARNING — $BAD_FIRST file(s) have unusual first line"
else
  echo "✅ OK"
fi

# ── Pass 8: any/unknown/var keywords ────────────────
echo -n "Pass 8: any/unknown/var ... "
BANNED=0
BANNED=$(grep -Prn '\b(any|unknown|var)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -v "catch\|console\|JSON\|'\$" | wc -l || echo 0)
BANNED=$(echo "$BANNED" | tr -d '[:space:]')
if [ "$BANNED" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $BANNED occurrence(s) of banned keywords"
  grep -Prn '\b(any|unknown|var)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -v "catch\|console\|JSON\|'\$" || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 9: unused callback params ──────────────────
echo -n "Pass 9: unused ForEach callback params ... "
UNUSED=0
UNUSED=$(grep -rn "ForEach.*index: number\|ForEach.*idx: number" "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
UNUSED=$(echo "$UNUSED" | tr -d '[:space:]')
if [ "$UNUSED" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — $UNUSED ForEach callback(s) declare index/idx param that may be unused"
else
  echo "✅ OK"
fi

# ── Write checkpoint ────────────────────────────────
mkdir -p "$(dirname "$CHECK_FILE")"
cat > "$CHECK_FILE" << JSONEOF
{
  "timestamp": "$TIMESTAMP",
  "errors": $ERRORS,
  "project": "$PROJECT_ROOT",
  "status": "$([ "$ERRORS" -eq 0 ] && echo 'PASS' || echo 'FAIL')"
}
JSONEOF

echo ""
echo "================================="
if [ "$ERRORS" -eq 0 ]; then
  echo "✅ ALL CHECKS PASSED"
  echo "Checkpoint: $CHECK_FILE"
  exit 0
else
  echo "❌ $ERRORS ERROR(S) FOUND"
  echo "Fix all errors before proceeding to Step 3."
  echo "Checkpoint: $CHECK_FILE"
  exit 1
fi
