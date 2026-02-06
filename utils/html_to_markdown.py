from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ConvertResult:
    converted: int
    skipped: int
    failed: int


_EXCLUDE_DIRS = {
    "_static",
    "_images",
    "_sources",
    "_sphinx_design_static",
    "generated",
}

_EXCLUDE_FILES = {
    "genindex.html",
    "py-modindex.html",
    "search.html",
    "index.html",  # usually navigation-heavy; you can include it if you want
}


def _iter_html_files(input_dir: Path) -> Iterator[Path]:
    for path in sorted(input_dir.rglob("*.html")):
        if not path.is_file():
            continue
        if any(part in _EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in _EXCLUDE_FILES:
            continue
        yield path


def _best_main_container(soup: BeautifulSoup):
    # Sphinx themes typically put main content under one of these.
    selectors = [
        "main",
        "div[role='main']",
        "div.document",
        "div.body",
        "div.bodywrapper",
        "article",
    ]
    for sel in selectors:
        node = soup.select_one(sel)
        if node is not None:
            return node
    return soup.body or soup


def _strip_noise(node) -> None:
    for tag in node.select(
        "script,style,noscript,nav,header,footer,form,button,svg,canvas,iframe"
    ):
        tag.decompose()

    # Sphinx-specific and other common doc chrome
    for sel in [
        ".sphinxsidebar",
        ".sphinxsidebarwrapper",
        ".sidebar",
        ".toc",
        ".contents",
        ".related",
        ".wy-nav-side",
        ".wy-nav-content-secondary",
        ".wy-breadcrumbs",
        ".breadcrumb",
        ".headerlink",
        ".rst-breadcrumbs",
        ".admonition-title",  # keep text content but drop the styling container
        ".searchbox",
        "#searchbox",
    ]:
        for tag in node.select(sel):
            tag.decompose()


def _html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown.

    Uses `markdownify` if installed; otherwise falls back to a conservative
    text-only extraction.
    """
    try:
        from markdownify import markdownify as md

        return md(
            html,
            heading_style="ATX",
            bullets="-",
            strip=["span"],
            code_language_callback=lambda _el: "",  # don't guess
        )
    except Exception:
        # Minimal fallback: text only (still useful for RAG).
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text("\n", strip=True)


def convert_html_dir_to_markdown(
    input_dir: Path,
    output_dir: Path,
    *,
    force: bool = False,
) -> ConvertResult:
    input_dir = input_dir.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    converted = 0
    skipped = 0
    failed = 0

    for html_path in _iter_html_files(input_dir):
        rel = html_path.relative_to(input_dir)
        out_path = (output_dir / rel).with_suffix(".md")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if (
            not force
            and out_path.exists()
            and out_path.stat().st_mtime >= html_path.stat().st_mtime
        ):
            skipped += 1
            continue

        try:
            raw = html_path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(raw, "html.parser")
            container = _best_main_container(soup)
            _strip_noise(container)

            title = (soup.title.get_text(" ", strip=True) if soup.title else rel.as_posix())
            md_body = _html_to_markdown(str(container)).strip()

            # Keep a stable, helpful header for retrieval.
            header = (
                f"# {title}\n\n"
                f"Source: {rel.as_posix()}\n\n"
            )
            out_path.write_text(header + md_body + "\n", encoding="utf-8")
            converted += 1
        except Exception:
            failed += 1

    return ConvertResult(converted=converted, skipped=skipped, failed=failed)


def _parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert HTML docs folder to Markdown for RAG")
    p.add_argument("--input", default="pandas", help="Input directory containing .html")
    p.add_argument(
        "--output",
        default="memory/md/pandas",
        help="Output directory for generated .md (mirrors input structure)",
    )
    p.add_argument("--force", action="store_true", help="Rebuild all outputs")
    return p.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> int:
    args = _parse_args(argv)
    res = convert_html_dir_to_markdown(
        Path(args.input),
        Path(args.output),
        force=bool(args.force),
    )
    print(
        f"HTML→MD done: converted={res.converted}, skipped={res.skipped}, failed={res.failed}"
    )
    return 0 if res.failed == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
