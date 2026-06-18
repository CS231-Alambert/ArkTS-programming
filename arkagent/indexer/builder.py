"""Build search index from knowledge base markdown files.

Parses all .md files in the KB directory, extracts sections, code blocks,
and API references, builds TF-IDF and inverted indices, serializes to index.json.
"""

import json
import re
import math
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

from ..config import config
from .schemas import (
    SearchIndex, Section, CodeBlock, FileMeta, APIReference,
)


def tokenize(text: str) -> list[str]:
    """Tokenize text: jieba for Chinese + whitespace for English."""
    tokens: list[str] = []
    # Split Chinese characters from ASCII
    parts = re.split(r'([一-鿿]+)', text.lower())
    for part in parts:
        if not part.strip():
            continue
        if re.match(r'[一-鿿]', part):
            try:
                import jieba
                tokens.extend(jieba.lcut(part))
            except ImportError:
                # Fallback: character-level bigrams
                tokens.extend(part[i:i+2] for i in range(len(part)-1))
        else:
            # ASCII: split on non-alphanumeric
            tokens.extend(re.findall(r'[a-z0-9_]+', part))
    return [t.strip() for t in tokens if t.strip() and len(t.strip()) > 1]


def extract_sections(file_name: str, lines: list[str]) -> list[Section]:
    """Extract heading-delimited sections from markdown lines."""
    sections: list[Section] = []
    current_heading = ""
    current_level = 0
    current_start = 0
    current_lines: list[str] = []

    for i, line in enumerate(lines):
        m = re.match(r'^(#{2,4})\s+(.+)', line)
        if m:
            # Save previous section
            if current_lines:
                sections.append(Section(
                    heading=current_heading,
                    heading_level=current_level,
                    file_name=file_name,
                    start_line=current_start,
                    end_line=i - 1,
                    content="\n".join(current_lines),
                ))
            # Start new section
            current_heading = m.group(2).strip()
            current_level = len(m.group(1))
            current_start = i
            current_lines = [line]
        else:
            current_lines.append(line)

    # Save final section
    if current_lines:
        sections.append(Section(
            heading=current_heading or "(top)",
            heading_level=current_level or 1,
            file_name=file_name,
            start_line=current_start,
            end_line=len(lines) - 1,
            content="\n".join(current_lines),
        ))

    return sections


def extract_code_blocks(lines: list[str]) -> list[CodeBlock]:
    """Extract fenced code blocks with context."""
    blocks: list[CodeBlock] = []
    in_block = False
    block_start = 0
    block_lang = ""
    block_lines: list[str] = []

    for i, line in enumerate(lines):
        m = re.match(r'^```(\w*)\s*$', line)
        if m and not in_block:
            in_block = True
            block_start = i
            block_lang = m.group(1) or "text"
            block_lines = []
        elif m and in_block:
            in_block = False
            lang = block_lang
            content = "\n".join(block_lines)
            # Get context (3 lines before/after)
            ctx_before = "\n".join(lines[max(0, block_start-3):block_start])
            ctx_after = "\n".join(lines[i+1:min(len(lines), i+4)])
            blocks.append(CodeBlock(
                start_line=block_start,
                end_line=i,
                language=lang,
                content=content,
                context_before=ctx_before,
                context_after=ctx_after,
            ))
        elif in_block:
            block_lines.append(line)

    return blocks


def extract_api_names(content: str) -> list[str]:
    """Extract API names from content using known patterns."""
    apis: set[str] = set()

    # Pattern 1: [apiName](...references...apiName)
    api_links = re.findall(
        r'\[([a-zA-Z_][a-zA-Z0-9_.]*)\]\([^)]*references[^)]*\)',
        content,
    )
    apis.update(api_links)

    # Pattern 2: code-quoted identifiers that look like APIs
    code_refs = re.findall(r'`([A-Z][a-zA-Z]+(?:[A-Z][a-z]+)+)`', content)
    apis.update(code_refs)

    # Pattern 3: method calls: controller.methodName(...)
    method_calls = re.findall(
        r'(?:\.)?\b(registerJavaScriptProxy|deleteJavaScriptRegister|runJavaScript|'
        r'javaScriptProxy|createWebMessagePorts|postMessage|onMessageEvent|closePort|'
        r'zoomIn|zoomOut|refresh|backward|forward|getUrl|getTitle|'
        r'accessBackward|accessForward|pageUp|pageDown|'
        r'setWindowDebugEnabled|loadUrl|loadData|'
        r'requestFocus|lostFocus|clearHistory|getHitTestValue)',
        content,
    )
    apis.update(method_calls)

    return sorted(apis)


def compute_tfidf(sections: list[Section]) -> dict[str, dict[int, float]]:
    """Compute TF-IDF vectors for all sections."""
    N = len(sections)
    if N == 0:
        return {}

    # Tokenize all sections
    section_tokens: list[list[str]] = []
    doc_freq: dict[str, int] = defaultdict(int)

    for sec in sections:
        tokens = tokenize(sec.content)
        section_tokens.append(tokens)
        unique_terms = set(tokens)
        for term in unique_terms:
            doc_freq[term] += 1

    # Compute TF-IDF
    tfidf: dict[str, dict[int, float]] = defaultdict(dict)
    for idx, tokens in enumerate(section_tokens):
        if not tokens:
            continue
        term_count: dict[str, int] = defaultdict(int)
        for t in tokens:
            term_count[t] += 1
        doc_len = len(tokens)
        for term, count in term_count.items():
            tf = count / doc_len
            idf = math.log((N + 1) / (doc_freq[term] + 1)) + 1
            tfidf[term][idx] = tf * idf

    return dict(tfidf)


