"""arkagent_search_docs — full-text search over ArkWeb knowledge base."""

from fastmcp import Context

from ...server import mcp, QueryIndex
from ...indexer.query import search_docs as do_search


@mcp.tool()
async def arkagent_search_docs(
    query: str,
    topic: str | None = None,
    max_results: int = 5,
    include_code_only: bool = False,
    context: Context | None = None,
) -> str:
    """Full-text search across the HarmonyOS ArkWeb knowledge base.

    Returns precise code blocks and surrounding context — never full file dumps.
    Use for questions like: 'how do I use javaScriptProxy?', 'WebMessagePort example',
    'renderMode options', 'NDK JSBridge setup'.

    Args:
        query: Natural language or keyword query (e.g., "javaScriptProxy 注册方式")
        topic: Optional filter to a specific topic area
        max_results: Maximum results (1-10, default 5)
        include_code_only: If true, return only code blocks without prose context
    """
    idx = QueryIndex.get()
    results = do_search(idx, query, topic, max_results, include_code_only)

    if not results:
        return f"*No results found for: '{query}'*\n\nTry `arkagent_list_topics()` to see available topics."

    lines = [f"## Search: '{query}'", f"Found {len(results)} result(s):\n"]
    for i, r in enumerate(results):
        lines.append(f"### {i+1}. {r.title}")
        lines.append(f"**File**: `{r.file_name}` | **Relevance**: {r.relevance:.2f}")
        if r.heading:
            lines.append(f"**Section**: {r.heading}")
        if r.api_ref:
            lines.append(f"**API**: `{r.api_ref.name}` — documented in `{r.api_ref.file_name}`")
        if r.snippet and not include_code_only:
            lines.append(f"\n{r.snippet[:500]}")
        for blk in r.code_blocks:
            lang = blk.language or "typescript"
            code = blk.content[:800]  # Cap code block size
            lines.append(f"\n```{lang}\n{code}\n```")
        lines.append("")

    out = "\n".join(lines)
    # Hard cap at ~2000 tokens worth of chars
    return out[:6000]


@mcp.tool()
async def arkagent_api_lookup(
    api_name: str,
    include_example: bool = True,
    context: Context | None = None,
) -> str:
    """Look up a specific ArkWeb API/interface by name.

    Returns signature, parameters, return type, and a usage example in one compact block.
    Use for: 'what does registerJavaScriptProxy do?',
    'WebviewController.zoomIn signature', 'createWebMessagePorts parameters'.

    Args:
        api_name: Exact or partial API name (e.g., "registerJavaScriptProxy", "runJavaScript")
        include_example: Include a code example (default true)
    """
    from ...indexer.query import api_lookup as do_lookup

    idx = QueryIndex.get()
    result = do_lookup(idx, api_name)

    if result is None:
        return (f"*API '{api_name}' not found in knowledge base.*\n\n"
                f"Try `arkagent_search_docs(\"{api_name}\")` for a broader search.")

    lines = [
        f"## `{api_name}`",
        f"**Source**: `{result.file_name}` — {result.title}",
    ]
    if result.heading:
        lines.append(f"**Section**: {result.heading}")
    if result.api_ref:
        api = result.api_ref
        lines.append(f"**Referenced in**: {len(api.section_indices)} section(s), "
                     f"{len(api.code_block_indices)} code block(s)")

    if result.snippet:
        lines.append(f"\n### Context\n{result.snippet[:500]}")

    if include_example and result.code_blocks:
        lines.append(f"\n### Code Example(s)")
        for i, blk in enumerate(result.code_blocks[:2]):
            lang = blk.language or "typescript"
            code = blk.content[:800]
            lines.append(f"\n```{lang}\n{code}\n```")

    return "\n".join(lines)[:5000]


@mcp.tool()
async def arkagent_find_example(
    scenario: str,
    topic: str | None = None,
    context: Context | None = None,
) -> str:
    """Retrieve complete, compilable code examples from the knowledge base.

    Returns full code blocks with imports and surrounding context.
    Use for: 'show me a javaScriptProxy example',
    'complete WebMessagePort setup', 'offline web component usage'.

    Args:
        scenario: Natural language scenario description (e.g., "offline web loading")
        topic: Optional filter to a specific topic area
    """
    from ...indexer.query import find_example as do_find

    idx = QueryIndex.get()
    result = do_find(idx, scenario, topic)

    if result is None:
        return (f"*No example found for: '{scenario}'*\n\n"
                f"Try `arkagent_search_docs(\"{scenario}\")` for related content.")

    lines = [
        f"## Example: {scenario}",
        f"**Source**: `{result.file_name}` — {result.title}",
        f"**Relevance**: {result.relevance:.2f}\n",
    ]
    if result.snippet:
        lines.append(f"### Context\n{result.snippet[:300]}\n")

    for i, blk in enumerate(result.code_blocks):
        lang = blk.language or "typescript"
        lines.append(f"### Code Block {i+1}\n```{lang}\n{blk.content[:1500]}\n```")

    return "\n".join(lines)[:6000]


@mcp.tool()
async def arkagent_list_topics(
    filter_pattern: str | None = None,
    context: Context | None = None,
) -> str:
    """List all indexed knowledge base topics with file sizes, code block counts,
    and key API coverage.

    Use as the first call to understand what's available before drilling into specific docs.

    Args:
        filter_pattern: Optional glob/pattern to filter topics (e.g., "web", "ndk", "offline")
    """
    from ...indexer.query import list_topics as do_list

    idx = QueryIndex.get()
    topics = do_list(idx, filter_pattern)

    lines = [
        f"## ArkAgent Knowledge Base — {len(topics)} Topics",
        "",
        "| # | Section | File | Lines | Codes | Top APIs |",
        "|---|---------|------|-------|-------|----------|",
    ]
    for i, t in enumerate(topics):
        apis = ", ".join(f"`{a}`" for a in t.top_apis[:3]) or "—"
        section = t.section or "—"
        lines.append(f"| {i+1} | `{section}` | `{t.file_name}` | {t.line_count} | {t.code_block_count} | {apis} |")

    lines.append(f"\n*Use `arkagent_search_docs(\"query\")` or `arkagent_api_lookup(\"name\")` "
                 f"to retrieve content.*")
    return "\n".join(lines)[:4000]
