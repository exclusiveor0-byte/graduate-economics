"""Build overview pages for imported macroeconomics chapters and appendices.

The imported lecture notes intentionally keep each chapter body in one
``contents.qmd`` file.  This utility gives that body a lightweight entry page:
an introduction, a reading roadmap, and stable links to every top-level
section.  Run it after adding, removing, or renaming a top-level section.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "macroeconomics"
SKIP_DIRECTORIES = {"ch00-macro-map"}
SECTION = re.compile(
    r"^:+\s+\{#(?P<anchor>[A-Za-z0-9_-]+)\s+\.section\}\s*$"
    r"\n^##\s+(?P<title>.+?)\s*$",
    re.MULTILINE,
)


@dataclass(frozen=True)
class Entry:
    anchor: str
    title: str


def clean_title(value: str) -> str:
    """Convert a Quarto heading into link text without its formatting marks."""
    value = re.sub(r"\{[^}]+\}", " ", value)
    value = value.replace("[", "").replace("]", "")
    return " ".join(value.split())


def chapter_title(index: Path) -> str:
    first_line = index.read_text(encoding="utf-8").splitlines()[0]
    return clean_title(re.sub(r"^#\s+", "", first_line))


def chapter_subtitle(contents: str) -> str:
    match = re.search(r"^description:\s*>-\s*$\n^\s{2}(?P<text>.+)$", contents, re.MULTILINE)
    return match.group("text").strip() if match else ""


def entries(contents: str) -> list[Entry]:
    return [Entry(match.group("anchor"), clean_title(match.group("title"))) for match in SECTION.finditer(contents)]


def topic_from(title: str) -> str:
    return title.split("·", maxsplit=1)[-1].strip()


def section_number(title: str) -> str:
    match = re.match(r"([A-Z]?\.?\d+(?:\.\d+)*)\s", title)
    return match.group(1) if match else ""


def without_section_number(title: str) -> str:
    return re.sub(r"^[A-Z]?\.?\d+(?:\.\d+)*\s+", "", title)


def roadmap(entries_: list[Entry]) -> list[str]:
    """Make three or four compact reading ranges from the chapter sections."""
    core = [
        entry
        for entry in entries_
        if entry.title not in {"Learning Check", "핵심 용어", "참조 문헌"}
    ]
    if not core:
        return []
    groups = 4 if len(core) > 15 else 3
    groups = min(groups, len(core))
    base, extra = divmod(len(core), groups)
    result: list[str] = []
    cursor = 0
    for group_index in range(groups):
        width = base + (1 if group_index < extra else 0)
        chunk = core[cursor : cursor + width]
        cursor += width
        first, last = chunk[0], chunk[-1]
        first_number, last_number = section_number(first.title), section_number(last.title)
        if first_number and last_number:
            span = first_number if first_number == last_number else f"{first_number}–{last_number}"
        elif first_number:
            span = f"{first_number} 및 {last.title}"
        else:
            span = first.title
        if span:
            result.append(
                f"- **{span}** {without_section_number(first.title)}"
                f" · {without_section_number(last.title)}"
            )
        else:
            result.append(f"- **{first.title}**")
    return result


def overview(title: str, subtitle: str, entries_: list[Entry]) -> str:
    topic = topic_from(title)
    subtitle_line = f"*{subtitle}*\n\n" if subtitle else ""
    section_links = "\n".join(
        f"- [{entry.title}](contents.html#{entry.anchor})" for entry in entries_
    )
    map_lines = "\n".join(roadmap(entries_))
    return (
        f"# {title} {{.unnumbered}}\n"
        f"{subtitle_line}"
        f"이 장에서는 **{topic}**의 핵심 질문, 모형의 구성, 주요 결과와 한계를 "
        "순서대로 검토합니다. 아래 Section 링크는 원본 통합 본문의 해당 위치로 이동합니다.\n\n"
        "## Chapter Map\n\n"
        "::: {.callout-note title=\"Reading Roadmap\"}\n"
        f"{map_lines}\n"
        ":::\n\n"
        "## Sections\n\n"
        f"{section_links}\n\n"
        "::: {.callout-tip title=\"본문 읽기\"}\n"
        "원본 통합 강의노트의 수식·표·연습문제는 한 페이지로 보존되어 있습니다. "
        "위의 Section 링크로 바로 이동하거나, [본문 전체](contents.html)에서 순서대로 읽을 수 있습니다.\n"
        ":::\n\n"
        "::: {.callout-tip title=\"협업 단위\"}\n"
        "본문은 원본 보존을 위해 한 파일로 관리합니다. 수정 제안에는 해당 Section의 제목과 앵커를 Pull Request에 함께 적어 주세요.\n"
        ":::\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="show files that would change without writing them")
    args = parser.parse_args()

    changed: list[Path] = []
    for directory in sorted(ROOT.iterdir()):
        if not directory.is_dir() or directory.name in SKIP_DIRECTORIES:
            continue
        index, contents = directory / "index.qmd", directory / "contents.qmd"
        if not index.exists() or not contents.exists():
            continue
        body = contents.read_text(encoding="utf-8")
        page = overview(chapter_title(index), chapter_subtitle(body), entries(body))
        if index.read_text(encoding="utf-8") != page:
            changed.append(index)
            if not args.dry_run:
                index.write_text(page, encoding="utf-8")

    for path in changed:
        print(path.relative_to(ROOT.parent))
    print(f"{'Would update' if args.dry_run else 'Updated'} {len(changed)} overview pages.")


if __name__ == "__main__":
    main()
