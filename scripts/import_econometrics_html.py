"""Convert a self-contained econometrics chapter HTML article to Quarto Markdown.

The source notes use semantic section ids and presentational class names.  This
small importer keeps both: headings become Quarto headings (and therefore
participate in the page TOC), while the existing classes become fenced-div
attributes consumed by styles/econometrics-content.scss.
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path


def attributes(tag: str) -> str:
    parts: list[str] = []
    id_match = re.search(r'\bid="([^"]+)"', tag)
    class_match = re.search(r'\bclass="([^"]+)"', tag)
    if id_match:
        parts.append(f"#{id_match.group(1)}")
    if class_match:
        parts.extend(f".{name}" for name in class_match.group(1).split())
    return " ".join(parts) or ".import-block"


def headings(source: str) -> str:
    def h2(match: re.Match[str]) -> str:
        text = re.sub(r'<span class="section-number">(.*?)</span>', r'[\1]{.section-number}', match.group(1))
        return f"\n## {text.strip()}\n"

    def hx(level: int):
        def convert(match: re.Match[str]) -> str:
            anchor = re.search(r'\bid="([^"]+)"', match.group(1))
            suffix = f" {{#{anchor.group(1)}}}" if anchor else ""
            return f"\n{'#' * level} {match.group(2).strip()}{suffix}\n"

        return convert

    source = re.sub(r'<h2[^>]*>(.*?)</h2>', h2, source, flags=re.S)
    source = re.sub(r'<h3([^>]*)>(.*?)</h3>', hx(3), source, flags=re.S)
    source = re.sub(r'<h4([^>]*)>(.*?)</h4>', hx(4), source, flags=re.S)
    return source


def convert(source: str) -> str:
    article = re.search(r'<article class="note-content">(.*?)</article>', source, flags=re.S)
    if not article:
        raise ValueError("Could not find <article class=\"note-content\"> in source HTML")

    text = headings(article.group(1))

    # The source files use MathJax's LaTeX delimiters. Pandoc's Markdown
    # reader handles dollar delimiters reliably inside imported fenced divs.
    # Unescape HTML entities inside math expressions.
    def unescape_display_math(match: re.Match[str]) -> str:
        content = html.unescape(match.group(1).strip())
        return f"\n$$\n{content}\n$$\n"

    def unescape_inline_math(match: re.Match[str]) -> str:
        content = html.unescape(match.group(1))
        return f"${content}$"

    text = re.sub(r"(?<!\\)\\\[(.*?)(?<!\\)\\\]", unescape_display_math, text, flags=re.S)
    text = re.sub(r"\\\((.*?)\\\)", unescape_inline_math, text, flags=re.S)

    def section_open(match: re.Match[str]) -> str:
        attrs = attributes(match.group(0))
        return f"\n\n:::::::::::::::::::::::::: {{{attrs}}}\n\n"

    text = re.sub(r'<section\b[^>]*>', section_open, text)
    text = text.replace("</section>", "\n\n::::::::::::::::::::::::::\n\n")

    div_stack: list[str] = []

    def div_open(match: re.Match[str]) -> str:
        # Quarto requires every nested fence to be shorter than its parent.
        # The source documents are shallowly nested; a generous descending
        # sequence also remains safely inside the long section fence above.
        fence = ":" * (20 - len(div_stack))
        div_stack.append(fence)
        attrs = attributes(match.group(0))
        return f"\n\n{fence} {{{attrs}}}\n\n"

    def div_close(_: re.Match[str]) -> str:
        if not div_stack:
            return "</div>"
        return f"\n\n{div_stack.pop()}\n\n"

    def div_tag(match: re.Match[str]) -> str:
        return div_close(match) if match.group(0) == "</div>" else div_open(match)

    text = re.sub(r'<div\b[^>]*>|</div>', div_tag, text)
    if div_stack:
        raise ValueError("Unclosed <div> tags in source HTML")

    # Keep classed paragraphs as fenced divs so SCSS styles them
    def classed_p(match: re.Match[str]) -> str:
        cls = match.group(1)
        content = match.group(2).strip()
        return f"\n::: {{.{cls}}}\n{content}\n:::\n"

    text = re.sub(r'<p class="([^"]+)">(.*?)</p>', classed_p, text, flags=re.S)

    text = re.sub(r'<p(?:\s[^>]*)?>', "\n", text)
    text = text.replace("</p>", "\n")
    text = re.sub(r'<!--.*?-->', "", text, flags=re.S)
    text = re.sub(r'\n{3,}', "\n\n", text)
    return text.strip() + "\n"


def main() -> None:
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        raise SystemExit("Usage: import_econometrics_html.py SOURCE_HTML OUTPUT_QMD TITLE [DESCRIPTION]")
    source, output = map(Path, sys.argv[1:3])
    converted = convert(source.read_text(encoding="utf-8"))
    desc_line = f'description: "{sys.argv[4]}"\n' if len(sys.argv) == 5 else ""
    Path(output).write_text(
        f'---\ntitle: "{sys.argv[3]}"\n{desc_line}---\n\n'
        "<!-- 원본 HTML의 section id와 설명 요소를 보존한 마이그레이션. 공유 CSS는 styles/econometrics-content.scss에서 관리한다. -->\n\n"
        + converted,
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
