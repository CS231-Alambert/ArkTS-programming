#!/usr/bin/env python3
"""
Clean Huawei developer doc HTML before markitdown conversion.

Extracts only the documentation content from Angular SPA HTML pages,
stripping navigation, sidebars, footers, and non-content noise.

Usage:
    python clean-markdown.py input.html > cleaned.html
    python clean-markdown.py input.html -o cleaned.html
    python clean-markdown.py --batch /path/to/html/dir/ --out /path/to/output/
"""

import argparse
import sys
import os
import re
from pathlib import Path

try:
    from bs4 import BeautifulSoup, Tag, NavigableString
except ImportError:
    print("ERROR: beautifulsoup4 required. Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)


# CSS selectors for content containers (tried in order)
CONTENT_SELECTORS = [
    '.markdown-body',
    '.document-content',
    '.doc-content',
    'article',
    'main .content',
    'main',
]

# Elements to remove even within content
REMOVE_SELECTORS = [
    '.feedback-section',
    '.doc-feedback',
    '.pagination-nav',
    '.breadcrumb',
    '.header-anchor',
    'script',
    'style',
    'noscript',
    '.copy-btn',
    '.code-block-header',
]

# Sections to remove by heading text
REMOVE_HEADINGS = [
    '意见反馈',
    '相关推荐',
    '本文导读',
]


def find_content(soup: BeautifulSoup) -> Tag | None:
    """Find the main documentation content container."""
    for selector in CONTENT_SELECTORS:
        el = soup.select_one(selector)
        if el is not None:
            return el
    return None


def clean_content(content: Tag) -> str:
    """Extract and clean the documentation content."""
    # Remove unwanted elements
    for selector in REMOVE_SELECTORS:
        for el in content.select(selector):
            el.decompose()

    # Remove "意见反馈" and similar sections
    for heading in content.find_all(['h2', 'h3']):
        text = heading.get_text(strip=True)
        if text in REMOVE_HEADINGS:
            # Remove heading and all siblings until next heading
            current = heading
            while current is not None:
                next_node = current.find_next_sibling()
                current.decompose()
                current = next_node
                if current is not None and current.name in ('h2', 'h3'):
                    break

    # Remove empty divs (Angular noise)
    for div in content.find_all('div'):
        if not div.get_text(strip=True) and not div.find('img'):
            div.decompose()

    # Remove Angular-specific attributes
    for tag in content.find_all(True):
        attrs_to_remove = [k for k in tag.attrs if k.startswith('_ng') or k.startswith('ng-')]
        for attr in attrs_to_remove:
            del tag[attr]

    # Normalize internal links
    for a in content.find_all('a', href=True):
        href = a.get('href', '')
        if href.startswith('/consumer/cn/doc/harmonyos-guides/'):
            # Extract slug from URL
            slug = href.replace('/consumer/cn/doc/harmonyos-guides/', '').split('?')[0].split('#')[0]
            a['href'] = f'{slug}.md'
        elif href.startswith('/consumer/cn/doc/'):
            slug = href.replace('/consumer/cn/doc/', '').replace('/', '-')
            a['href'] = f'{slug}.md'

    # Preserve code blocks with language hints
    for pre in content.find_all('pre'):
        code = pre.find('code')
        if code is not None:
            classes = code.get('class', [])
            lang = None
            if isinstance(classes, list):
                for c in classes:
                    if c.startswith('language-'):
                        lang = c.replace('language-', '')
                        break
            if lang:
                code['data-lang'] = lang
            elif 'typescript' in code.get_text()[:100].lower() or 'import' in code.get_text()[:100]:
                code['data-lang'] = 'typescript'

    return str(content)


def extract_metadata(html_path: str, soup: BeautifulSoup) -> dict:
    """Extract document metadata from HTML."""
    meta = {
        'source_file': os.path.basename(html_path),
    }

    # Try <meta name="version">
    version_tag = soup.find('meta', attrs={'name': 'version'})
    if version_tag:
        meta['doc_version'] = version_tag.get('content', '')

    # Try <title>
    title_tag = soup.find('title')
    if title_tag:
        title = title_tag.get_text(strip=True)
        # Clean up the title — remove "文档中心" suffix
        title = title.replace('文档中心', '').strip()
        if title:
            meta['page_title'] = title

    # Try to find the actual page heading
    content = find_content(soup)
    if content:
        h1 = content.find('h1')
        if h1:
            meta['heading'] = h1.get_text(strip=True)

    return meta


def generate_frontmatter(meta: dict) -> str:
    """Generate YAML frontmatter."""
    lines = ['---']
    lines.append(f"title: \"{meta.get('heading', meta.get('page_title', 'Unknown'))}\"")
    lines.append(f"source: \"{meta.get('source_file', '')}\"")
    if 'doc_version' in meta:
        lines.append(f"doc_version: \"{meta['doc_version']}\"")
    lines.append(f"kit: \"ArkWeb\"")
    lines.append('---')
    lines.append('')
    return '\n'.join(lines)


def process_file(html_path: str) -> str | None:
    """Process a single HTML file and return cleaned content."""
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    content = find_content(soup)
    if content is None:
        print(f"  ⚠ No content container found in {html_path}", file=sys.stderr)
        return None

    cleaned = clean_content(content)

    # Check if there's actual content
    text_only = BeautifulSoup(cleaned, 'html.parser').get_text(strip=True)
    if len(text_only) < 100:
        print(f"  ⚠ Content too short ({len(text_only)} chars): {html_path}", file=sys.stderr)
        return None

    return cleaned


def main():
    parser = argparse.ArgumentParser(description='Clean Huawei developer doc HTML')
    parser.add_argument('input', nargs='?', help='Input HTML file')
    parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    parser.add_argument('--batch', help='Batch process a directory of HTML files')
    parser.add_argument('--out', help='Output directory for batch mode', default='.')
    parser.add_argument('--no-frontmatter', action='store_true', help='Skip YAML frontmatter')
    args = parser.parse_args()

    if args.batch:
        html_dir = Path(args.batch)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        html_files = sorted(html_dir.glob('*.html'))
        print(f"Processing {len(html_files)} HTML files...")

        success = 0
        for html_file in html_files:
            print(f"  {html_file.name}...", end=' ')
            cleaned = process_file(str(html_file))
            if cleaned is None:
                print("SKIPPED")
                continue

            # Write cleaned HTML for markitdown
            out_path = out_dir / html_file.with_suffix('.cleaned.html').name
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(cleaned)

            file_size = out_path.stat().st_size
            print(f"OK ({file_size} bytes)")
            success += 1

        print(f"\nDone: {success}/{len(html_files)} files extracted")
        return

    if not args.input:
        parser.print_help()
        sys.exit(1)

    cleaned = process_file(args.input)
    if cleaned is None:
        sys.exit(1)

    output = cleaned
    if not args.no_frontmatter:
        with open(args.input, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        meta = extract_metadata(args.input, soup)
        output = generate_frontmatter(meta) + cleaned

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Written: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
