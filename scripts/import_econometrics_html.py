"""Import an econometrics chapter supplied as a standalone HTML lecture note.

The importer keeps the article body, headings, equations, tables, exercises,
and semantic CSS classes while discarding the source page's scripts and visual
chrome. Quarto supplies the shared book navigation and styles.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path


SECTIONS = [
    ("s11", "1.1 Description과 Causality: 계량경제학의 첫 번째 구분"),
    ("s12", "1.2 Population, sample, target: 두 해석을 담는 공통 언어"),
    ("s13", "1.3 Conditional Expectation Function: descriptive regression의 기준점"),
    ("s14", "1.4 Best Linear Predictor와 Best Linear Approximation: 회귀계수의 기본 해석"),
    ("s15", "1.5 Identification: descriptive object에서 causal interpretation으로"),
    ("s16", "1.6 Exact model, misspecification, 그리고 pseudo-true parameter"),
    ("s17", "1.7 Population problem에서 sample problem으로"),
    ("s18", "1.8 OLS를 다시 읽기: descriptive baseline, causal special case"),
    ("s19", "1.9 Optimization과 numerical analysis는 어디에 위치하는가?"),
    ("s110", "1.10 전체 흐름: 먼저 기술하고, 그 다음 인과를 식별한다"),
    ("references", "참고문헌 및 다음 장"),
]


def plain(fragment: str) -> str:
    fragment = re.sub(r"<br\s*/?>", ": ", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", "", fragment)
    return " ".join(html.unescape(fragment).split())


def html_to_markdown(body: str) -> str:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".html", delete=False) as source:
        source.write(body)
        source_path = Path(source.name)
    try:
        result = subprocess.run(
            ["quarto", "pandoc", "--from=html+tex_math_single_backslash", "--to=markdown", str(source_path)],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    finally:
        source_path.unlink(missing_ok=True)
    return result.stdout.strip()


def extract(source: str) -> tuple[str, str, str]:
    title_match = re.search(r"<h1>(.*?)</h1>", source, re.S)
    subtitle_match = re.search(r'<p class="subtitle">(.*?)</p>', source, re.S)
    article_match = re.search(r'<article class="note-content">(.*?)</article>', source, re.S)
    if not title_match or not article_match:
        raise ValueError("Could not locate the chapter title or article body.")
    # The supplied source has one malformed HTML fragment in the overlap
    # condition. Restore the intended probability statement before Pandoc
    # parses it, so the formula is not silently truncated during migration.
    body = re.sub(
        r'<div class="math-display">\s*\\\[\s*'
        r'Y=DY\(1\)\+\(1-D\)Y\(0\),\\qquad \(Y\(1\),Y\(0\)\)\\perp D\\mid X,\s*\\\]\s*'
        r'\\\[\s*0<p\(d=1\\mid .*?</div>',
        lambda _: '<div class="math-display">\\[\n'
        '\\begin{gathered}\n'
        'Y=DY(1)+(1-D)Y(0),\\qquad (Y(1),Y(0))\\perp D\\mid X,\\\\\n'
        '0 < P(D=1\\mid X=x) < 1.\n'
        '\\end{gathered}\n'
        '\\]\n</div>',
        article_match.group(1).strip(),
        flags=re.S,
    )
    title = plain(title_match.group(1))
    subtitle = plain(subtitle_match.group(1)) if subtitle_match else title
    return title, subtitle, html_to_markdown(body)


def build_index(title: str, subtitle: str) -> str:
    section_links = "\n".join(f"- [{label}](contents.html#{anchor})" for anchor, label in SECTIONS)
    return f"""# Chapter 01 · 계량경제학의 구조 {{.unnumbered}}
*{subtitle}*

이 장은 회귀계수를 읽는 출발점으로서 **기술적 설명**, **인과적 해석**,
**식별**, **추정**을 분리한다. 아래 링크는 원본 본문의 해당 절로 이동한다.

## Chapter Map

::: {{.callout-note title="Reading Roadmap"}}
- **1.1–1.2** 기술적 질문과 인과적 질문 · population, sample, target
- **1.3–1.4** CEF · BLP/BLA와 회귀계수의 기술적 해석
- **1.5–1.6** 식별가정 · 모형오류와 pseudo-true parameter
- **1.7–1.10** 표본 추정 · OLS · 계산 · 전체 논리
:::

## Sections

{section_links}

::: {{.callout-tip title="본문 읽기"}}
수식·표·연습문제는 원본 구조를 보존한 [본문 전체](contents.html)에 있습니다.
위의 Section 링크로 바로 이동하거나 순서대로 읽을 수 있습니다.
:::

::: {{.callout-tip title="협업 단위"}}
본문 수정 제안에는 해당 Section의 제목과 앵커를 Pull Request에 함께 적어 주세요.
:::
"""


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: import_econometrics_html.py SOURCE.html")
    source_path = Path(sys.argv[1])
    title, subtitle, body = extract(source_path.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    target = root / "econometrics" / "ch01-foundations"
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.qmd").write_text(build_index(title, subtitle), encoding="utf-8")
    (target / "contents.qmd").write_text(
        "---\n"
        f"title: \"{title}\"\n"
        f"description: \"{subtitle}\"\n"
        "---\n\n"
        "<!-- 원본 본문을 보존한 마이그레이션. 공유 CSS는 styles/econometrics-content.scss에서 관리합니다. -->\n\n"
        f"{body}\n",
        encoding="utf-8",
    )
    print(f"{title} -> {target.relative_to(root)}")


if __name__ == "__main__":
    main()
