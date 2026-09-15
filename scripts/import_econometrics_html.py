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


CHAPTERS = {
    "1": {
        "directory": "ch01-foundations",
        "heading": "계량경제학의 구조",
        "introduction": "이 장은 회귀계수를 읽는 출발점으로서 **기술적 설명**, **인과적 해석**, **식별**, **추정**을 분리한다.",
        "roadmap": [
            "**1.1–1.2** 기술적 질문과 인과적 질문 · population, sample, target",
            "**1.3–1.4** CEF · BLP/BLA와 회귀계수의 기술적 해석",
            "**1.5–1.6** 식별가정 · 모형오류와 pseudo-true parameter",
            "**1.7–1.10** 표본 추정 · OLS · 계산 · 전체 논리",
        ],
        "sections": [
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
        ],
    },
    "2": {
        "directory": "ch02-probability-information",
        "heading": "확률모형, 정보집합, 그리고 자료배열",
        "introduction": "이 장은 **full data와 observed data**, **정보집합**, **조건부기대값**, **의존구조**, **empirical law**를 계량경제학의 확률언어로 연결한다.",
        "roadmap": [
            "**2.1–2.3** 확률모형 · 관측법칙 · population functionals",
            "**2.4–2.6** 정보집합 · 조건부기대값 · 독립성과 식별",
            "**2.7–2.9** support · 동적 정보 · 자료배열과 의존구조",
            "**2.10–2.11** empirical law · sample analogue · 연습문제",
        ],
        "sections": [
            ("s21", "2.1 경제적 세계를 확률모형으로 표현하기"),
            ("s22", "2.2 Full data와 observed data"),
            ("s23", "2.3 Distribution, expectation, population functionals"),
            ("s24", "2.4 Information과 σ-field"),
            ("s25", "2.5 Conditional expectation과 conditional law"),
            ("s26", "2.6 Independence, mean independence, conditional independence"),
            ("s27", "2.7 Support, versions, 그리고 observational content"),
            ("s28", "2.8 Dynamic information"),
            ("s29", "2.9 자료배열과 의존구조"),
            ("s210", "2.10 Population law에서 empirical law로"),
            ("s2110", "2.11 요약과 연습문제"),
            ("references", "참고문헌 및 다음 장"),
        ],
    },
    "3": {
        "directory": "ch03-target-model-identification",
        "heading": "Target, Model, and Identification",
        "introduction": "이 장은 **estimand**, **model restrictions**, **observational equivalence**, **point·set identification**을 구분하고 causal·moment model의 식별 논리를 연결한다.",
        "roadmap": [
            "**3.1–3.3** target · model · identified set의 일반적 정의",
            "**3.4–3.6** descriptive·causal identification · partial identification",
            "**3.7–3.9** moment/rank · weak identification · pseudo-true parameter",
            "**3.10–3.11** 식별·추정·최적화의 분리 · 연습문제",
        ],
        "sections": [
            ("s31", "3.1 무엇을 식별하려는가: Target, Parameter, Estimand"),
            ("s32", "3.2 Model은 무엇인가"),
            ("s33", "3.3 Identification의 일반적 정의"),
            ("s34", "3.4 Descriptive Targets와 Statistical Identification"),
            ("s35", "3.5 Causal Targets와 Causal Identification"),
            ("s36", "3.6 Observational Equivalence, Point Identification, Set Identification"),
            ("s37", "3.7 Moment Restrictions와 Rank Identification"),
            ("s38", "3.8 Global, Local, and Weak Identification"),
            ("s39", "3.9 Misspecification과 Pseudo-True Parameter"),
            ("s310", "3.10 Identification, Estimation, Optimization의 분리"),
            ("s3110", "3.11 요약과 연습문제"),
            ("references", "참고문헌 및 다음 장"),
        ],
    },
}


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


def build_index(chapter: str, metadata: dict[str, object], subtitle: str) -> str:
    section_links = "\n".join(
        f"- [{label}](contents.html#{anchor})" for anchor, label in metadata["sections"]
    )
    roadmap = "\n".join(f"- {item}" for item in metadata["roadmap"])
    return f"""# Chapter {int(chapter):02d} · {metadata["heading"]} {{.unnumbered}}
*{subtitle}*

{metadata["introduction"]} 아래 링크는 원본 본문의 해당 절로 이동한다.

## Chapter Map

::: {{.callout-note title="Reading Roadmap"}}
{roadmap}
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
    if len(sys.argv) != 3 or sys.argv[2] not in CHAPTERS:
        chapters = ", ".join(CHAPTERS)
        raise SystemExit(f"Usage: import_econometrics_html.py SOURCE.html CHAPTER ({chapters})")
    source_path = Path(sys.argv[1])
    chapter = sys.argv[2]
    metadata = CHAPTERS[chapter]
    title, subtitle, body = extract(source_path.read_text(encoding="utf-8"))
    root = Path(__file__).resolve().parents[1]
    target = root / "econometrics" / str(metadata["directory"])
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.qmd").write_text(build_index(chapter, metadata, subtitle), encoding="utf-8")
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
