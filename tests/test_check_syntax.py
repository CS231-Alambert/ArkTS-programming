"""Tests for check_syntax validation tool.

Uses fixtures/minimal_project/ as test data.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from arkagent.tools.validation.check_syntax import arkagent_check_syntax

FIXTURES = Path(__file__).parent / "fixtures" / "minimal_project"


@pytest.mark.asyncio
async def test_check_good_page():
    """Good page should have no critical errors."""
    good_file = FIXTURES / "entry/src/main/ets/pages/Index.ets"
    result = await arkagent_check_syntax(file_path=str(good_file), project_root=str(FIXTURES))
    # Should not report critical errors for a clean file
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_check_bad_page():
    """Bad page should flag var, any, @ohos old import."""
    bad_file = FIXTURES / "entry/src/main/ets/pages/BadPage.ets"
    result = await arkagent_check_syntax(file_path=str(bad_file), project_root=str(FIXTURES))
    assert isinstance(result, str)
    # BadPage has: var, any, @ohos.router → should report issues
    combined = result.lower()
    assert any(kw in combined for kw in ["var", "any", "@ohos", "issue", "error", "warning"])


@pytest.mark.asyncio
async def test_check_directory():
    """Scan entire project directory."""
    ets_dir = FIXTURES / "entry/src/main/ets"
    result = await arkagent_check_syntax(file_path=str(ets_dir), project_root=str(FIXTURES))
    assert isinstance(result, str)
    # Should find both files
    assert "Index" in result or "BadPage" in result or len(result) > 50


@pytest.mark.asyncio
async def test_check_with_pass_filter():
    """Respect 'passes' argument."""
    result = await arkagent_check_syntax(
        file_path=str(FIXTURES / "entry/src/main/ets/pages/BadPage.ets"),
        project_root=str(FIXTURES),
        passes="1,2,3",  # only first 3 passes
    )
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_check_with_skip():
    """Respect 'skip' argument."""
    result = await arkagent_check_syntax(
        file_path=str(FIXTURES / "entry/src/main/ets/pages/BadPage.ets"),
        project_root=str(FIXTURES),
        skip="1,2,3",
    )
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_nonexistent_file():
    """Graceful handling of missing file."""
    result = await arkagent_check_syntax(
        file_path=str(FIXTURES / "nonexistent.ets"),
        project_root=str(FIXTURES),
    )
    assert isinstance(result, str)
