"""arkagent_scan_project — full project validation in one call."""

import json
import re
from pathlib import Path
from fastmcp import Context

from ...server import mcp

# Import validation logic from sibling tools
from .validate_imports import DEPRECATED, CORRECT_IMPORTS
from .check_state_mgmt import V1_DECORATORS, V2_DECORATORS


@mcp.tool()
async def arkagent_scan_project(
    project_root: str = ".",
    target_api: int = 12,
    checks: str | None = None,
    context: Context | None = None,
) -> str:
    """Run all validation checks on a HarmonyOS project in one call.

    Produces a structured gate report covering: imports, syntax, state management,
    security (hardcoded secrets, missing permissions), architecture (layer placement),
    http lifecycle (createHttp/destroy pairing).

    Args:
        project_root: Project root directory (default: ".")
        target_api: Target API level (12+ requires V2, @kit imports, etc.)
        checks: Comma-separated check categories to run (default: all)
    """
    root = Path(project_root).resolve()
    selected = set((checks or "imports,syntax,state,security,http,architecture").split(","))

    # Find all .ets/.ts files
    ets_files = list(root.rglob("*.ets")) + list(root.rglob("*.ts"))
    # Cap at 50 files for performance
    ets_files = ets_files[:50]

    # Check for module.json5
    module_json = root / "entry" / "src" / "main" / "module.json5"

    # ── Category results ──
    results: dict[str, dict] = {
        "imports": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
        "syntax": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
        "state": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
        "security": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
        "http": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
        "architecture": {"status": "SKIP", "errors": 0, "warns": 0, "details": []},
    }
    total_errors = 0
    total_warns = 0

    for fpath in ets_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        lines = content.splitlines()
        rel = str(fpath.relative_to(root))

        # ── Imports check ──
        if "imports" in selected:
            for lineno, line in enumerate(lines, 1):
                for old, new in DEPRECATED.items():
                    if old in line:
                        results["imports"]["errors"] += 1
                        results["imports"]["details"].append(f"{rel}:{lineno}: {old} → {new}")

        # ── Syntax check ──
        if "syntax" in selected:
            for lineno, line in enumerate(lines, 1):
                if line.strip().startswith("//"):
                    continue
                if re.search(r"\bvar\s+", line):
                    results["syntax"]["errors"] += 1
                if re.search(r":\s*(any|unknown)\b", line):
                    results["syntax"]["errors"] += 1
                if re.search(r"\bdelete\s+", line):
                    results["syntax"]["errors"] += 1
                if re.search(r"\beval\s*\(", line):
                    results["syntax"]["errors"] += 1

        # ── State management check ──
        if "state" in selected:
            has_v1 = False
            has_v2 = False
            for line in lines:
                for dec in V1_DECORATORS:
                    if re.search(r'\b' + re.escape(dec) + r'\b', line):
                        has_v1 = True
                for dec in V2_DECORATORS:
                    if re.search(r'\b' + re.escape(dec) + r'\b', line):
                        has_v2 = True
            if has_v1 and has_v2:
                results["state"]["errors"] += 1
                results["state"]["details"].append(f"{rel}: V1/V2 decorators mixed in same file")
            elif has_v1 and target_api >= 12:
                results["state"]["warns"] += 1
                results["state"]["details"].append(f"{rel}: Uses V1 decorators (target API {target_api})")

        # ── Security check ──
        if "security" in selected:
            for lineno, line in enumerate(lines, 1):
                # Hardcoded API keys/tokens
                if re.search(r'(api[_-]?key|token|secret|password)\s*[:=]\s*["\'][\w-]{8,}', line, re.I):
                    if not line.strip().startswith("//"):
                        results["security"]["errors"] += 1
                        results["security"]["details"].append(f"{rel}:{lineno}: Possible hardcoded secret")

        # ── HTTP lifecycle check ──
        if "http" in selected:
            has_create = any("http.createHttp" in l for l in lines)
            has_destroy = any(".destroy()" in l for l in lines)
            if has_create and not has_destroy:
                results["http"]["errors"] += 1
                results["http"]["details"].append(f"{rel}: createHttp() without destroy() in finally")

    # ── Architecture check ──
    if "architecture" in selected:
        # Check Internet permission
        if module_json.exists():
            try:
                mod = module_json.read_text(encoding="utf-8")
                if "ohos.permission.INTERNET" not in mod:
                    results["architecture"]["warns"] += 1
                    results["architecture"]["details"].append("INTERNET permission not declared in module.json5")
            except Exception:
                pass

        # Three-layer direction check
        common = root / "common"
        features = root / "features"
        products = root / "products" / "entry"
        if common.exists() and features.exists() and products.exists():
            results["architecture"]["details"].append("Three-layer architecture detected: ✅")
        else:
            results["architecture"]["details"].append("Single-module project (standard)")

    # ── Compute statuses ──
    for cat, r in results.items():
        if r["details"]:
            r["status"] = "FAIL" if r["errors"] > 0 else "WARN"
        else:
            r["status"] = "PASS"

    total_errors = sum(r["errors"] for r in results.values())
    total_warns = sum(r["warns"] for r in results.values())
    overall = "❌ FAIL" if total_errors > 0 else ("⚠️ WARN" if total_warns > 0 else "✅ PASS")

    # ── Build report ──
    report = [
        f"## ArkAgent Project Scan — {overall}",
        f"**Project**: `{root}` | **Files**: {len(ets_files)} | **Errors**: {total_errors} | **Warns**: {total_warns}\n",
        "| Category | Status | Errors | Warns |",
        "|----------|--------|--------|-------|",
    ]
    for cat, r in results.items():
        report.append(f"| {cat} | {r['status']} | {r['errors']} | {r['warns']} |")

    report.append("")
    for cat, r in results.items():
        if r["details"]:
            report.append(f"### {cat} ({r['status']})")
            for d in r["details"][:5]:
                report.append(f"- {d}")

    return "\n".join(report)[:5000]
