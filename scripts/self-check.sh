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

# ── Pass 10: localhost/127.0.0.1 in HTTP URLs ──────────
echo -n "Pass 10: localhost in HTTP URLs ... "
LOCALHOST_COUNT=0
LOCALHOST_COUNT=$(grep -Prn "(localhost|127\.0\.0\.1)" "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
LOCALHOST_COUNT=$(echo "$LOCALHOST_COUNT" | tr -d '[:space:]')
if [ "$LOCALHOST_COUNT" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — $LOCALHOST_COUNT occurrence(s) of localhost/127.0.0.1 found"
  echo "  Emulator cannot reach localhost; use your machine's LAN IP with --host flag on json-server"
  grep -Prn "(localhost|127\.0\.0\.1)" "$ETS_DIR" --include="*.ets" 2>/dev/null || true
else
  echo "✅ OK"
fi

# ── Pass 11: @ohos.net.http old imports ─────────────
echo -n "Pass 11: @ohos.net.http imports ... "
if grep -rn '@ohos\.net\.http' "$ETS_DIR" --include="*.ets" 2>/dev/null; then
  echo "❌ FAIL — replace with import { http } from '@kit.NetworkKit'"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 12: http usage without INTERNET permission ──
echo -n "Pass 12: http without INTERNET permission ... "
HTTP_USAGE=0
HTTP_USAGE=$(grep -rn 'http\.createHttp\|from.*@kit\.NetworkKit' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
HTTP_USAGE=$(echo "$HTTP_USAGE" | tr -d '[:space:]')
if [ "$HTTP_USAGE" -gt 0 ] 2>/dev/null; then
  MODULE_JSON="$PROJECT_ROOT/entry/src/main/module.json5"
  if [ -f "$MODULE_JSON" ]; then
    if grep -q 'ohos\.permission\.INTERNET' "$MODULE_JSON" 2>/dev/null; then
      echo "✅ OK (http used, permission granted)"
    else
      echo "❌ FAIL — http.createHttp used but ohos.permission.INTERNET not declared in module.json5"
      ERRORS=$((ERRORS + 1))
    fi
  else
    echo "⚠️  WARNING — module.json5 not found, cannot verify INTERNET permission"
  fi
else
  echo "✅ OK (no http usage)"
fi

# ── Pass 13: displayPriority with decimal ────────────
echo -n "Pass 13: displayPriority decimal ... "
DP_DECIMAL=0
DP_DECIMAL=$(grep -Prn 'displayPriority\(\s*\d+\.\d+' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
DP_DECIMAL=$(echo "$DP_DECIMAL" | tr -d '[:space:]')
if [ "$DP_DECIMAL" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — $DP_DECIMAL displayPriority() call(s) use decimal values"
  echo "  [x, x+1) interval is treated as same priority; use integers instead"
  grep -Prn 'displayPriority\(\s*\d+\.\d+' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
else
  echo "✅ OK"
fi

# ── Pass 14: multiple variable declarations on one line ──
echo -n "Pass 14: multi-variable declarations ... "
MULTI_VAR=0
MULTI_VAR=$(grep -Prn '\b(let|const)\s+\w+\s*=.*,\s*\w+\s*=' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -v '//' | wc -l || echo 0)
MULTI_VAR=$(echo "$MULTI_VAR" | tr -d '[:space:]')
if [ "$MULTI_VAR" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $MULTI_VAR occurrence(s) of multiple variables on one line"
  echo "  → 编程规范-要求级: 每条语句只声明一个变量"
  echo "  → 修复: 拆分为独立 let/const 声明"
  grep -Prn '\b(let|const)\s+\w+\s*=.*,\s*\w+\s*=' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -v '//' || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 15: NaN compared with == / != ────────────────
echo -n "Pass 15: NaN == / != comparison ... "
NAN_CMP=0
NAN_CMP=$(grep -Prn '(==|!=)\s*NaN|NaN\s*(==|!=)' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
NAN_CMP=$(echo "$NAN_CMP" | tr -d '[:space:]')
if [ "$NAN_CMP" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $NAN_CMP occurrence(s) of NaN ==/!= comparison"
  echo "  → 编程规范-要求级: NaN 判断必须使用 Number.isNaN()"
  echo "  → 修复: 将 x == NaN 改为 Number.isNaN(x)"
  grep -Prn '(==|!=)\s*NaN|NaN\s*(==|!=)' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 16: assignment in conditional expression ──────
echo -n "Pass 16: assignment in conditionals ... "
COND_ASSIGN=0
COND_ASSIGN=$(grep -Prn '\bif\s*\(\s*\w+\s*=\s*[^=]' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
COND_ASSIGN=$(echo "$COND_ASSIGN" | tr -d '[:space:]')
if [ "$COND_ASSIGN" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $COND_ASSIGN occurrence(s) of assignment inside if/while condition"
  echo "  → 编程规范-要求级: 控制性条件表达式内禁止赋值"
  echo "  → 修复: 将赋值移到条件外，条件内只做比较"
  grep -Prn '\bif\s*\(\s*\w+\s*=\s*[^=]' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 17: return/break/continue/throw in finally ────
echo -n "Pass 17: return/break/continue/throw in finally ... "
FINALLY_BAD=0
FINALLY_BAD=$(grep -Prn 'finally\s*\{[^}]*\b(return|break|continue|throw)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
FINALLY_BAD=$(echo "$FINALLY_BAD" | tr -d '[:space:]')
if [ "$FINALLY_BAD" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $FINALLY_BAD occurrence(s) of control-flow in finally block"
  echo "  → 编程规范-要求级: finally 代码块内禁止 return/break/continue/throw"
  echo "  → 修复: 将控制流语句移到 finally 外部"
  grep -Prn 'finally\s*\{[^}]*\b(return|break|continue|throw)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 18: @Prop on object/class types (use @ObjectLink) ──
echo -n "Pass 18: @Prop on object types ... "
PROP_OBJ=0
PROP_OBJ=$(grep -Prn '@Prop\s+\w+\s*:\s*[A-Z]' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
PROP_OBJ=$(echo "$PROP_OBJ" | tr -d '[:space:]')
if [ "$PROP_OBJ" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — $PROP_OBJ @Prop declaration(s) on object/class types"
  echo "  → CodeLinter @performance: 使用 @ObjectLink 替代 @Prop 避免深拷贝"
  echo "  → 适用条件: 子组件不需要本地修改状态变量值时"
  grep -Prn '@Prop\s+\w+\s*:\s*[A-Z]' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
else
  echo "✅ OK"
fi

# ── Pass 19: fontSize/fontColor/fontWeight on non-text ──
echo -n "Pass 19: fontSize on non-text containers ... "
FONT_MISUSE=0
FONT_MISUSE=$(grep -Prn '(Column|Row|Stack|Flex|List|Grid|Scroll|Tabs)\([^)]*\)\s*\{[^}]*\.(fontSize|fontColor|fontWeight)\(' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
FONT_MISUSE=$(echo "$FONT_MISUSE" | tr -d '[:space:]')
if [ "$FONT_MISUSE" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — possible fontSize/fontColor/fontWeight on non-text container"
  echo "  → fontSize/fontColor/fontWeight 只用于 Text/Span/Button/TextInput 等文本组件"
else
  echo "✅ OK"
fi

# ── Pass 20: Alignment.Left/Right instead of Start/End ──
echo -n "Pass 20: Alignment.Left/Right ... "
ALIGN_LR=0
ALIGN_LR=$(grep -Prn 'Alignment\.(Left|Right)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
ALIGN_LR=$(echo "$ALIGN_LR" | tr -d '[:space:]')
if [ "$ALIGN_LR" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $ALIGN_LR occurrence(s) of Alignment.Left/Right"
  echo "  → 鸿蒙使用国际化的 Start/End 语义，禁止 Left/Right"
  echo "  → 修复: Alignment.Start / Alignment.End"
  grep -Prn 'Alignment\.(Left|Right)\b' "$ETS_DIR" --include="*.ets" 2>/dev/null || true
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK"
fi

# ── Pass 21: Shape without .stroke() ───────────────────
echo -n "Pass 21: Shape components without .stroke() ... "
SHAPE_NO_STROKE=0
for shape in Circle Ellipse Line Polyline Polygon Rect Path; do
  SHAPE_FILES=$(grep -rl "$shape(" "$ETS_DIR" --include="*.ets" 2>/dev/null || true)
  if [ -n "$SHAPE_FILES" ]; then
    for sf in $SHAPE_FILES; do
      # Check if .stroke() appears anywhere in the file after the shape
      grep -q '\.stroke(' "$sf" 2>/dev/null || SHAPE_NO_STROKE=$((SHAPE_NO_STROKE + 1))
    done
  fi
done
if [ "$SHAPE_NO_STROKE" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — $SHAPE_NO_STROKE file(s) use Shape components but may lack .stroke()"
  echo "  → Shape 必须在代码中显式调用 .stroke() 才会在白色背景上可见"
else
  echo "✅ OK"
fi

# ── Pass 22: @State outside struct ─────────────────────
echo -n "Pass 22: @State outside struct ... "
STATE_OUTSIDE=0
STATE_OUTSIDE=$(grep -rn '@State' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -v 'struct' | wc -l || echo 0)
STATE_OUTSIDE=$(echo "$STATE_OUTSIDE" | tr -d '[:space:]')
if [ "$STATE_OUTSIDE" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — @State declarations possibly outside struct body"
  echo "  → @State 必须写在 @Component struct 内部"
else
  echo "✅ OK"
fi

# ── Pass 23: @State/@Link read inside loop body ────────
echo -n "Pass 23: @State/@Link read in loops ... "
LOOP_STATE=0
LOOP_STATE=$(grep -Prn '\b(for|while|ForEach)\b.*\{[^}]*\bthis\.\w+' "$ETS_DIR" --include="*.ets" 2>/dev/null | wc -l || echo 0)
LOOP_STATE=$(echo "$LOOP_STATE" | tr -d '[:space:]')
if [ "$LOOP_STATE" -gt 0 ] 2>/dev/null; then
  echo "  ($LOOP_STATE loop block(s) — verify @State reads are extracted to local vars)"
  echo "  → 最佳实践: 循环中频繁读取 @State 前先提取为局部变量，减少响应式查询开销"
else
  echo "✅ OK"
fi

# ── Pass 24: Color.Xxx enumeration that may not exist ───
echo -n "Pass 24: Color enum validity ... "
COLOR_BAD=0
COLOR_BAD=$(grep -Prn 'Color\.\w+' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -vE 'Color\.(Red|Blue|Green|Yellow|Black|White|Gray|Grey|Orange|Pink|Brown|Transparent|Cyan|Magenta)$' | wc -l || echo 0)
COLOR_BAD=$(echo "$COLOR_BAD" | tr -d '[:space:]')
if [ "$COLOR_BAD" -gt 0 ] 2>/dev/null; then
  echo "⚠️  WARNING — unusual Color enum(s) found"
  echo "  → 优先使用十六进制 '#XXXXXX' 替代 Color.Xxx 枚举（跨版本兼容性更好）"
  grep -Prn 'Color\.\w+' "$ETS_DIR" --include="*.ets" 2>/dev/null | grep -vE 'Color\.(Red|Blue|Green|Yellow|Black|White|Gray|Grey|Orange|Pink|Brown|Transparent|Cyan|Magenta)$' || true
else
  echo "✅ OK"
fi

# ── Pass 25: component files without export default ────
echo -n "Pass 25: components/ export default ... "
COMP_DIR="$PROJECT_ROOT/entry/src/main/ets/components"
MISSING_EXPORT=0
if [ -d "$COMP_DIR" ]; then
  for cf in $(find "$COMP_DIR" -name "*.ets" -type f 2>/dev/null); do
    grep -q 'export default' "$cf" 2>/dev/null || MISSING_EXPORT=$((MISSING_EXPORT + 1))
  done
fi
if [ "$MISSING_EXPORT" -gt 0 ] 2>/dev/null; then
  echo "❌ FAIL — $MISSING_EXPORT components/ file(s) missing export default"
  echo "  → components/ 下的可复用组件必须用 export default 导出"
  ERRORS=$((ERRORS + 1))
else
  echo "✅ OK ($(find "$COMP_DIR" -name '*.ets' -type f 2>/dev/null | wc -l) files)"
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
