"""Server configuration"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ServerConfig:
    """ArkAgent MCP server configuration."""

    # Knowledge base path (root with subdirectories: arkweb/, arkts/, arkui/, ui-design-kit/)
    kb_path: Path = Path(
        "/root/.cc-switch/skills/harmonyos-arkts/docs"
    )

    # Index file path (generated at startup)
    index_path: Path = Path("/root/ArkAgent/arkagent/indexer/index.json")

    # Rules directory
    rules_path: Path = Path("/root/.claude/rules/ecc/arkts")

    # Default max results per search
    max_search_results: int = 5

    # Max tokens per tool response (approximate)
    max_response_tokens: int = 2000

    # Rebuild index if source files are newer than index
    auto_rebuild: bool = True


# Global config instance
config = ServerConfig()
