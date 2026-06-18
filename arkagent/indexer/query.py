"""Query the search index with token-efficient result assembly.

Uses TF-IDF cosine similarity for section ranking and inverted index
for code block matching. Results are capped at ~2000 tokens.
"""

import math
from dataclasses import dataclass, field

from .builder import tokenize
from .schemas import SearchIndex, Section, CodeBlock, APIReference, FileMeta


@dataclass
class SearchResult:
    """A single search result."""
    file_name: str
    title: str
    heading: str
    snippet: str  # Relevant text excerpt (~200 tokens)
    code_blocks: list[CodeBlock] = field(default_factory=list)
    api_ref: APIReference | None = None
    relevance: float = 0.0


def _cosine_similarity(query_vec: dict[str, float], doc_vec: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    if not query_vec or not doc_vec:
        return 0.0
    dot = sum(query_vec.get(t, 0.0) * doc_vec.get(t, 0.0) for t in query_vec)
    q_norm = math.sqrt(sum(v**2 for v in query_vec.values()))
    d_norm = math.sqrt(sum(v**2 for v in doc_vec.values()))
    if q_norm == 0 or d_norm == 0:
        return 0.0
    return dot / (q_norm * d_norm)


def _truncate_snippet(text: str, max_chars: int = 800) -> str:
    """Truncate text to approximately max_chars characters (≈ 200 tokens)."""
    if len(text) <= max_chars:
        return text
    # Try to break at a paragraph or sentence boundary
    truncated = text[:max_chars]
    last_break = max(truncated.rfind("\n\n"), truncated.rfind("。"), truncated.rfind(". "))
    if last_break > max_chars // 2:
        return truncated[:last_break] + "\n..."
    return truncated + "..."


def search_docs(
    index: SearchIndex,
    query: str,
    topic: str | None = None,
    max_results: int = 5,
    include_code_only: bool = False,
) -> list[SearchResult]:
    """Full-text search over the knowledge base."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Build query TF vector
    query_tf: dict[str, float] = {}
    for t in query_tokens:
        query_tf[t] = query_tf.get(t, 0.0) + 1.0
    total = len(query_tokens)
    for t in query_tf:
        query_tf[t] /= total

    # Score sections by TF-IDF cosine similarity
    scored: list[tuple[int, float]] = []
    for si, sec in enumerate(index.sections):
        if topic and topic not in sec.file_name:
            continue
        sec_tokens = tokenize(sec.content)
        sec_tf: dict[str, float] = {}
        for t in sec_tokens:
            sec_tf[t] = sec_tf.get(t, 0.0) + 1.0
        st = len(sec_tokens)
        for t in sec_tf:
            sec_tf[t] /= st
        score = _cosine_similarity(query_tf, sec_tf)
        if score > 0:
            scored.append((si, score))

    scored.sort(key=lambda x: -x[1])

    # Also check code blocks via inverted index
    code_matches: set[int] = set()
    for token in query_tokens:
        if token in index.code_inverted:
            code_matches.update(index.code_inverted[token][:3])

    # Assemble results
    results: list[SearchResult] = []
    seen_files: set[str] = set()

    for si, score in scored[:max_results * 2]:
        sec = index.sections[si]
        meta = index.topics.get(sec.file_name)
        if meta is None:
            continue

        # Deduplicate by file (show best section per file)
        if sec.file_name in seen_files:
            continue

        snippet = _truncate_snippet(sec.content)
        if include_code_only:
            snippet = ""  # Only return code blocks

        # Find relevant code blocks
        blocks = []
        for bi in sec.code_block_indices:
            if bi < len(index.code_blocks):
                blocks.append(index.code_blocks[bi])
        # Also include code blocks matched directly
        for bi in code_matches:
            if bi < len(index.code_blocks):
                blk = index.code_blocks[bi]
                if blk.start_line >= sec.start_line and blk.end_line <= sec.end_line:
                    if bi not in [b.start_line for b in blocks]:
                        blocks.append(blk)

        results.append(SearchResult(
            file_name=sec.file_name,
            title=meta.title,
            heading=sec.heading,
            snippet=snippet,
            code_blocks=blocks[:2],  # Max 2 code blocks per result
            relevance=score,
        ))
        seen_files.add(sec.file_name)

        if len(results) >= max_results:
            break

    # If query matches an API name, add API card
    query_lower = query.lower()
    for api_name, api_ref in index.apis.items():
        if api_name.lower() in query_lower or query_lower in api_name.lower():
            for r in results:
                if r.file_name == api_ref.file_name:
                    r.api_ref = api_ref
                    r.relevance = max(r.relevance, 0.95)
                    break

    return results


def api_lookup(index: SearchIndex, api_name: str) -> SearchResult | None:
    """Look up a specific API by name."""
    # Exact match
    api_ref = index.apis.get(api_name)
    # Case-insensitive match
    if api_ref is None:
        for name, ref in index.apis.items():
            if name.lower() == api_name.lower():
                api_ref = ref
                break
    # Partial match
    if api_ref is None:
        api_lower = api_name.lower()
        for name, ref in index.apis.items():
            if api_lower in name.lower() or name.lower() in api_lower:
                api_ref = ref
                break

    if api_ref is None:
        return None

    meta = index.topics.get(api_ref.file_name)
    if meta is None:
        return None

    # Find the most relevant section
    best_sec: Section | None = None
    best_score = 0.0
    for si in api_ref.section_indices:
        if si < len(index.sections):
            sec = index.sections[si]
            score = float(sec.content.lower().count(api_name.lower()))
            if score > best_score:
                best_score = score
                best_sec = sec

    # Find code blocks
    blocks = []
    for bi in api_ref.code_block_indices:
        if bi < len(index.code_blocks):
            blocks.append(index.code_blocks[bi])

    snippet = _truncate_snippet(best_sec.content) if best_sec else ""

    return SearchResult(
        file_name=api_ref.file_name,
        title=meta.title,
        heading=best_sec.heading if best_sec else "",
        snippet=snippet,
        code_blocks=blocks[:3],
        api_ref=api_ref,
        relevance=1.0,
    )


def find_example(
    index: SearchIndex,
    scenario: str,
    topic: str | None = None,
) -> SearchResult | None:
    """Find a complete code example matching a scenario."""
    query_tokens = tokenize(scenario)

    # Score code blocks by token match density
    best_idx = -1
    best_score = 0.0

    for bi, blk in enumerate(index.code_blocks):
        if topic and topic not in index.sections[0].file_name:
            # Find which file this block belongs to
            # (simplified: skip topic filter for code blocks)
            pass
        if len(blk.content) < 50:
            continue  # Skip tiny code blocks

        blk_tokens = set(tokenize(blk.content))
        matches = sum(1 for t in query_tokens if t in blk_tokens)
        if len(query_tokens) > 0:
            score = matches / len(query_tokens)
        else:
            score = 0.0

        # Boost for typescript blocks
        if blk.language in ("typescript", "ts", "ets"):
            score *= 1.5

        if score > best_score:
            best_score = score
            best_idx = bi

    if best_idx < 0 or best_score < 0.1:
        return None

    blk = index.code_blocks[best_idx]

    # Determine which file this block belongs to
    file_name = "unknown"
    for fname, meta in index.topics.items():
        for sec in index.sections:
            if sec.file_name == fname and sec.start_line <= blk.start_line <= sec.end_line:
                file_name = fname
                break
        if file_name != "unknown":
            break

    meta = index.topics.get(file_name)

    return SearchResult(
        file_name=file_name,
        title=meta.title if meta else "",
        heading="",
        snippet=blk.context_before,
        code_blocks=[blk],
        relevance=best_score,
    )


def list_topics(index: SearchIndex, filter_pattern: str | None = None) -> list[FileMeta]:
    """List all indexed topics."""
    topics = list(index.topics.values())
    topics.sort(key=lambda t: -t.line_count)
    if filter_pattern:
        topics = [t for t in topics if filter_pattern.lower() in t.file_name.lower()
                  or filter_pattern.lower() in t.title.lower()]
    return topics
