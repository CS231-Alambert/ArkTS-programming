"""ArkAgent — HarmonyOS/ArkTS MCP Server"""

__version__ = "0.1.0"

# Convenience re-exports for external consumers
from .config import ServerConfig, config
from .indexer.builder import build_index, load_index, save_index
from .indexer.schemas import SearchIndex

__all__ = [
    "__version__",
    "ServerConfig",
    "config",
    "build_index",
    "load_index",
    "save_index",
    "SearchIndex",
]