def build_inverted_index(sections: list[Section]) -> dict[str, list[int]]:
    """Build inverted index: term → list of section indices."""
    inverted: dict[str, set[int]] = defaultdict(set)
    for idx, sec in enumerate(sections):
        tokens = set(tokenize(sec.content))
        for term in tokens:
            inverted[term].add(idx)
    return {k: sorted(v) for k, v in inverted.items()}


def build_code_inverted(blocks: list[CodeBlock]) -> dict[str, list[int]]:
    """Build inverted index for code blocks."""
    inverted: dict[str, set[int]] = defaultdict(set)
    for idx, block in enumerate(blocks):
        tokens = set(tokenize(block.content))
        for term in tokens:
            inverted[term].add(idx)
    return {k: sorted(v) for k, v in inverted.items()}


def build_index(kb_path: Path | None = None) -> SearchIndex:
    """Build the complete search index from knowledge base files."""
    kb = kb_path or config.kb_path
    if not kb.exists():
        raise FileNotFoundError(f"Knowledge base not found: {kb}")

    md_files = sorted(kb.rglob("*.md"))
    # Filter out INDEX files (00- prefix)
    md_files = [f for f in md_files if not f.name.startswith("00-")]

    all_sections: list[Section] = []
    all_blocks: list[CodeBlock] = []
    topics: dict[str, FileMeta] = {}
    apis: dict[str, APIReference] = {}

    for fpath in md_files:
        lines = fpath.read_text(encoding="utf-8").splitlines()
        file_name = fpath.name

        # Extract sections
        sections = extract_sections(file_name, lines)
        # Extract code blocks
        blocks = extract_code_blocks(lines)

        # Link code blocks to sections
        for si, sec in enumerate(sections):
            sec.code_block_indices = []
            for bi, blk in enumerate(blocks):
                if blk.start_line >= sec.start_line and blk.end_line <= sec.end_line:
                    sec.code_block_indices.append(bi)

        # Extract APIs
        full_content = "\n".join(lines)
        api_names = extract_api_names(full_content)

        # Build file metadata
        h1 = lines[0].lstrip("# ") if lines else file_name
        h2s = [re.sub(r'^#+\s*', '', l) for l in lines if re.match(r'^##\s', l)]
        # Derive section from parent directory name
        section = fpath.parent.name if fpath.parent != kb else ""
        topics[file_name] = FileMeta(
            file_name=file_name,
            title=h1,
            section=section,
            line_count=len(lines),
            code_block_count=len(blocks),
            top_headings=h2s[:5],
            top_apis=api_names[:5],
        )

        # Register APIs
        offset = len(all_sections)
        for api in api_names:
            if api not in apis:
                apis[api] = APIReference(name=api, file_name=file_name)
            sec_indices = [
                offset + si for si, sec in enumerate(sections)
                if api.lower() in sec.content.lower()
            ]
            blk_indices = [
                bi for bi, blk in enumerate(blocks)
                if api in blk.content
            ]
            apis[api].section_indices.extend(sec_indices)
            apis[api].code_block_indices.extend(blk_indices)

        all_sections.extend(sections)
        all_blocks.extend(blocks)

    # Compute TF-IDF and inverted indices
    tfidf = compute_tfidf(all_sections)
    inverted = build_inverted_index(all_sections)
    code_inverted = build_code_inverted(all_blocks)

    index = SearchIndex(
        topics=topics,
        sections=all_sections,
        code_blocks=all_blocks,
        apis=apis,
        inverted=inverted,
        code_inverted=code_inverted,
        build_time=datetime.now(timezone.utc).isoformat(),
        source_file_count=len(md_files),
        total_lines=sum(t.line_count for t in topics.values()),
    )

    return index


def save_index(index: SearchIndex, path: Path | None = None) -> Path:
    """Serialize index to JSON file."""
    out = path or config.index_path
    out.parent.mkdir(parents=True, exist_ok=True)

    # Convert to serializable dict (full content ~800KB — one-time load at startup)
    data = {
        "topics": {k: v.__dict__ for k, v in index.topics.items()},
        "sections": [s.__dict__ for s in index.sections],
        "code_blocks": [b.__dict__ for b in index.code_blocks],
        "apis": {k: v.__dict__ for k, v in index.apis.items()},
        "inverted": index.inverted,
        "code_inverted": index.code_inverted,
        "build_time": index.build_time,
        "source_file_count": index.source_file_count,
        "total_lines": index.total_lines,
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return out


def load_index(path: Path | None = None) -> SearchIndex:
    """Load index from JSON file."""
    p = path or config.index_path
    if not p.exists():
        raise FileNotFoundError(f"Index not found: {p} — run build_index() first")

    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    # Deserialize sections
    sections = [Section(**s) for s in data["sections"]]

    # Deserialize code blocks
    code_blocks = [CodeBlock(**b) for b in data["code_blocks"]]

    # Deserialize topics
    topics = {k: FileMeta(**v) for k, v in data["topics"].items()}

    # Deserialize APIs
    apis = {k: APIReference(**v) for k, v in data["apis"].items()}

    return SearchIndex(
        topics=topics,
        sections=sections,
        code_blocks=code_blocks,
        apis=apis,
        inverted=data.get("inverted", {}),
        code_inverted=data.get("code_inverted", {}),
        build_time=data.get("build_time", ""),
        source_file_count=data.get("source_file_count", 0),
        total_lines=data.get("total_lines", 0),
    )
