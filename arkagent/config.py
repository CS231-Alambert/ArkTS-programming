"""Server configuration"""

import os
from dataclasses import dataclass, field
from pathlib import Path


def _resolve(path: str) -> Path:
    """Resolve a path that may be absolute or relative to this config file."""
    p = Path(os.path.expandvars(path))
    if p.is_absolute():
        return p
    return (Path(__file__).parent / p).resolve()


@dataclass
class ServerConfig:
    """ArkAgent MCP server configuration.

    All paths support environment variable overrides:
      ARKAGENT_KB_PATH    — knowledge base root (subdirs: arkweb/, arkts/, arkui/, ui-design-kit/)
      ARKAGENT_INDEX_PATH — TF-IDF index file
      ARKAGENT_RULES_PATH — ArkTS rule definitions
    """

    # Knowledge base path — default: ../docs relative to this config file
    kb_path: Path = field(default_factory=lambda: _resolve(
        os.environ.get("ARKAGENT_KB_PATH", "../docs")
    ))

    # Index file path — generated at startup / rebuild
    index_path: Path = field(default_factory=lambda: _resolve(
        os.environ.get("ARKAGENT_INDEX_PATH", "indexer/index.json")
    ))

    # Rules directory — default: user-level ECC ArkTS rules
    rules_path: Path = field(default_factory=lambda: _resolve(
        os.environ.get("ARKAGENT_RULES_PATH", "/root/.claude/rules/ecc/arkts")
    ))

    # Default max results per search
    max_search_results: int = 5

    # Max tokens per tool response (approximate)
    max_response_tokens: int = 2000

    # Rebuild index if source files are newer than index
    auto_rebuild: bool = True


# Global config instance
config = ServerConfig()
