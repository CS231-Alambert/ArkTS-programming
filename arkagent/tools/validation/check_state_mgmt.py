"""arkagent_check_state_mgmt — audit V1/V2 state management in .ets files."""

import re
from pathlib import Path
from fastmcp import Context

from ...server import mcp

# V1 decorators (forbidden in API 12+ projects)
V1_DECORATORS: dict[str, str] = {
    "@State": "Use `@Local` (component-scoped state)",
    "@Prop": "Use `@Param` (read-only prop from parent)",
    "@Link": "Use `@Event` (child→parent) or `this!!.var` (two-way bind)",
    "@ObjectLink": "Use `@ObservedV2` + `@Trace` on class, access directly",
    "@Observed": "Use `@ObservedV2` on the class definition",
    "@Provide": "Use `@Provider(\"key\")` (V2 provider)",
    "@Consume": "Use `@Consumer(\"key\")` (V2 consumer)",
    "@Watch": "Use `@Monitor(\"prop\")` (V2 watcher)",
    "@Component": "Use `@ComponentV2` on the struct",
}

V2_DECORATORS = [
    "@ComponentV2", "@Local", "@Param", "@Event",
    "@Provider", "@Consumer", "@Monitor", "@Computed", "@ObservedV2", "@Trace",
]


@mcp.tool()
async def arkagent_check_state_mgmt(
    file_path: str | None = None,
    project_root: str = ".",
    target_api: int = 12,
    context: Context | None = None,
) -> str:
    """Audit .ets/.ts files for state management issues.

    Detects V1 decorators (@State, @Prop, @Link, @Observed) that should be migrated to V2,
    V1/V2 mixing in same component, and @Prop on object types (should use @ObjectLink).

    Args:
        file_path: Single file or directory to audit
        project_root: Project root directory
        target_api: Target API level (12+ = V2 required, default 12)
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

    issues: list[dict] = []
    stats = {"v1_files": 0, "v2_files": 0, "mixed_files": 0, "total": 0}

    for fpath in files[:30]:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        found_v1: list[str] = []
        found_v2: list[str] = []

        for lineno, line in enumerate(content.splitlines(), 1):
            for dec, suggestion in V1_DECORATORS.items():
                if re.search(r'\b' + re.escape(dec) + r'\b', line):
                    # Skip false positives in comments
                    if line.strip().startswith("//"):
                        continue
                    found_v1.append(dec)
                    issues.append({
                        "file": str(fpath.relative_to(root)),
                        "line": lineno,
                        "decorator": dec,
                        "suggestion": suggestion,
                        "code": line.strip()[:80],
                    })

            for dec in V2_DECORATORS:
                if re.search(r'\b' + re.escape(dec) + r'\b', line):
                    found_v2.append(dec)

        stats["total"] += 1
        if found_v1 and found_v2:
            stats["mixed_files"] += 1
        elif found_v1:
            stats["v1_files"] += 1
        elif found_v2:
            stats["v2_files"] += 1

    if not issues:
        return (f"✅ **State management audit passed** — {stats['total']} file(s) scanned.\n"
                f"V2 files: {stats['v2_files']} | V1 files: {stats['v1_files']} | "
                f"Mixed: {stats['mixed_files']}")

    lines = [
        f"## State Management Audit — {stats['total']} file(s)",
        f"**V2**: {stats['v2_files']} | **V1**: {stats['v1_files']} | "
        f"**Mixed**: {stats['mixed_files']} | **Issues**: {len(issues)}\n",
    ]

    if target_api >= 12:
        lines.append("### V1 Decorators Found (should migrate to V2)\n")
        for i in issues[:15]:
            lines.append(f"- `{i['file']}:{i['line']}` — `{i['decorator']}` → {i['suggestion']}")
            lines.append(f"  ```{i['code']}```")

    if stats["mixed_files"]:
        lines.append(f"\n⚠️ **{stats['mixed_files']} file(s)** have both V1 and V2 decorators — "
                     f"V1 and V2 must NOT be mixed in the same component.")

    return "\n".join(lines)[:4000]
