"""arkagent_validate_imports — check import path correctness."""

import re
from pathlib import Path
from fastmcp import Context

from ...server import mcp, QueryIndex

# Known correct import paths (API 12+)
CORRECT_IMPORTS: dict[str, str] = {
    "router": "@kit.ArkUI",
    "window": "@kit.ArkUI",
    "http": "@kit.NetworkKit",
    "preferences": "@kit.ArkData",
    "UIAbility": "@kit.AbilityKit",
    "Want": "@kit.AbilityKit",
    "abilityAccessCtrl": "@kit.AbilityKit",
    "Permissions": "@kit.AbilityKit",
    "fileIo": "@kit.CoreFileKit",
    "camera": "@kit.CameraKit",
    "sensor": "@kit.SensorServiceKit",
    "media": "@kit.MediaKit",
    "notificationManager": "@kit.NotificationKit",
    "ble": "@kit.ConnectivityKit",
    "hilog": "@kit.PerformanceAnalysisKit",
    "BusinessError": "@kit.BasicServicesKit",
    "webview": "@kit.ArkUI",
}

# Deprecated import patterns
DEPRECATED: dict[str, str] = {
    "@ohos.router": "@kit.ArkUI",
    "@ohos.net.http": "@kit.NetworkKit",
    "@ohos.data.preferences": "@kit.ArkData",
    "@ohos.app.ability.UIAbility": "@kit.AbilityKit",
    "@ohos.window": "@kit.ArkUI",
    "@ohos.file.fs": "@kit.CoreFileKit",
    "@ohos.multimedia.media": "@kit.MediaKit",
    "@ohos.multimedia.camera": "@kit.CameraKit",
}


@mcp.tool()
async def arkagent_validate_imports(
    file_path: str | None = None,
    project_root: str = ".",
    context: Context | None = None,
) -> str:
    """Scan .ets/.ts files for import path violations.

    Checks: @ohos.* imports that should be @kit.* (API 12+),
    known APIs imported from wrong modules, deprecated path patterns.

    Args:
        file_path: Single .ets/.ts file or directory to scan (recursive if directory)
        project_root: Project root directory for context (default: ".")
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
            files = list(fp.rglob("*.ets")) + list(fp.rglob("*.ts"))
    else:
        # Scan entire project
        files = list(root.rglob("*.ets")) + list(root.rglob("*.ts"))

    violations: list[dict] = []
    for fpath in files[:50]:  # Cap at 50 files
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        for lineno, line in enumerate(content.splitlines(), 1):
            # Check for deprecated @ohos imports
            for old, new in DEPRECATED.items():
                if old in line:
                    violations.append({
                        "file": str(fpath.relative_to(root)),
                        "line": lineno,
                        "issue": f"Deprecated import: `{old}` → use `{new}`",
                        "severity": "ERROR",
                    })

            # Check for wrong module imports
            import_m = re.match(r"import\s*\{([^}]+)\}\s*from\s*['\"]([^'\"]+)['\"]", line)
            if import_m:
                names = [n.strip().split()[-1] for n in "".join(import_m.groups()).split(",")]
                mod = import_m.group(2)
                for name in names:
                    if name in CORRECT_IMPORTS and CORRECT_IMPORTS[name] not in mod:
                        # Only flag if it's clearly wrong (not just a superset)
                        if "ohos" in mod.lower() and "kit" not in mod.lower():
                            violations.append({
                                "file": str(fpath.relative_to(root)),
                                "line": lineno,
                                "issue": f"`{name}` imported from `{mod}` — should be `{CORRECT_IMPORTS[name]}`",
                                "severity": "ERROR",
                            })

    if not violations:
        return f"✅ **Import validation passed** — {len(files)} file(s) scanned, no violations found."

    errors = [v for v in violations if v["severity"] == "ERROR"]
    warnings = [v for v in violations if v["severity"] == "WARN"]

    lines = [
        f"## Import Validation — {len(files)} file(s) scanned",
        f"**{len(errors)} error(s), {len(warnings)} warning(s)**\n",
    ]
    for v in violations[:20]:
        lines.append(f"- **{v['severity']}** `{v['file']}:{v['line']}` — {v['issue']}")

    return "\n".join(lines)[:4000]
