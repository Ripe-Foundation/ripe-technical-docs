#!/usr/bin/env python3
"""Validate local Markdown links, fences, and SUMMARY coverage."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
UNPUBLISHED_PAGES = {ROOT / "reference" / "ImplementationBaseline.md"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
HTML_ID_RE = re.compile(r"\bid=[\"']([^\"']+)[\"']")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target or target.startswith("#") or target.startswith(EXTERNAL_PREFIXES):
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    target = target.split("#", 1)[0]
    target = unquote(target)
    if not target:
        return None
    return (source.parent / target).resolve()


def heading_anchors(path: Path) -> set[str]:
    """Approximate GitHub/GitBook ATX heading IDs, including duplicate suffixes."""
    anchors: set[str] = set()
    counts: dict[str, int] = {}
    open_fence: tuple[str, int] | None = None
    for line in path.read_text().splitlines():
        fence = FENCE_RE.match(line)
        if fence:
            marker = fence.group(1)
            if open_fence is None:
                open_fence = (marker[0], len(marker))
            elif marker[0] == open_fence[0] and len(marker) >= open_fence[1]:
                open_fence = None
            continue
        if open_fence is not None:
            continue

        anchors.update(unquote(value) for value in HTML_ID_RE.findall(line))
        match = HEADING_RE.match(line)
        if not match:
            continue
        heading = re.sub(r"\s+#+\s*$", "", match.group(1))
        heading = re.sub(r"!?\[([^\]]*)\]\([^)]+\)", r"\1", heading)
        heading = re.sub(r"<[^>]+>", "", heading).replace("`", "")
        base = re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", heading.lower()).strip())
        if not base:
            continue
        duplicate = counts.get(base, 0)
        counts[base] = duplicate + 1
        anchors.add(base if duplicate == 0 else f"{base}-{duplicate}")
    return anchors


def check_links(
    path: Path, errors: list[str], anchor_cache: dict[Path, set[str]]
) -> None:
    content = path.read_text()
    for match in LINK_RE.finditer(content):
        raw_target = match.group(1).strip()
        if raw_target.startswith("<") and raw_target.endswith(">"):
            raw_target = raw_target[1:-1]
        if not raw_target or raw_target.startswith(EXTERNAL_PREFIXES):
            continue
        raw_path, separator, raw_fragment = raw_target.partition("#")
        if raw_path:
            target = (path.parent / unquote(raw_path)).resolve()
        else:
            target = path.resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {match.group(1)}")
            continue
        if not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {match.group(1)}")
            continue
        if separator and raw_fragment and target.suffix == ".md":
            fragment = unquote(raw_fragment)
            anchors = anchor_cache.setdefault(target, heading_anchors(target))
            if fragment not in anchors:
                errors.append(
                    f"{path.relative_to(ROOT)}: missing heading fragment "
                    f"#{fragment} in {target.relative_to(ROOT)}"
                )


def check_fences(path: Path, errors: list[str]) -> None:
    open_fence: tuple[str, int, int] | None = None
    for number, line in enumerate(path.read_text().splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        marker = match.group(1)
        if open_fence is None:
            open_fence = (marker[0], len(marker), number)
        elif marker[0] == open_fence[0] and len(marker) >= open_fence[1]:
            open_fence = None
    if open_fence is not None:
        errors.append(
            f"{path.relative_to(ROOT)}:{open_fence[2]}: unclosed {open_fence[0] * open_fence[1]} fence"
        )


def summary_targets() -> set[Path]:
    summary = ROOT / "SUMMARY.md"
    targets: set[Path] = set()
    for match in LINK_RE.finditer(summary.read_text()):
        target = local_target(summary, match.group(1))
        if target is not None and target.suffix == ".md":
            targets.add(target)
    return targets


def main() -> int:
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    files = markdown_files()
    for path in files:
        check_links(path, errors, anchor_cache)
        check_fences(path, errors)
        content = path.read_text()
        if content and not content.endswith("\n"):
            errors.append(f"{path.relative_to(ROOT)}: missing trailing newline")

    summarized = summary_targets()
    for path in files:
        if path.name == "SUMMARY.md" or path in UNPUBLISHED_PAGES:
            continue
        if path not in summarized:
            errors.append(f"SUMMARY.md: missing page: {path.relative_to(ROOT)}")

    if errors:
        print("Markdown validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1

    print(f"validated {len(files)} Markdown files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
