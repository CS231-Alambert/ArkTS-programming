#!/usr/bin/env bash
# install-hooks.sh — One-command Hard Gate installation.
# Adds PreToolUse (block Write before Step 0) + PostToolUse (silent auto-check)
# to ~/.claude/settings.json.
# Usage: bash scripts/install-hooks.sh
# Safe to run multiple times — merges, doesn't overwrite.

set -euo pipefail

SETTINGS_FILE="$HOME/.claude/settings.json"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 Installing hard-gate hooks"
echo "   Skill dir: $SKILL_DIR"
echo "   Target: $SETTINGS_FILE"
echo ""

# ── Build hook config ─────────────────────────────────
HOOK_PRE=$(cat << PREEOF
      {
        "matcher": "Write",
        "command": "test -f \"\${PROJECT_DIR}/.arkts-check/00-scan.json\" || (printf '\\n🔴 HARD GATE BLOCKED: Step 0 not run.\\n→ Run: bash ${SKILL_DIR}/scripts/scaffold.sh <ProjectName> <com.example.app>\\n' >&2 && exit 2)",
        "description": "Block .ets writes before Step 0 scan"
      }
PREEOF
)

HOOK_POST=$(cat << POSTEOF
      {
        "matcher": "Write",
        "command": "if echo \"\${FILE_PATH}\" | grep -q '\\.ets\$'; then cd \"\${PROJECT_DIR}\" && bash \"${SKILL_DIR}/scripts/quick-check.sh\" . 2>&1 || true; fi",
        "description": "Silent auto-check after .ets writes (OpenHuman subconscious loop pattern)"
      }
POSTEOF
)

# ── Read existing settings ────────────────────────────
if [ -f "$SETTINGS_FILE" ]; then
  echo "   Existing settings.json found — merging..."
  python3 -c "
import json, sys, os

with open('$SETTINGS_FILE') as f:
    settings = json.load(f)

hooks = settings.setdefault('hooks', {})
pre = hooks.setdefault('PreToolUse', [])
post = hooks.setdefault('PostToolUse', [])

# Check if our hooks are already installed
pre_cmd = '00-scan.json'
post_cmd = 'quick-check.sh'
already_pre = any(pre_cmd in json.dumps(h) for h in pre)
already_post = any(post_cmd in json.dumps(h) for h in post)

if already_pre and already_post:
    print('   ✅ Hard-gate hooks already installed. Nothing to do.')
    sys.exit(0)

# Remove any existing gate hooks (to avoid duplicates on re-run)
pre[:] = [h for h in pre if pre_cmd not in json.dumps(h)]
post[:] = [h for h in post if post_cmd not in json.dumps(h)]

# Add our hooks
pre.append($HOOK_PRE)
post.append($HOOK_POST)
settings['hooks'] = hooks

with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print('   ✅ Hard-gate hooks installed.')
" 2>&1
else
  echo "   Creating new settings.json..."
  python3 -c "
import json, os
settings = {
    'hooks': {
        'PreToolUse': [$HOOK_PRE],
        'PostToolUse': [$HOOK_POST]
    }
}
os.makedirs(os.path.dirname('$SETTINGS_FILE'), exist_ok=True)
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)
print('   ✅ settings.json created with hard-gate hooks.')
" 2>&1
fi

echo ""
echo "========================================="
echo "  Hard Gate hooks installed."
echo "  PreToolUse:  Block .ets writes before Step 0"
echo "  PostToolUse: Auto quick-check after .ets edits"
echo ""
echo "  To verify: cat $SETTINGS_FILE"
echo "  To remove: Remove the hook entries from $SETTINGS_FILE"
echo "========================================="
