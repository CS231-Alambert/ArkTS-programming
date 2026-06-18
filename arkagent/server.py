"""ArkAgent MCP Server — FastMCP entry point with lifespan-based index management."""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastmcp import FastMCP

from .config import config
from .indexer.builder import build_index, load_index, save_index


# ── Global index instance (populated at startup) ──

class QueryIndex:
    """Thin wrapper that holds the loaded search index for tool access."""

    _instance: object | None = None  # SearchIndex

    @classmethod
    def get(cls):
        if cls._instance is None:
            raise RuntimeError("Index not loaded — server lifespan not yet run")
        return cls._instance

    @classmethod
    def set(cls, index):
        cls._instance = index


def _should_rebuild() -> bool:
    """Check if index needs rebuilding (source files newer than index.json)."""
    idx_path = config.index_path
    if not idx_path.exists():
        return True
    idx_mtime = idx_path.stat().st_mtime
    for md_file in config.kb_path.glob("*.md"):
        if md_file.stat().st_mtime > idx_mtime:
            return True
    return False


def _init_index():
    """Initialize the search index: load cached or build fresh."""
    if _should_rebuild():
        print("[ArkAgent] Building search index...", file=sys.stderr)
        idx = build_index()
        save_index(idx)
        print(f"[ArkAgent] Index built: {idx.source_file_count} files, "
              f"{idx.total_lines} lines, {len(idx.apis)} APIs", file=sys.stderr)
    else:
        print("[ArkAgent] Loading cached index...", file=sys.stderr)
        idx = load_index()
        print(f"[ArkAgent] Index loaded: {idx.source_file_count} files", file=sys.stderr)
    QueryIndex.set(idx)


# ── FastMCP Server ──

@asynccontextmanager
async def lifespan(app: FastMCP):
    """Server lifespan: build index on startup, cleanup on shutdown."""
    _init_index()
    yield
    # Cleanup (if needed)
    QueryIndex.set(None)


mcp = FastMCP(
    name="ArkAgent",
    lifespan=lifespan,
)


# ── Tool registration (import triggers @mcp.tool() decorators) ──

def register_tools():
    """Import all tool modules to trigger @mcp.tool() decorator registration."""
    # Knowledge tools (all in search_docs.py)
    import arkagent.tools.knowledge.search_docs  # noqa: F401
    # Validation tools
    import arkagent.tools.validation.validate_imports  # noqa: F401
    import arkagent.tools.validation.check_syntax  # noqa: F401
    import arkagent.tools.validation.check_state_mgmt  # noqa: F401
    import arkagent.tools.validation.scan_project  # noqa: F401
    # Gate pipeline tools
    import arkagent.tools.gate  # noqa: F401


# Register at import time
register_tools()
