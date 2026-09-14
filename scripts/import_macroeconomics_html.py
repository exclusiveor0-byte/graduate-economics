"""Import the user-supplied macroeconomics lecture-note HTML into chapter pages.

The original document has one book-document section per chapter. This importer
preserves every article body as local HTML inside a QMD page, including its
MathJax delimiters, tables, exercises, and reference lists. It uses only the
Python standard library and does not copy source CSS or scripts, since the
Quarto book supplies its own shared presentation layer.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

CHAPTERS = [
    ("ch00", "ch00-macro-map", "Chapter 00 · 거시경제학의 지도"),
    ("ch01", "ch01-solow-growth", "Chapter 01 · 성장사실과 Solow 모형"),
    ("ch02", "ch02-ramsey-olg", "Chapter 02 · 내생적 저축과 세대구조"),
    ("ch03", "ch03-endogenous-growth", "Chapter 03 · 지식축적과 내생적 성장"),
    ("ch04", "ch04-development-accounting", "Chapter 04 · 국가 간 소득격차"),
    ("ch05", "ch05-real-business-cycles", "Chapter 05 · 실물경기변동"),
    ("ch06", "ch06-nominal-rigidity", "Chapter 06 · 명목경직성"),
    ("ch07", "ch07-new-keynesian-dsge", "Chapter 07 · New Keynesian DSGE"),
    ("ch08", "ch08-monetary-policy", "Chapter 08 · 통화정책"),
    ("ch09", "ch09-consumption-risk", "Chapter 09 · 소비·저축·위험"),
    ("ch10", "ch10-investment", "Chapter 10 · 투자수요"),
    ("ch11", "ch11-complete-markets", "Chapter 11 · 완전시장"),
    ("ch12", "ch12-financial-frictions", "Chapter 12 · 금융마찰과 금융위기"),
    ("ch13", "ch13-incomplete-markets", "Chapter 13 · 불완전시장과 부의 분포"),
    ("appA", "appendix-a-dynamic-optimization", "Appendix A · 동태최적화와 재귀적 방법"),
    ("appB", "appendix-b-linear-rational-expectations", "Appendix B · 선형 합리적 기대모형"),
    ("appC", "appendix-c-perturbation", "Appendix C · 섭동법과 고차근사"),
    ("appD", "appendix-d-business-cycle-measurement", "Appendix D · 경기변동 측정과 모형평가"),
    ("appE", "appendix-e-growth-empirics", "Appendix E · 성장회계와 성장실증"),
]


def plain(fragment: str) -> str:
    fragment = re.sub(r"<br\\s*/?>", ": ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return " ".join(html.unescape(fragment).split())


def html_to_quarto_markdown(body: str) -> str:
    """Convert source HTML while preserving MathJax TeX as Quarto math."""
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as source:
        source.write(body)
        source_path = Path(source.name)
    try:
        result = subprocess.run(
            [
                "quarto", "pandoc", "--from=html+tex_math_single_backslash",
                "--to=markdown", str(source_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        source_path.unlink(missing_ok=True)
    return result.stdout.strip()


def document_blocks(source: str) -> dict[str, str]:
    marker = re.compile(r'<section class="book-document" id="([^"]+)"')
    matches = list(marker.finditer(source))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source)
        blocks[match.group(1)] = source[match.start() : end]
    return blocks


def extract(block: str, chapter_id: str) -> tuple[str, str, str]:
    title_match = re.search(r"<h1>(.*?)</h1>", block, re.S)
    subtitle_match = re.search(r'<p class="subtitle">(.*?)</p>', block, re.S)
    article_match = re.search(
        r'<article[^>]*class="[^"]*(?:note-content|article)[^"]*"[^>]*>(.*?)</article>',
        block,
        re.S,
    )
    if not title_match or not article_match:
        raise ValueError(f"Could not locate title/body for {chapter_id}")
    title = plain(title_match.group(1))
    subtitle = plain(subtitle_match.group(1)) if subtitle_match else ""
    body = article_match.group(1).strip()
    # Pandoc otherwise interprets square brackets inside inline TeX in raw table
    # cells as Markdown links. HTML entities survive to the browser and are
    # decoded before MathJax reads the expression.
    body = re.sub(
        r"\\\((.*?)\\\)",
        lambda match: r"\(" + match.group(1).replace("[", "&#91;").replace("]", "&#93;") + r"\)",
        body,
        flags=re.S,
    )
    return title, subtitle, html_to_quarto_markdown(body)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: import_macroeconomics_html.py SOURCE.html")
    source = Path(sys.argv[1]).read_text(encoding="utf-8")
    blocks = document_blocks(source)
    target_root = Path(__file__).resolve().parents[1] / "macroeconomics"
    for chapter_id, directory, fallback_title in CHAPTERS:
        if chapter_id not in blocks:
            raise ValueError(f"Source is missing {chapter_id}")
        title, subtitle, body = extract(blocks[chapter_id], chapter_id)
        target = target_root / directory
        target.mkdir(parents=True, exist_ok=True)
        (target / "index.qmd").write_text(
            f"# {fallback_title} {{.unnumbered}}\n\n{subtitle or title}\n\n"
            "이 장은 원본 통합 강의노트에서 마이그레이션했습니다. "
            "[본문 전체 읽기](contents.qmd)\n",
            encoding="utf-8",
        )
        (target / "contents.qmd").write_text(
            "---\n"
            "title: >-\n"
            f"  {title}\n"
            "description: >-\n"
            f"  {subtitle or title}\n"
            "---\n\n"
            "<!-- 원본 본문을 보존한 마이그레이션. 공유 CSS는 styles/macro-content.scss에서 관리합니다. -->\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        print(f"{chapter_id}: {title} -> {target.relative_to(target_root)}")


if __name__ == "__main__":
    main()
