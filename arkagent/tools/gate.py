"""ArkAgent gate pipeline tools — checkpoint file-based enforcement.

Mirrors the harmonyos-arkts skill's 4-step hard-gate pipeline:
  0. gate_scan  — scan project structure → .arkts-check/00-scan.json
  1. (manual)   — user writes code
  2. gate_check — run validation → .arkts-check/02-checked.json
  3. (output)   — report in conversation

Checkpoint files use the same JSON schema as self-check.sh for
compatibility with existing Claude Code hooks.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastmcp import Context

from ..server import mcp

CHECKPOINT_DIR = ".arkts-check"

CHECKPOINT_SCHEMA = {
    "timestamp": "",        # ISO 8601
    "step": 0,              # 0=scan, 2=checked
    "project_root": "",     # absolute path
    "errors": 0,            # error count
    "warnings": 0,          # warning count
    "files_scanned": 0,     # number of .ets/.ts files found
    "status": "PASS",       # PASS, FAIL, WARN
    "checks": [],           # list of {pass_id, name, status, message}
}


def _checkpoint_path(project_root: str) -> Path:
    return Path(project_root) / CHECKPOINT_DIR


def _scan_project(project_root: Path) -> dict:
    """Scan project structure: count files, detect architecture, find module.json5."""
    ets_files = list(project_root.rglob("*.ets")) + list(project_root.rglob("*.ts"))
    entry_src = project_root / "entry" / "src" / "main"
    module_json = entry_src / "module.json5"

    info = {
        "ets_count": len(ets_files),
        "has_entry_module": entry_src.exists(),
        "has_module_json5": module_json.exists(),
        "has_common_layer": (project_root / "common").exists(),
        "has_features_layer": (project_root / "features").exists(),
        "has_products_layer": (project_root / "products").exists(),
        "directories": [
            str(d.relative_to(project_root))
            for d in sorted(project_root.iterdir())
            if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__"
        ],
    }

    # Three-layer architecture detection
    if info["has_common_layer"] and info["has_features_layer"] and info["has_products_layer"]:
        info["architecture"] = "three-layer (common/features/products)"
    elif info["has_entry_module"]:
        info["architecture"] = "single-module (entry)"
    else:
        info["architecture"] = "minimal (no standard structure detected)"

    return info


@mcp.tool()
async def arkagent_gate_scan(
    project_root: str = ".",
    context: Context | None = None,
) -> str:
    """Step 0: Scan project structure and write gate checkpoint.

    Must be called BEFORE writing any .ets files. Creates .arkts-check/00-scan.json.
    The checkpoint file is checked by Claude Code hooks to enforce the pipeline.

    Args:
        project_root: Project root directory (default: ".")
    """
    root = Path(project_root).resolve()
    ck_dir = _checkpoint_path(str(root))
    ck_dir.mkdir(parents=True, exist_ok=True)

    info = _scan_project(root)

    # Write scan checkpoint
    checkpoint = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": 0,
        "project_root": str(root),
        "errors": 0,
        "warnings": 0,
        "files_scanned": info["ets_count"],
        "status": "PASS",
        "architecture": info["architecture"],
        "checks": [
            {"pass_id": 0, "name": "project_structure", "status": "PASS",
             "message": f"Architecture: {info['architecture']}"},
        ],
    }

    ck_file = ck_dir / "00-scan.json"
    ck_file.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"## Gate Step 0: Project Scan — ✅ PASS",
        f"",
        f"**Project**: `{root}`",
        f"**Architecture**: {info['architecture']}",
        f"**Files**: {info['ets_count']} .ets/.ts file(s)",
        f"**Entry module**: {'✅' if info['has_entry_module'] else '❌'}",
        f"**module.json5**: {'✅' if info['has_module_json5'] else '❌'}",
        f"",
        f"**Directories**: {', '.join(info['directories'][:10])}",
        f"",
        f"**Checkpoint**: `{ck_file}`",
        f"",
        f"*Next: Write your .ets files, then run `arkagent_gate_check()` for Step 2 validation.*",
    ]
    return "\n".join(lines)


@mcp.tool()
async def arkagent_gate_check(
    project_root: str = ".",
    step: int = 2,
    context: Context | None = None,
) -> str:
    """Step 2: Run full validation and write checkpoint file.

    Runs all 25 syntax checks + import validation + state management audit.
    Writes .arkts-check/02-checked.json with structured results.
    Compatible with self-check.sh checkpoint format.

    Args:
        project_root: Project root directory (default: ".")
        step: Which gate step (default 2, the validation step)
    """
    root = Path(project_root).resolve()
    ck_dir = _checkpoint_path(str(root))

    # Ensure Step 0 checkpoint exists
    scan_ck = ck_dir / "00-scan.json"
    if not scan_ck.exists():
        return (
            "❌ **Gate BLOCKED**: Step 0 not completed.\n\n"
            "Run `arkagent_gate_scan()` first to scan the project structure.\n"
            "The PreToolUse hook will also block .ets file writes until Step 0 is done."
        )

    # Run all validation checks
    all_issues: list[dict] = []

    # Import check_syntax scanner logic
    from .validation.check_syntax import _scan_file, CHECKS

    ets_files = list(root.rglob("*.ets")) + list(root.rglob("*.ts"))
    ets_files = ets_files[:50]  # Cap at 50 for performance

    for fpath in ets_files:
        issues = _scan_file(fpath)
        all_issues.extend(issues)

    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warns = [i for i in all_issues if i["severity"] == "WARN"]
    infos = [i for i in all_issues if i["severity"] == "INFO"]

    # Group by pass
    pass_summaries = {}
    for issue in all_issues:
        pid = issue["pass"]
        if pid not in pass_summaries:
            pass_summaries[pid] = {"count": 0, "name": issue["check"], "status": "PASS"}
        pass_summaries[pid]["count"] += 1
        if issue["severity"] == "ERROR":
            pass_summaries[pid]["status"] = "FAIL"
        elif issue["severity"] == "WARN" and pass_summaries[pid]["status"] != "FAIL":
            pass_summaries[pid]["status"] = "WARN"

    # Build checkpoint
    status = "FAIL" if errors else ("WARN" if warns else "PASS")
    checkpoint = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "project_root": str(root),
        "errors": len(errors),
        "warnings": len(warns),
        "infos": len(infos),
        "files_scanned": len(ets_files),
        "status": status,
        "checks": [
            {
                "pass_id": pid,
                "name": info["name"],
                "status": info["status"],
                "count": info["count"],
            }
            for pid, info in sorted(pass_summaries.items())
        ],
    }

    ck_file = ck_dir / "02-checked.json"
    ck_file.write_text(json.dumps(checkpoint, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build report
    emoji = "❌" if status == "FAIL" else ("⚠️" if status == "WARN" else "✅")
    lines = [
        f"## Gate Step {step}: Validation — {emoji} {status}",
        f"",
        f"**Files**: {len(ets_files)} scanned | **Errors**: {len(errors)} | **Warns**: {len(warns)} | **Infos**: {len(infos)}",
        f"**Checkpoint**: `{ck_file}`",
        f"",
        "| Pass | Check | Status | Count |",
        "|------|-------|--------|-------|",
    ]
    for pid, info in sorted(pass_summaries.items()):
        lines.append(f"| {pid} | {info['name']} | {info['status']} | {info['count']} |")

    if errors:
        lines.append(f"\n### Errors ({len(errors)})")
        for e in errors[:10]:
            lines.append(f"- **[{e['check']}]** `{e['file']}:{e['line']}` — {e['message']}")
            lines.append(f"  ```{e['code']}```")
        if len(errors) > 10:
            lines.append(f"\n*...and {len(errors) - 10} more error(s)*")

    if status != "PASS":
        lines.append(f"\n---")
        lines.append(f"**Fix the issues above, then re-run `arkagent_gate_check()`**")

    return "\n".join(lines)[:6000]


@mcp.tool()
async def arkagent_gate_status(
    project_root: str = ".",
    context: Context | None = None,
) -> str:
    """Check current gate pipeline status.

    Reads .arkts-check/ checkpoint files and reports which steps are complete,
    with error/warning counts from the last check run.

    Args:
        project_root: Project root directory (default: ".")
    """
    root = Path(project_root).resolve()
    ck_dir = _checkpoint_path(str(root))

    lines = [
        f"## Gate Pipeline Status — `{root}`",
        "",
        "| Step | Name | Status | Details |",
        "|------|------|--------|---------|",
    ]

    steps_found = 0
    for step_id, step_name, filename in [
        (0, "Project Scan", "00-scan.json"),
        (2, "Validation", "02-checked.json"),
    ]:
        ck_file = ck_dir / filename
        if ck_file.exists():
            try:
                data = json.loads(ck_file.read_text(encoding="utf-8"))
                status = data.get("status", "?")
                errors = data.get("errors", 0)
                warns = data.get("warnings", 0)
                ts = data.get("timestamp", "")[:19]
                lines.append(
                    f"| {step_id} | {step_name} | {status} | "
                    f"{errors} error(s), {warns} warn(s) — {ts} |"
                )
                steps_found += 1
            except Exception:
                lines.append(f"| {step_id} | {step_name} | ⚠️ CORRUPT | Checkpoint file invalid |")
                steps_found += 1
        else:
            lines.append(f"| {step_id} | {step_name} | ⬚ NOT RUN | — |")

    if steps_found == 0:
        lines.append(f"\n*No checkpoints found. Run `arkagent_gate_scan()` to start.*")
    else:
        lines.append(f"\n*Run `arkagent_gate_scan()` or `arkagent_gate_check()` to advance the pipeline.*")

    return "\n".join(lines)
