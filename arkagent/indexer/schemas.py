"""Index data schemas"""

from dataclasses import dataclass, field


@dataclass
class CodeBlock:
    """A fenced code block extracted from a markdown file."""

    start_line: int
    end_line: int
    language: str  # "typescript", "json5", "text"
    content: str
    context_before: str  # ~3 lines of prose before the block
    context_after: str  # ~3 lines of prose after the block


@dataclass
class Section:
    """A heading-delimited section within a knowledge base file."""

    heading: str  # e.g., "## javaScriptProxy 注册方式"
    heading_level: int  # 2, 3, or 4
    file_name: str  # Which KB file this section belongs to
    start_line: int
    end_line: int
    content: str  # Full section text
    code_block_indices: list[int] = field(default_factory=list)


@dataclass
class FileMeta:
    """Metadata about a knowledge base file."""

    file_name: str
    title: str  # First H1 heading
    section: str = ""  # KB subdirectory (arkweb, arkts, arkui, ui-design-kit)
    line_count: int = 0
    code_block_count: int = 0
    top_headings: list[str] = field(default_factory=list)
    top_apis: list[str] = field(default_factory=list)


@dataclass
class APIReference:
    """A documented API/interface reference."""

    name: str  # e.g., "registerJavaScriptProxy"
    file_name: str  # Which KB file documents it
    section_indices: list[int] = field(default_factory=list)
    code_block_indices: list[int] = field(default_factory=list)


@dataclass
class SearchIndex:
    """The complete searchable index of the knowledge base."""

    topics: dict[str, FileMeta]  # file_name → FileMeta
    sections: list[Section]
    code_blocks: list[CodeBlock]
    apis: dict[str, APIReference]  # API name → reference
    inverted: dict[str, list[int]]  # lowercase term → section indices
    code_inverted: dict[str, list[int]]  # lowercase term → code block indices
    build_time: str = ""
    source_file_count: int = 0
    total_lines: int = 0
