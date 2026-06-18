"""ArkAgent CLI entry point."""

import sys
import argparse

from .server import mcp


def main():
    parser = argparse.ArgumentParser(
        prog="arkagent",
        description="ArkAgent MCP Server — HarmonyOS/ArkTS knowledge + validation",
    )
    sub = parser.add_subparsers(dest="command")

    # `arkagent mcp`
    mcp_parser = sub.add_parser("mcp", help="Start MCP server")
    mcp_parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )

    # `arkagent rebuild-index`
    rebuild = sub.add_parser("rebuild-index", help="Force rebuild the search index")

    # `arkagent version`
    version = sub.add_parser("version", help="Print version")

    args = parser.parse_args()

    if args.command == "mcp":
        from .server import _init_index
        # Pre-build index before starting server
        _init_index()
        mcp.run(transport=args.transport)
    elif args.command == "rebuild-index":
        from .indexer.builder import build_index, save_index
        print("Rebuilding search index...")
        idx = build_index()
        path = save_index(idx)
        print(f"Index rebuilt: {idx.source_file_count} files, {idx.total_lines} lines, {len(idx.apis)} APIs")
        print(f"Saved to: {path}")
    elif args.command == "version":
        from . import __version__
        print(f"ArkAgent v{__version__}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
