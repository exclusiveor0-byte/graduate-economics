"""Import the replacement standalone macroeconomics chapter HTML files.

Each source file contains one self-contained ``<article class="note-content">``.
The importer keeps the article body, MathJax delimiters, tables, exercises, and
reference lists while placing each chapter in a stable semantic directory.
"""

from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CHAPTERS = [
    ("00", "chapter00_restructured.html", "ch00-foundations"),
    ("01", "chapter01_restructured.html", "ch01-constrained-optimization"),
    ("02", "chapter02_restructured.html", "ch02-continuous-time-dynamics"),
    ("03", "chapter03_restructured_fixed.html", "ch03-dynamic-programming"),
    ("04", "chapter04_restructured.html", "ch04-two-period-macro"),
    ("05", "chapter05_restructured_fixed.html", "ch05-solow-swan"),
    ("06", "chapter06_restructured.html", "ch06-infinite-horizon-consumption"),
    ("07", "chapter07_restructured.html", "ch07-ramsey-cks"),
    ("08", "chapter08_restructured.html", "ch08-endogenous-growth"),
    ("09", "chapter09_restructured.html", "ch09-growth-accounting"),
    ("10", "chapter10_restructured.html", "ch10-stochastic-dynamics"),
    ("11", "chapter11_restructured.html", "ch11-complete-markets"),
    ("12", "chapter12_restructured.html", "ch12-incomplete-markets"),
    ("13", "chapter13_restructured.html", "ch13-business-cycle-facts"),
    ("14", "chapter14_restructured.html", "ch14-linear-rational-expectations"),
    ("15", "chapter15_restructured.html", "ch15-real-business-cycles"),
]


def plain(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return " ".join(html.unescape(fragment).split())


def html_to_quarto_markdown(body: str) -> str:
    quarto = os.environ.get("QUARTO_BIN") or shutil.which("quarto") or "quarto"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as source:
        source.write(body)
        source_path = Path(source.name)
    try:
        result = subprocess.run(
            [quarto, "pandoc", "--from=html+tex_math_single_backslash", "--to=markdown", str(source_path)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        source_path.unlink(missing_ok=True)
    return result.stdout.strip()


def extract(source: str, chapter_id: str) -> tuple[str, str, str]:
    title_match = re.search(r"<h1>(.*?)</h1>", source, re.S)
    subtitle_match = re.search(r'<p class="subtitle">(.*?)</p>', source, re.S)
    article_match = re.search(
        r'<article[^>]*class="[^"]*(?:note-content|article)[^"]*"[^>]*>(.*?)</article>',
        source,
        re.S,
    )
    if not title_match or not article_match:
        raise ValueError(f"Could not locate title/body for chapter {chapter_id}")
    title = plain(title_match.group(1))
    subtitle = plain(subtitle_match.group(1)) if subtitle_match else ""
    body = article_match.group(1).strip()
    body = re.sub(
        r"\\\((.*?)\\\)",
        lambda match: r"\(" + match.group(1).replace("[", "&#91;").replace("]", "&#93;") + r"\)",
        body,
        flags=re.S,
    )
    return title, subtitle, html_to_quarto_markdown(body)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: import_macro_restructured.py SOURCE_DIRECTORY")
    source_root = Path(sys.argv[1])
    target_root = Path(__file__).resolve().parents[1] / "macroeconomics"
    for chapter_id, filename, directory in CHAPTERS:
        source_path = source_root / filename
        if not source_path.exists():
            raise FileNotFoundError(source_path)
        title, subtitle, body = extract(source_path.read_text(encoding="utf-8"), chapter_id)
        target = target_root / directory
        target.mkdir(parents=True, exist_ok=True)
        display_title = f"Chapter {chapter_id} · {title}"
        (target / "index.qmd").write_text(
            f"# {display_title} {{.unnumbered}}\n\n"
            f"{subtitle or title}\n\n"
            "이 장은 새 거시경제학 강의노트에서 마이그레이션했습니다. "
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
            "<!-- 새 거시경제학 노트를 보존한 마이그레이션. 공유 CSS는 styles/macro-content.scss에서 관리합니다. -->\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        print(f"Chapter {chapter_id}: {title} -> {directory}")


if __name__ == "__main__":
    main()
