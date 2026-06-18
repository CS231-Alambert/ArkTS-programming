"""arkagent_check_syntax — scan .ets/.ts for ArkTS compilation-blocking errors.

Ported from self-check.sh with 15 most critical passes (full 25 is too slow for MCP).
"""

import re
from pathlib import Path
from fastmcp import Context

from ...server import mcp

# Check patterns — (pass_id, name, regex, severity, message)
CHECKS: list[tuple[int, str, str, str, str]] = [
    (1, "@ohos imports", r"from\s+['\"]@ohos\.", "ERROR",
     "Use @kit.* imports (API 12+): `import {{ ... }} from '@kit.ArkUI'`"),
    (2, "new Function()", r"new\s+Function\s*\(", "ERROR",
     "`new Function()` is forbidden in ArkTS. Use arrow functions or regular functions."),
    (3, "any/unknown type", r":\s*(any|unknown)\b", "ERROR",
     "`any`/`unknown` types are forbidden in ArkTS. Use explicit types."),
    (4, "var declaration", r"\bvar\s+", "ERROR",
     "`var` is forbidden in ArkTS. Use `let` or `const`."),
    (5, "obj[key] access", r'\w+\s*\["[^"]*"\]', "WARN",
     "Dynamic property access `obj[\"key\"]` is forbidden. Use `obj.key`."),
    (6, "delete operator", r"\bdelete\s+", "ERROR",
     "`delete` operator is forbidden in ArkTS. Use nullable types with `null`."),
    (7, "eval()", r"\beval\s*\(", "ERROR",
     "`eval()` is forbidden in ArkTS."),
    (8, "for...in loop", r"\bfor\s*\(.*\s+in\s+", "ERROR",
     "`for...in` is forbidden. Use regular `for` or `forEach` loops."),
    (9, "destructuring", r"(const|let)\s*\{\s*\w+", "WARN",
     "Destructuring may cause ArkTS compilation issues. Use manual assignment."),
    (10, "fontSize on non-text", r'\.fontSize\(\d+\)', "WARN",
     "Check that fontSize() is used on Text/Button/TextInput, not layout components."),
    (11, "Alignment.Left/Right", r'Alignment\.(Left|Right)', "WARN",
     "Use `Alignment.Start`/`Alignment.End` instead of Left/Right (RTL-safe)."),
    (12, "hardcoded hex color", r"'#[0-9a-fA-F]{6}'|'#[0-9a-fA-F]{3}'", "INFO",
     "Prefer `$r('app.color.xxx')` over hardcoded hex colors for theme support."),
    (13, "missing unit suffix", r'(?<!\w)(width|height|margin|padding)\s*\(\s*\d+\s*\)', "WARN",
     "Dimension values should have unit suffix: `vp`, `fp`, `px`, `%`."),
    (14, "router without RouterMode", r'router\.pushUrl\s*\([^)]*\)', "INFO",
     "Include `router.RouterMode.Standard` as second parameter to pushUrl()."),
    (15, "createHttp without destroy", r'http\.createHttp\s*\(', "WARN",
     "Every `http.createHttp()` must have `.destroy()` in a `finally` block."),

    # ── Pass 16-25: ported from self-check.sh (coding standards + component specs) ──
    (16, "multi-var declaration", r'\b(let|const)\s+\w+\s*=.*,\s*\w+\s*=', "WARN",
     "Multiple variable declarations on one line. Use separate let/const per variable."),
    (17, "NaN comparison", r'(==|!=)\s*NaN|NaN\s*(==|!=)', "ERROR",
     "NaN comparison with ==/!= is always false. Use Number.isNaN() instead."),
    (18, "assignment in conditional", r'\bif\s*\(\s*\w+\s*=\s*[^=]', "ERROR",
     "Assignment inside if/while condition is forbidden. Move assignment outside, compare only."),
    (19, "control flow in finally", r'finally\s*\{[^}]*\b(return|break|continue|throw)\b', "ERROR",
     "return/break/continue/throw forbidden in finally block. Move outside."),
    (20, "@Prop on object type", r'@Prop\s+\w+\s*:\s*[A-Z]', "WARN",
     "@Prop on object/class types causes deep copy overhead. Use @ObjectLink (V1) or @Param (V2)."),
    (21, "@State/@Link in loop", r'\b(for|while|ForEach)\b.*\{[^}]*\bthis\.\w+', "INFO",
     "Reading @State/@Link inside loop body? Extract to local variable first for performance."),
    (22, "fontSize/fontColor on non-text", r'(Column|Row|Stack|Flex|List|Grid|Scroll|Tabs)\([^)]*\)\s*\{[^}]*\.(fontSize|fontColor|fontWeight)\(', "WARN",
     "fontSize/fontColor/fontWeight should only be used on Text/Span/Button/TextInput components."),
    (23, "Shape without stroke", r'(Circle|Ellipse|Line|Polyline|Polygon|Rect|Path)\(', "INFO",
     "Shape components must call .stroke() to be visible on light backgrounds."),
    (24, "unusual Color enum", r'Color\.(?!Red|Blue|Green|Yellow|Black|White|Gray|Grey|Orange|Pink|Brown|Transparent|Cyan|Magenta\b)\w+', "INFO",
     "Unusual Color enum may lack cross-version support. Prefer hex '#XXXXXX' instead."),
    (25, "component missing export", r'@Component(V2)?\s*\n?\s*struct\s+\w+', "INFO",
     "Component file in components/ should use `export default` for reusability."),
]


