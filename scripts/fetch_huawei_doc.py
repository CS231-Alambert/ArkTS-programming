#!/usr/bin/env python3
"""Fetch HarmonyOS developer docs via headless browser and convert to Markdown.

Huawei's developer docs are an Angular SPA — direct HTTP requests return
an empty <app-root>. This script uses Playwright to render the page,
extract article content, and convert it to clean Markdown matching the
existing ArkAgent KB format.

Usage:
    python3 fetch_huawei_doc.py --slug web-component-overview --section arkweb
    python3 fetch_huawei_doc.py --slug web-component-overview --section arkweb --dry-run
    python3 fetch_huawei_doc.py --batch urls.json
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag


# ── Configuration ──────────────────────────────────────────────────

BASE_URL = "https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/"
KB_ROOT = Path("/root/.cc-switch/skills/harmonyos-arkts/docs")

# UI artifacts to strip (standalone lines matching these patterns)
ARTIFACT_PATTERNS = [
    re.compile(r'^\s*(收起|展开)\s*$'),
    re.compile(r'^\s*自动换行\s*$'),
    re.compile(r'^\s*深色代码主题\s*$'),
    re.compile(r'^\s*复制\s*$'),
    re.compile(r'^\s*复制链接\s*$'),
    re.compile(r'^\s*举报\s*$'),
    re.compile(r'^\s*反馈\s*$'),
    re.compile(r'^\s*意见反馈\s*$'),
    re.compile(r'^\s*以上内容对您是否有帮助\?\s*$'),
    re.compile(r'^\s*如果您有其他疑问.*$'),
    re.compile(r'^\s*\*\s*$'),  # Lone asterisk (star rating widget)
    re.compile(r'^\s*社区提问\s*$'),
    re.compile(r'^\s*智能客服提问\s*$'),
]

# HTML elements to completely remove (Huawei UI chrome inside article)
REMOVE_CLASSES = [
    "copy-button", "code-theme", "code-expand", "feedback-btn",
    "theme-switch", "word-wrap-btn", "expand-btn", "collapse-btn",
    "report-btn",
]

# Selectors to try for finding the article content (in order)
CONTENT_SELECTORS = [
    ".markdown-body",
    "#mark .markdown-body",
    "article",
    ".document-content-html",
    "#document-content",
    ".doc-content",
]


# ── HTML → Markdown converter ──────────────────────────────────────

def html_to_markdown(html_content: str) -> str:
    """Convert article HTML to Markdown matching existing KB format."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove script and style tags
    for tag in soup.find_all(["script", "style", "noscript", "svg"]):
        tag.decompose()

    # Remove Angular comment nodes
    for comment in soup.find_all(string=lambda t: isinstance(t, str) and t.strip().startswith("<!---->")):
        comment.extract()

    # Remove known UI artifact elements by class
    for cls in REMOVE_CLASSES:
        for tag in soup.find_all(class_=re.compile(cls, re.I)):
            tag.decompose()

    # Remove elements that only contain artifact text
    for tag in soup.find_all(["span", "div", "button"]):
        text = tag.get_text(strip=True)
        if text in ("收起", "展开", "复制", "复制链接", "举报", "反馈",
                     "自动换行", "深色代码主题"):
            tag.decompose()

    lines = []
    _convert_node(soup, lines, depth=0)
    return _clean_output("\n".join(lines))


