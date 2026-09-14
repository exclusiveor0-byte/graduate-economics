"""Check the built book with only Python's standard library; run after quarto render."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BOOK = ROOT / "_book"


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids, self.links = [], []
        self.math = self.callouts = self.proofs = 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if "id" in attrs:
            self.ids.append(attrs["id"])
        for key in ("href", "src"):
            if key in attrs:
                self.links.append(attrs[key])
        self.math += "math" in classes
        self.callouts += "callout" in classes
        self.proofs += "callout-collapse" in classes


def main():
    files = list(BOOK.rglob("*.html"))
    errors, rows = [], []
    if not files:
        sys.exit("No rendered HTML found. Run quarto render first.")
    pages = {p.resolve(): Page(p.read_text(encoding="utf-8")) for p in files}
    # Book sources are explicitly listed in the Quarto configuration.
    config = (ROOT / "_quarto.yml").read_text(encoding="utf-8-sig")
    sources = re.findall(r"^\s*- (?:part: )?([^\n]+\.qmd)\s*$", config, re.M)
    for source in sources:
        output = (BOOK / Path(source).with_suffix(".html")).resolve()
        if output not in pages:
            errors.append(f"Missing page: {source}")
            continue
        page = pages[output]
        text = (ROOT / source).read_text(encoding="utf-8-sig")
        expected_callouts = len(re.findall(r"^:{3,}\s*\{\.callout-", text, re.M))
        expected_proofs = len(re.findall(r'^:{3,}.*collapse="true"', text, re.M))
        if page.callouts != expected_callouts:
            errors.append(f"Callout count: {source}: {page.callouts}/{expected_callouts}")
        if page.proofs != expected_proofs:
            errors.append(f"Collapsed block count: {source}: {page.proofs}/{expected_proofs}")
        if len(re.findall(r"^\s*\$\$\s*$", text, re.M)) % 2:
            errors.append(f"Unbalanced display delimiters: {source}")
        rows.append({"source": source, "math": page.math, "callouts": page.callouts, "collapsed": page.proofs})
    for path, page in pages.items():
        relative = path.relative_to(BOOK)
        for identifier, count in Counter(page.ids).items():
            if count > 1:
                errors.append(f"Duplicate id: {relative}#{identifier}")
        for href in page.links:
            url = urlsplit(href)
            if url.scheme or url.netloc:
                continue
            target = (BOOK / unquote(url.path.lstrip("/")) if url.path.startswith("/") else path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                errors.append(f"Broken link: {relative} -> {href}")
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f"Missing anchor: {relative} -> {href}")
    report = {"pages": len(rows), "sections": rows, "errors": sorted(set(errors))}
    out = ROOT / "qa-output"
    out.mkdir(exist_ok=True)
    (out / "render-check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Checked {len(rows)} book pages; {sum(r['math'] for r in rows)} math spans; {sum(r['callouts'] for r in rows)} callouts; {sum(r['collapsed'] for r in rows)} collapsed blocks.")
    for error in report["errors"]:
        print(error)
    return bool(errors)


if __name__ == "__main__":
    sys.exit(main())