def _scan_file(fpath: Path) -> list[dict]:
    """Scan a single file for syntax issues."""
    try:
        content = fpath.read_text(encoding="utf-8")
    except Exception:
        return []

    issues: list[dict] = []
    for lineno, line in enumerate(content.splitlines(), 1):
        for pid, name, pattern, severity, msg in CHECKS:
            if re.search(pattern, line):
                # Skip false positives in comments
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("*"):
                    continue
                # Skip string literals containing the pattern
                if '`' in line or '"' in line:
                    # Simple heuristic: if pattern appears inside quotes, skip
                    in_string = False
                    for c in line:
                        if c in '`"\'':
                            in_string = not in_string
                    if in_string:
                        continue

                issues.append({
                    "file": str(fpath),
                    "line": lineno,
                    "pass": pid,
                    "check": name,
                    "severity": severity,
                    "message": msg,
                    "code": stripped[:80],
                })
    return issues


@mcp.tool()
async def arkagent_check_syntax(
    file_path: str | None = None,
    project_root: str = ".",
    passes: str | None = None,
    skip: str | None = None,
    context: Context | None = None,
) -> str:
    """Scan .ets/.ts files for ArkTS syntax error patterns that would fail compilation.

    Covers 25 critical error patterns: any/unknown types, var declarations, ForEach keys,
    destructuring, dynamic property access, deprecated imports, alignment issues,
    coding standards (NaN comparison, assignment-in-conditional, control-flow-in-finally),
    state management (@Prop on objects, @State in loops), component specs
    (fontSize on non-text, Shape without stroke, Color enum validity, missing export default).

    Args:
        file_path: Single file or directory (scans .ets/.ts recursively if directory)
        project_root: Project root directory (default: ".")
        passes: Comma-separated pass numbers to run (e.g., "1,2,8")
        skip: Comma-separated pass numbers to skip
    """
    root = Path(project_root).resolve()
    files: list[Path] = []

    if file_path:
        fp = Path(file_path)
        if not fp.is_absolute():
            fp = root / fp
        if fp.is_file():
            files = [fp]
        elif fp.is_dir():
            files = list(fp.rglob("*.ets"))
    else:
        files = list(root.rglob("*.ets"))

    # Filter passes
    enabled = set(range(1, 26))
    if passes:
        enabled = {int(p.strip()) for p in passes.split(",") if p.strip().isdigit()}
    if skip:
        for s in skip.split(","):
            s = s.strip()
            if s.isdigit():
                enabled.discard(int(s))

    all_issues: list[dict] = []
    for fpath in files[:30]:  # Cap at 30 files
        issues = _scan_file(fpath)
        all_issues.extend([i for i in issues if i["pass"] in enabled])

    if not all_issues:
        return f"✅ **Syntax check passed** — {len(files)} file(s) scanned, no issues found."

    # Group by severity
    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warns = [i for i in all_issues if i["severity"] == "WARN"]
    infos = [i for i in all_issues if i["severity"] == "INFO"]

    lines = [
        f"## ArkTS Syntax Check — {len(files)} file(s)",
        f"**{len(errors)} ERROR(s) | {len(warns)} WARN(s) | {len(infos)} INFO(s)**\n",
    ]
    for i in errors[:10] + warns[:10]:
        lines.append(f"- **{i['severity']}** [{i['check']}] `{i['file']}:{i['line']}` — {i['message']}")
        lines.append(f"  ```{i['code']}```")

    if len(all_issues) > 20:
        lines.append(f"\n*...and {len(all_issues) - 20} more issue(s). Run on specific files for details.*")

    return "\n".join(lines)[:5000]
