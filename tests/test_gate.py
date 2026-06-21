"""Tests for the gate pipeline tools."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from arkagent.tools.gate import (
    _checkpoint_path,
    _scan_project,
    arkagent_gate_check,
    arkagent_gate_scan,
    arkagent_gate_status,
)

FIXTURES = Path(__file__).parent / "fixtures" / "minimal_project"


# ── unit tests for helpers ──

class TestCheckpointPath:
    def test_returns_checkpoint_dir(self):
        """_checkpoint_path returns .arkts-check directory (not a specific file)."""
        cp = _checkpoint_path("/tmp/myproject")
        assert cp == Path("/tmp/myproject/.arkts-check")

    def test_relative_path(self):
        cp = _checkpoint_path(".")
        assert cp.name == ".arkts-check"


class TestScanProject:
    def test_scans_fixture_project(self):
        data = _scan_project(FIXTURES)
        assert data["has_entry_module"] is True
        assert data["has_module_json5"] is True
        assert data["has_common_layer"] is True  # fixtures has common/
        assert data["has_features_layer"] is True
        assert data["has_products_layer"] is True
        assert data["architecture"] == "three-layer (common/features/products)"

    def test_scan_empty_dir(self):
        with tempfile.TemporaryDirectory() as td:
            data = _scan_project(Path(td))
            assert data["has_entry_module"] is False
            assert data["architecture"] == "minimal (no standard structure detected)"


# ── integration tests for MCP tools ──

@pytest.mark.asyncio
async def test_gate_scan_writes_checkpoint():
    with tempfile.TemporaryDirectory() as td:
        # Create minimal entry structure
        entry = Path(td) / "entry/src/main"
        entry.mkdir(parents=True)
        (entry / "module.json5").write_text("{}")
        profile = entry / "resources/base/profile"
        profile.mkdir(parents=True)
        (profile / "main_pages.json").write_text('{"src": ["pages/Index"]}')

        result = await arkagent_gate_scan(project_root=td)
        assert "PASS" in result
        assert (Path(td) / ".arkts-check/00-scan.json").exists()


@pytest.mark.asyncio
async def test_gate_scan_nonexistent_dir():
    """Should still report (doesn't fail — scans what exists)."""
    result = await arkagent_gate_scan(project_root="/nonexistent/path/xyz")
    assert isinstance(result, str)
    assert "PASS" in result  # graceful: reports minimal structure


@pytest.mark.asyncio
async def test_gate_check_without_scan():
    with tempfile.TemporaryDirectory() as td:
        result = await arkagent_gate_check(project_root=td)
        # Should warn that 00-scan.json is missing
        assert "00-scan" in result or "BLOCKED" in result.upper() or "not found" in result.lower()


@pytest.mark.asyncio
async def test_gate_check_with_valid_scan():
    with tempfile.TemporaryDirectory() as td:
        # Run scan first
        entry = Path(td) / "entry/src/main"
        entry.mkdir(parents=True)
        (entry / "module.json5").write_text("{}")
        profile = entry / "resources/base/profile"
        profile.mkdir(parents=True)
        (profile / "main_pages.json").write_text('{"src": ["pages/Index"]}')

        await arkagent_gate_scan(project_root=td)

        # Create 01-generated.json
        gen = Path(td) / ".arkts-check/01-generated.json"
        gen.write_text(json.dumps({"timestamp": "2026-01-01T00:00:00", "files": ["test.ets"]}))

        result = await arkagent_gate_check(project_root=td)
        assert isinstance(result, str)
        assert len(result) > 0


@pytest.mark.asyncio
async def test_gate_status():
    with tempfile.TemporaryDirectory() as td:
        result = await arkagent_gate_status(project_root=td)
        assert isinstance(result, str)


@pytest.mark.asyncio
async def test_full_pipeline():
    """End-to-end: scan → generate checkpoint → check → status."""
    with tempfile.TemporaryDirectory() as td:
        # Build project structure
        entry = Path(td) / "entry/src/main"
        entry.mkdir(parents=True)
        (entry / "module.json5").write_text("{}")
        profile = entry / "resources/base/profile"
        profile.mkdir(parents=True)
        (profile / "main_pages.json").write_text('{"src": ["pages/Index"]}')

        # Step 0
        r0 = await arkagent_gate_scan(project_root=td)
        assert "PASS" in r0
        assert (Path(td) / ".arkts-check/00-scan.json").exists()

        # Step 1 checkpoint
        gen = Path(td) / ".arkts-check/01-generated.json"
        gen.write_text(json.dumps({"timestamp": "2026-01-01T00:00:00", "files": ["test.ets"]}))

        # Step 2
        r2 = await arkagent_gate_check(project_root=td)
        assert isinstance(r2, str)

        # Step 3
        r3 = await arkagent_gate_status(project_root=td)
        assert isinstance(r3, str)
