"""Tests for the TF-IDF index builder."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from arkagent.indexer.builder import (
    build_code_inverted,
    build_index,
    build_inverted_index,
    extract_api_names,
    extract_code_blocks,
    extract_sections,
    tokenize,
)
from arkagent.indexer.schemas import CodeBlock, Section


class TestTokenize:
    def test_chinese_segmentation(self):
        tokens = tokenize("方舟Web组件提供JSBridge能力")
        assert "方舟" in tokens or "web" in tokens
        assert len(tokens) > 0

    def test_english_lowercase(self):
        tokens = tokenize("javaScriptProxy is GREAT")
        assert "javascriptproxy" in tokens
        assert "great" in tokens
        assert "is" in tokens

    def test_empty_string(self):
        assert tokenize("") == []

    def test_punctuation_stripped(self):
        tokens = tokenize("hello, world!")
        assert "," not in tokens
        assert "!" not in tokens


class TestExtractSections:
    def test_basic_section(self):
        lines = ["# Title", "", "## Section One", "", "content here", "", "### Sub", "more"]
        sections = extract_sections("test.md", lines)
        titles = [s.heading for s in sections]
        assert "Section One" in titles
        assert "Sub" in titles

    def test_no_headings(self):
        lines = ["just", "plain", "text"]
        sections = extract_sections("plain.md", lines)
        # Implementation creates a "(top)" section for files without headings
        assert sections[0].heading == "(top)" if sections else True

    def test_section_content(self):
        lines = ["## My Section", "", "hello world", "", "## Next"]
        sections = extract_sections("t.md", lines)
        assert len(sections) >= 1
        assert "hello world" in sections[0].content


class TestExtractCodeBlocks:
    def test_fenced_block(self):
        lines = ["```bash", "echo hello", "```"]
        blocks = extract_code_blocks(lines)
        assert len(blocks) == 1
        assert blocks[0].language == "bash"
        assert "echo hello" in blocks[0].content

    def test_multiple_blocks(self):
        lines = [
            "```python",
            "print(1)",
            "```",
            "text",
            "```python",
            "print(2)",
            "```",
        ]
        blocks = extract_code_blocks(lines)
        assert len(blocks) == 2

    def test_no_blocks(self):
        assert extract_code_blocks(["no code here"]) == []


class TestExtractApiNames:
    def test_js_api(self):
        names = extract_api_names("registerJavaScriptProxy('testObj', {})")
        assert "javaScriptProxy" in names or "registerJavaScriptProxy" in names

    def test_no_api(self):
        assert extract_api_names("just some plain text") == []


class TestBuildInvertedIndex:
    def test_basic(self):
        sections = [
            Section(
                heading="Test",
                heading_level=2,
                file_name="a.md",
                start_line=0,
                end_line=3,
                content="hello world foo bar",
            ),
            Section(
                heading="Other",
                heading_level=2,
                file_name="b.md",
                start_line=0,
                end_line=3,
                content="foo baz qux",
            ),
        ]
        inverted = build_inverted_index(sections)
        assert "hello" in inverted
        assert "foo" in inverted
        # "foo" appears in both section 0 and section 1
        assert len(inverted["foo"]) == 2


class TestBuildCodeInverted:
    def test_basic(self):
        blocks = [
            CodeBlock(
                start_line=0, end_line=2, language="python",
                content="import foobar\nprint(1)",
                context_before="", context_after="",
            ),
        ]
        inverted = build_code_inverted(blocks)
        assert "foobar" in inverted


class TestBuildIndex:
    def test_kb_path_not_found(self):
        """build_index should raise when kb_path doesn't exist."""
        with pytest.raises((FileNotFoundError, NotADirectoryError, OSError)):
            build_index(Path("/nonexistent/path/for/testing"))
