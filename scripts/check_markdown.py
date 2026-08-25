#!/usr/bin/env python3
"""Validate local Markdown links, fences, and published navigation coverage."""

from __future__ import annotations

import re
import sys
from fnmatch import fnmatchcase
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
IGNORE_PATH = ROOT / ".markdownignore"
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*$")
HTML_ID_RE = re.compile(r"\bid=[\"']([^\"']+)[\"']")
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:")
ESCAPABLE = frozenset(r"!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~")
LINK_WHITESPACE = " \t\r\n"


def markdown_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)


def unpublished_patterns() -> tuple[str, ...]:
    if not IGNORE_PATH.is_file():
        return ()
    return tuple(
        line
        for raw in IGNORE_PATH.read_text().splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    )


def is_unpublished(path: Path, patterns: tuple[str, ...]) -> bool:
    relative_parts = path.relative_to(ROOT).parts
    return any(_matches_root_pattern(relative_parts, pattern) for pattern in patterns)


def _matches_root_pattern(relative_parts: tuple[str, ...], raw_pattern: str) -> bool:
    """Match a slash-delimited ignore glob from the repository root."""
    pattern = raw_pattern.strip().replace("\\", "/")
    while pattern.startswith("./"):
        pattern = pattern[2:]
    pattern = pattern.lstrip("/")
    if pattern.endswith("/"):
        pattern += "**"
    pattern_parts = tuple(part for part in pattern.split("/") if part and part != ".")
    if not pattern_parts or ".." in pattern_parts:
        return False

    cache: dict[tuple[int, int], bool] = {}

    def matches(pattern_index: int, path_index: int) -> bool:
        key = (pattern_index, path_index)
        if key in cache:
            return cache[key]
        if pattern_index == len(pattern_parts):
            result = path_index == len(relative_parts)
        elif pattern_parts[pattern_index] == "**":
            result = matches(pattern_index + 1, path_index) or (
                path_index < len(relative_parts) and matches(pattern_index, path_index + 1)
            )
        else:
            result = (
                path_index < len(relative_parts)
                and fnmatchcase(relative_parts[path_index], pattern_parts[pattern_index])
                and matches(pattern_index + 1, path_index + 1)
            )
        cache[key] = result
        return result

    return matches(0, 0)


def _line_without_ending(line: str) -> str:
    return line.rstrip("\r\n")


def _opening_fence(line: str) -> tuple[str, int] | None:
    """Return a valid CommonMark-style fence marker and length."""
    match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", _line_without_ending(line))
    if not match:
        return None
    marker, info = match.groups()
    if marker[0] == "`" and "`" in info:
        return None
    return marker[0], len(marker)


def _closes_fence(line: str, marker: str, minimum: int) -> bool:
    match = re.match(r"^ {0,3}(`+|~+)[ \t]*$", _line_without_ending(line))
    return bool(match and match.group(1)[0] == marker and len(match.group(1)) >= minimum)


def _mask_non_newlines(value: str) -> str:
    return "".join(char if char in "\r\n" else " " for char in value)


