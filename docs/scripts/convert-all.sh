#!/bin/bash
# Batch convert Huawei doc HTML → clean Markdown for knowledge base
# Usage: bash convert-all.sh [--kit arkweb|arkts] [--resume]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
HTML_DIR="${1:-/mnt/c/Users/24559/Desktop/arkweb-docs}"
KIT="${2:-arkweb}"
OUT_DIR="$SKILL_DIR/$KIT"

mkdir -p "$OUT_DIR"
mkdir -p /tmp/arkweb-cleaned

echo "=== Phase 1: Extract content from HTML ==="
python3 "$SCRIPT_DIR/clean-markdown.py" --batch "$HTML_DIR" --out /tmp/arkweb-cleaned

echo ""
echo "=== Phase 2: Convert cleaned HTML → Markdown ==="
count=0
for f in /tmp/arkweb-cleaned/*.cleaned.html; do
  base=$(basename "$f" .cleaned.html)
  # Remove Chinese prefix for cleaner filenames
  slug=$(echo "$base" | sed 's/^[^-]*-//')
  out="$OUT_DIR/${slug}.md"

  echo "  → $slug"
  markitdown "$f" -o "$out" 2>/dev/null

  # Post-process: normalize code block language tags
  if [ -f "$out" ]; then
    # Replace JSON code blocks with typescript where appropriate
    sed -i 's/```json$/```typescript/g' "$out"
    count=$((count + 1))
  fi
done

echo ""
echo "=== Phase 3: Quality check ==="
for f in "$OUT_DIR"/*.md; do
  lines=$(wc -l < "$f")
  headings=$(grep -c '^## ' "$f" 2>/dev/null || echo 0)
  codes=$(grep -c '```' "$f" 2>/dev/null || echo 0)

  status="✅"
  if [ "$lines" -lt 50 ]; then
    status="⚠️ SHORT"
  fi
  if [ "$headings" -eq 0 ]; then
    status="⚠️ NO-H2"
  fi

  printf "  %s %4d lines, %d headings, %d code blocks  %s\n" \
    "$status" "$lines" "$headings" "$((codes / 2))" "$(basename "$f")"
done

echo ""
echo "✅ Converted $count files → $OUT_DIR/"