def _convert_node(node, lines: list[str], depth: int):
    """Recursively convert DOM nodes to Markdown lines."""
    if isinstance(node, NavigableString):
        text = str(node)
        if text.strip():
            lines.append(text)
        return

    if not isinstance(node, Tag):
        return

    tag_name = node.name.lower() if node.name else ""

    # ── Headings ──
    if tag_name in ("h1", "h2", "h3", "h4", "h5", "h6"):
        level = int(tag_name[1])
        # Skip H1 — KB format doesn't use H1
        if level == 1:
            return
        text = node.get_text(strip=True)
        if text:
            prefix = "#" * level
            lines.append(f"\n{prefix} {text}\n")
        return

    # ── Code blocks (pre) ──
    if tag_name == "pre":
        code_tag = node.find("code")
        lang = ""
        code_text = ""
        if code_tag:
            # Extract language from class if present
            classes = code_tag.get("class", [])
            if isinstance(classes, str):
                classes = classes.split()
            for cls in classes:
                if cls.startswith("language-") or cls.startswith("lang-"):
                    lang = cls.replace("language-", "").replace("lang-", "")
            code_text = code_tag.get_text()
        else:
            code_text = node.get_text()

        lines.append(f"\n```{lang}")
        # Preserve individual lines (may have line numbers from Huawei formatting)
        for line in code_text.splitlines():
            lines.append(line)
        lines.append("```\n")
        return

    # ── Inline code ──
    if tag_name == "code" and not _has_pre_parent(node):
        lines.append(f"`{node.get_text()}`")
        return

    # ── Paragraphs ──
    if tag_name == "p":
        text = node.get_text(strip=True)
        if text:
            lines.append(f"\n{text}\n")
        return

    # ── Lists ──
    if tag_name == "li":
        prefix = "  " * depth + "* "
        # Get direct text (before any nested lists)
        direct_text = ""
        for child in node.children:
            if isinstance(child, NavigableString):
                direct_text += str(child).strip()
            elif isinstance(child, Tag) and child.name in ("ul", "ol"):
                break  # Nested list handled below
        if direct_text:
            lines.append(prefix + direct_text)

        # Process children for nested lists
        for child in node.children:
            if isinstance(child, Tag) and child.name in ("ul", "ol"):
                _convert_node(child, lines, depth + 1)
            elif isinstance(child, Tag) and child.name == "p":
                _convert_node(child, lines, depth)
        return

    if tag_name in ("ul", "ol"):
        for child in node.children:
            if isinstance(child, Tag) and child.name == "li":
                _convert_node(child, lines, depth)
        lines.append("")  # Blank line after list
        return

    # ── Tables ──
    if tag_name == "table":
        _convert_table(node, lines)
        return

    # ── Images ──
    if tag_name == "img":
        src = node.get("src", "")
        alt = node.get("alt", "")
        if src:
            lines.append(f"\n![{alt}]({src})\n")
        return

    # ── Links ──
    if tag_name == "a":
        href = node.get("href", "")
        text = node.get_text(strip=True)
        if href and text:
            # Skip empty or javascript links
            if href.startswith("javascript:"):
                lines.append(text)
            else:
                lines.append(f"[{text}]({href})")
        elif text:
            lines.append(text)
        return

    # ── Emphasis ──
    if tag_name in ("strong", "b"):
        lines.append(f"**{node.get_text()}**")
        return
    if tag_name in ("em", "i"):
        lines.append(f"*{node.get_text()}*")
        return

    # ── Blockquotes ──
    if tag_name == "blockquote":
        text = node.get_text(strip=True)
        for line in text.splitlines():
            lines.append(f"> {line}")
        lines.append("")
        return

    # ── Horizontal rules ──
    if tag_name == "hr":
        lines.append("\n---\n")
        return

    # ── Line breaks ──
    if tag_name == "br":
        lines.append("")
        return

    # ── Divs / sections / spans — recurse into children ──
    for child in node.children:
        _convert_node(child, lines, depth)


def _has_pre_parent(node) -> bool:
    """Check if node has a <pre> ancestor."""
    parent = node.parent
    while parent:
        if isinstance(parent, Tag) and parent.name == "pre":
            return True
        parent = parent.parent
    return False


def _convert_table(table, lines: list[str]):
    """Convert HTML table to Markdown pipe table."""
    rows = table.find_all("tr")
    if not rows:
        return

    lines.append("")
    max_cols = 0
    table_data = []

    for row in rows:
        cells = row.find_all(["th", "td"])
        cell_texts = [cell.get_text(strip=True) for cell in cells]
        max_cols = max(max_cols, len(cell_texts))
        table_data.append(cell_texts)
        is_header = row.find("th") is not None

    # Header row
    if table_data:
        lines.append("| " + " | ".join(table_data[0]) + " |")
        lines.append("|" + "|".join(["---"] * max_cols) + "|")
        for row in table_data[1:]:
            # Pad to max_cols
            padded = row + [""] * (max_cols - len(row))
            lines.append("| " + " | ".join(padded) + " |")
    lines.append("")