def _is_escaped(value: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and value[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def _at_indented_line_start(value: str, index: int) -> bool:
    line_start = max(value.rfind("\n", 0, index), value.rfind("\r", 0, index)) + 1
    prefix = value[line_start:index]
    return prefix.startswith("\t") or (len(prefix) >= 4 and not prefix.strip(" "))


def _mask_inline_code_spans(content: str) -> str:
    """Mask closed backtick spans, including multiline and nested shorter runs."""
    output = list(content)
    index = 0
    while index < len(content):
        if (
            content[index] != "`"
            or _is_escaped(content, index)
            or _at_indented_line_start(content, index)
        ):
            index += 1
            continue
        opener_end = index + 1
        while opener_end < len(content) and content[opener_end] == "`":
            opener_end += 1
        width = opener_end - index
        candidate = opener_end
        closer_end: int | None = None
        while candidate < len(content):
            candidate = content.find("`", candidate)
            if candidate < 0:
                break
            run_end = candidate + 1
            while run_end < len(content) and content[run_end] == "`":
                run_end += 1
            if run_end - candidate == width:
                closer_end = run_end
                break
            candidate = run_end
        if closer_end is None:
            index = opener_end
            continue
        for position in range(index, closer_end):
            if output[position] not in "\r\n":
                output[position] = " "
        index = closer_end
    return "".join(output)


def markdown_prose(content: str) -> str:
    """Mask fenced and inline code before interpreting Markdown links."""
    output: list[str] = []
    open_fence: tuple[str, int] | None = None
    for line in content.splitlines(keepends=True):
        if open_fence is None:
            opening = _opening_fence(line)
            if opening is not None:
                open_fence = opening
                output.append(_mask_non_newlines(line))
                continue
        elif _closes_fence(line, *open_fence):
            open_fence = None
            output.append(_mask_non_newlines(line))
            continue
        if open_fence is not None:
            output.append(_mask_non_newlines(line))
        else:
            output.append(line)
    return _mask_inline_code_spans("".join(output))


def _unescape_backslashes(value: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(value):
        if (
            value[index] == "\\"
            and index + 1 < len(value)
            and value[index + 1] in ESCAPABLE
        ):
            output.append(value[index + 1])
            index += 2
        else:
            output.append(value[index])
            index += 1
    return "".join(output)


def _normalize_reference_label(label: str) -> str:
    unescaped = _unescape_backslashes(label)
    return re.sub(r"[ \t\r\n]+", " ", unescaped).strip().casefold()


def _display_reference_label(label: str) -> str:
    unescaped = _unescape_backslashes(label)
    return re.sub(r"[ \t\r\n]+", " ", unescaped).strip()


def _parse_bracket(
    content: str, start: int, *, allow_nested: bool
) -> tuple[str, int] | None:
    if start >= len(content) or content[start] != "[" or _is_escaped(content, start):
        return None
    depth = 1
    index = start + 1
    while index < len(content):
        if content[index] == "\\" and index + 1 < len(content):
            if content[index + 1] in ESCAPABLE:
                index += 2
                continue
        if content[index] == "[":
            if not allow_nested:
                return None
            depth += 1
        elif content[index] == "]":
            depth -= 1
            if depth == 0:
                return content[start + 1 : index], index + 1
        index += 1
    return None


def _skip_link_whitespace(content: str, index: int) -> int:
    while index < len(content) and content[index] in LINK_WHITESPACE:
        index += 1
    return index


def _parse_angle_destination(content: str, start: int) -> tuple[str, int] | None:
    if start >= len(content) or content[start] != "<":
        return None
    index = start + 1
    while index < len(content):
        if content[index] == "\\" and index + 1 < len(content):
            if content[index + 1] in ESCAPABLE:
                index += 2
                continue
        if content[index] in "\r\n" or content[index] == "<":
            return None
        if content[index] == ">":
            return _unescape_backslashes(content[start + 1 : index]), index + 1
        index += 1
    return None


def _parse_bare_destination(
    content: str, start: int, *, inline: bool
) -> tuple[str, int] | None:
    depth = 0
    index = start
    while index < len(content):
        char = content[index]
        if char in LINK_WHITESPACE or ord(char) < 0x20 or ord(char) == 0x7F:
            break
        if char == "\\" and index + 1 < len(content) and content[index + 1] in ESCAPABLE:
            index += 2
            continue
        if char == "<":
            return None
        if char == "(":
            depth += 1
            if depth > 32:
                return None
        elif char == ")":
            if depth == 0:
                if inline:
                    break
                return None
            depth -= 1
        index += 1
    if depth != 0:
        return None
    return _unescape_backslashes(content[start:index]), index


def _parse_title(content: str, start: int) -> int | None:
    if start >= len(content) or content[start] not in "\"'(":
        return None
    closing = ")" if content[start] == "(" else content[start]
    index = start + 1
    while index < len(content):
        if content[index] == "\\" and index + 1 < len(content):
            if content[index + 1] in ESCAPABLE:
                index += 2
                continue
        if content[index] == closing:
            return index + 1
        index += 1
    return None


def _parse_inline_destination(content: str, start: int) -> tuple[str, int] | None:
    if start >= len(content) or content[start] != "(":
        return None
    first = start + 1
    index = _skip_link_whitespace(content, first)
    had_leading_whitespace = index != first
    if index >= len(content):
        return None
    if content[index] == ")":
        return "", index + 1

    if had_leading_whitespace and content[index] in "\"'(":
        title_end = _parse_title(content, index)
        if title_end is not None:
            closing = _skip_link_whitespace(content, title_end)
            if closing < len(content) and content[closing] == ")":
                return "", closing + 1

    parsed = (
        _parse_angle_destination(content, index)
        if content[index] == "<"
        else _parse_bare_destination(content, index, inline=True)
    )
    if parsed is None:
        return None
    target, index = parsed
    if index < len(content) and content[index] == ")":
        return target, index + 1
    whitespace_end = _skip_link_whitespace(content, index)
    if whitespace_end == index:
        return None
    if whitespace_end < len(content) and content[whitespace_end] == ")":
        return target, whitespace_end + 1
    title_end = _parse_title(content, whitespace_end)
    if title_end is None:
        return None
    closing = _skip_link_whitespace(content, title_end)
    if closing >= len(content) or content[closing] != ")":
        return None
    return target, closing + 1


def _parse_reference_definition(line: str) -> tuple[str, str] | None:
    line = _line_without_ending(line)
    indentation = len(line) - len(line.lstrip(" "))
    if indentation > 3 or indentation == len(line) or line[indentation] != "[":
        return None
    parsed_label = _parse_bracket(line, indentation, allow_nested=False)
    if parsed_label is None:
        return None
    raw_label, index = parsed_label
    label = _normalize_reference_label(raw_label)
    if not label or len(raw_label) > 999 or index >= len(line) or line[index] != ":":
        return None
    index = index + 1
    index = _skip_link_whitespace(line, index)
    if index >= len(line):
        return None
    parsed_target = (
        _parse_angle_destination(line, index)
        if line[index] == "<"
        else _parse_bare_destination(line, index, inline=False)
    )
    if parsed_target is None:
        return None
    target, index = parsed_target
    if index == len(line):
        return label, target
    whitespace_end = _skip_link_whitespace(line, index)
    if whitespace_end == index:
        return None
    if whitespace_end == len(line):
        return label, target
    title_end = _parse_title(line, whitespace_end)
    if title_end is None or _skip_link_whitespace(line, title_end) != len(line):
        return None
    return label, target


def _reference_definitions(
    content: str,
) -> tuple[dict[str, str], list[tuple[int, int]]]:
    definitions: dict[str, str] = {}
    ranges: list[tuple[int, int]] = []
    offset = 0
    for line in content.splitlines(keepends=True):
        definition = _parse_reference_definition(line)
        if definition is not None:
            label, target = definition
            definitions.setdefault(label, target)
            ranges.append((offset, offset + len(line)))
        offset += len(line)
    return definitions, ranges


def _scan_markdown_links(content: str) -> tuple[list[str], set[str]]:
    prose = markdown_prose(content)
    definitions, definition_ranges = _reference_definitions(prose)
    scan = list(prose)
    for start, end in definition_ranges:
        for index in range(start, end):
            if scan[index] not in "\r\n":
                scan[index] = " "
    prose = "".join(scan)

    targets: list[str] = []
    missing: set[str] = set()
    index = 0
    while index < len(prose):
        if prose[index] != "[" or _is_escaped(prose, index):
            index += 1
            continue
        parsed_text = _parse_bracket(prose, index, allow_nested=True)
        if parsed_text is None:
            index += 1
            continue
        raw_text, text_end = parsed_text

        if text_end < len(prose) and prose[text_end] == "(":
            inline = _parse_inline_destination(prose, text_end)
            if inline is not None:
                target, link_end = inline
                targets.append(target)
                index = link_end
                continue

        if text_end < len(prose) and prose[text_end] == "[":
            parsed_label = _parse_bracket(prose, text_end, allow_nested=False)
            if parsed_label is not None:
                raw_label, reference_end = parsed_label
                selected_label = raw_label or raw_text
                normalized = _normalize_reference_label(selected_label)
                if normalized in definitions:
                    targets.append(definitions[normalized])
                elif normalized:
                    missing.add(_display_reference_label(selected_label))
                index = reference_end
                continue

        normalized = _normalize_reference_label(raw_text)
        if normalized in definitions:
            targets.append(definitions[normalized])
            index = text_end
            continue
        index += 1
    return targets, missing


def link_targets(content: str) -> list[str]:
    """Return inline, full, collapsed, and shortcut reference link targets."""
    return _scan_markdown_links(content)[0]


def undefined_reference_labels(content: str) -> list[str]:
    """Return explicit full/collapsed reference labels with no definition."""
    return sorted(_scan_markdown_links(content)[1], key=str.casefold)


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
        if open_fence is not None:
            if _closes_fence(line, *open_fence):
                open_fence = None
            continue
        opening = _opening_fence(line)
        if opening is not None:
            open_fence = opening
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
    for label in undefined_reference_labels(content):
        errors.append(
            f"{path.relative_to(ROOT)}: undefined reference-style link: [{label}]"
        )
    for raw_target in link_targets(content):
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
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
            continue
        if not target.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {raw_target}")
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
        if open_fence is not None:
            if _closes_fence(line, open_fence[0], open_fence[1]):
                open_fence = None
            continue
        opening = _opening_fence(line)
        if opening is not None:
            open_fence = (opening[0], opening[1], number)
    if open_fence is not None:
        rendered_fence = open_fence[0] * open_fence[1]
        errors.append(
            f"{path.relative_to(ROOT)}:{open_fence[2]}: "
            f"unclosed {rendered_fence} fence"
        )


def summary_targets() -> set[Path]:
    summary = ROOT / "SUMMARY.md"
    targets: set[Path] = set()
    for raw_target in link_targets(summary.read_text()):
        target = local_target(summary, raw_target)
        if target is not None and target.suffix == ".md":
            targets.add(target)
    return targets


def main() -> int:
    errors: list[str] = []
    anchor_cache: dict[Path, set[str]] = {}
    files = markdown_files()
    patterns = unpublished_patterns()
    for path in files:
        check_links(path, errors, anchor_cache)
        check_fences(path, errors)
        content = path.read_text()
        if content and not content.endswith("\n"):
            errors.append(f"{path.relative_to(ROOT)}: missing trailing newline")

    summarized = summary_targets()
    for path in files:
        if path.name == "SUMMARY.md" or is_unpublished(path, patterns):
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