def _clean_output(text: str) -> str:
    """Clean up the Markdown output."""
    # Remove standalone artifact lines (each pattern matches full lines)
    for pattern in ARTIFACT_PATTERNS:
        text = pattern.sub("", text)

    # Remove artifact sequences: consecutive artifact words on separate lines
    text = re.sub(
        r'\n\s*(收起|展开|自动换行|深色代码主题|复制|复制链接|举报|反馈)\s*\n',
        '\n', text,
    )

    # Collapse 3+ blank lines into 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove lines that are only non-breaking spaces or invisible chars
    text = re.sub(r'\n[ \t ​]+\n', '\n\n', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


# ── Playwright fetcher ──────────────────────────────────────────────

def fetch_page(slug: str, timeout: int = 30) -> tuple[str | None, bool]:
    """Fetch a Huawei doc page via Playwright, returning (article_html, is_index_page).

    Returns (None, False) on failure.
    is_index_page = True if the page has minimal content (<300 chars) and is likely a nav page.
    """
    from playwright.sync_api import sync_playwright

    url = BASE_URL + slug
    print(f"  Fetching: {url}", file=sys.stderr)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1440, "height": 900},
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)

            # Wait for Angular to render the content
            content_found = False
            for selector in CONTENT_SELECTORS:
                try:
                    page.wait_for_selector(selector, timeout=15000)
                    print(f"  Content found via: {selector}", file=sys.stderr)
                    content_found = True
                    break
                except Exception:
                    continue

            if not content_found:
                # Extra wait and retry
                time.sleep(3)
                for selector in CONTENT_SELECTORS:
                    try:
                        page.wait_for_selector(selector, timeout=5000)
                        print(f"  Content found via: {selector} (retry)", file=sys.stderr)
                        content_found = True
                        break
                    except Exception:
                        continue

            # Extra wait for Angular rendering to complete
            time.sleep(2)

            # Try JS-based extraction for more robust content finding
            content_html = None
            result = page.evaluate("""() => {
                const selectors = [
                    '.markdown-body', '#mark .markdown-body', '#mark', '.idpContent',
                    '.document-content', '[class*="doc-content"]', 'article',
                    'main', '[role="main"]'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el && el.textContent.trim().length > 100) {
                        return {selector: sel, html: el.innerHTML, length: el.innerHTML.length};
                    }
                }
                return {selector: null, html: '', length: 0};
            }""")
            if result['html'] and result['length'] > 100:
                content_html = result['html']
                print(f"  JS extracted {result['length']} chars via: {result['selector']}", file=sys.stderr)

            # Determine if this is an index page (very minimal content)
            is_index = not content_html or len(content_html) < 300

            return content_html, is_index

        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            return None, False
        finally:
            browser.close()


# ── CLI ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Fetch Huawei HarmonyOS docs and convert to Markdown")
    parser.add_argument("--slug", help="Document slug (e.g., web-component-overview)")
    parser.add_argument("--url", help="Full URL (overrides --slug)")
    parser.add_argument("--section", default="arkweb",
                        choices=["arkweb", "arkts", "arkui", "ui-design-kit"],
                        help="KB section subdirectory (default: arkweb)")
    parser.add_argument("--batch", help="Path to JSON file with [{\"slug\": \"...\", \"section\": \"...\"}, ...]")
    parser.add_argument("--out", help="Output file path (overrides auto-path)")
    parser.add_argument("--dry-run", action="store_true", help="Print to stdout instead of writing file")
    parser.add_argument("--delay", type=float, default=2.0,
                        help="Delay between batch requests in seconds (default: 2)")
    args = parser.parse_args()

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            items = json.load(f)
        _batch_fetch(items, args.delay, args.dry_run)
    elif args.slug or args.url:
        slug = args.slug or args.url.split("/")[-1]
        section = args.section
        _single_fetch(slug, section, args.out, args.dry_run, url=args.url)
    else:
        parser.print_help()
        sys.exit(1)


def _single_fetch(slug: str, section: str, out_path: str | None, dry_run: bool, url: str | None = None):
    """Fetch a single page and convert to MD."""
    content_html, is_index = fetch_page(slug)

    if not content_html:
        print(f"FAILED to fetch: {slug}", file=sys.stderr)
        sys.exit(1)

    if is_index:
        print(f"  ⚠️  Index page (minimal content)", file=sys.stderr)

    md = html_to_markdown(content_html)

    if dry_run:
        print(md)
        return

    if out_path:
        output = Path(out_path)
    else:
        output = KB_ROOT / section / f"{slug}.md"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(md, encoding="utf-8")
    print(f"  -> Saved: {output} ({len(md)} chars)", file=sys.stderr)


def _batch_fetch(items: list[dict], delay: float, dry_run: bool):
    """Fetch multiple pages in batch."""
    success = 0
    fail = 0
    for i, item in enumerate(items):
        slug = item["slug"]
        section = item.get("section", "arkweb")
        print(f"\n[{i+1}/{len(items)}] {section}/{slug}", file=sys.stderr)

        try:
            content_html, is_index = fetch_page(slug)
            if content_html:
                if is_index:
                    print(f"  ⚠️  Index page (links only, minimal prose)", file=sys.stderr)
                md = html_to_markdown(content_html)
                if dry_run:
                    print(f"  --- {section}/{slug} ({len(md)} chars) ---")
                    print(md[:500])
                else:
                    output = KB_ROOT / section / f"{slug}.md"
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text(md, encoding="utf-8")
                    print(f"  -> Saved: {output} ({len(md)} chars)", file=sys.stderr)
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(f"  ERROR [{section}/{slug}]: {e}", file=sys.stderr)
            fail += 1

        if i < len(items) - 1:
            time.sleep(delay)

    print(f"\n--- Batch complete: {success} OK, {fail} FAILED, {len(items)} total ---", file=sys.stderr)


if __name__ == "__main__":
    main()
