#!/usr/bin/env python3
"""Generate or verify contract API inventories in the technical docs.

The narrative documentation explains intent and behavior. This script enforces
the explicit source-to-page map, pins selector-facing Vyper ABIs, and extracts
directly declared APIs from sources without a tracked ABI at the exact protocol
commit recorded in reference/implementation-baseline.json.

Usage:
    python3 scripts/sync_api_reference.py --protocol-repo /path/to/ripe-protocol --write
    python3 scripts/sync_api_reference.py --protocol-repo /path/to/ripe-protocol --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


DOCS_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = DOCS_ROOT / "reference" / "implementation-baseline.json"
EXPECTED_PROTOCOL_REPOSITORY = "https://github.com/Ripe-Foundation/ripe-protocol"
EXPECTED_PROTOCOL_BRANCH = "rh"
BEGIN_PREFIX = "<!-- BEGIN GENERATED API REFERENCE: "
END_PREFIX = "<!-- END GENERATED API REFERENCE: "
GENERATED_BEGIN_RE = re.compile(r"<!-- BEGIN GENERATED API REFERENCE: ([^>]+) -->")
GENERATED_END_RE = re.compile(r"<!-- END GENERATED API REFERENCE: ([^>]+) -->")
SOURCE_LINK_RE = re.compile(
    r"\[(?:📄 )?(?:View Source Code|View the pinned RH source)\]\([^)]+\)"
)


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def git_show(repo: Path, commit: str, path: str) -> str:
    return run_git(repo, "show", f"{commit}:{path}")


def canonical_type(item: dict[str, Any]) -> str:
    raw_type = item["type"]
    if not raw_type.startswith("tuple"):
        return raw_type
    tuple_type = "(" + ",".join(canonical_type(c) for c in item.get("components", [])) + ")"
    return tuple_type + raw_type[len("tuple") :]


def named_items(items: Iterable[dict[str, Any]], *, event: bool = False) -> str:
    rendered: list[str] = []
    for item in items:
        value = canonical_type(item)
        name = item.get("name", "")
        if name:
            value += f" {name}"
        if event and item.get("indexed"):
            value += " indexed"
        rendered.append(value)
    return ", ".join(rendered)


def output_items(items: Iterable[dict[str, Any]]) -> str:
    values = [canonical_type(item) for item in items]
    if not values:
        return "—"
    if len(values) == 1:
        return f"`{values[0]}`"
    return "`(" + ", ".join(values) + ")`"


def input_types(item: dict[str, Any]) -> tuple[str, ...]:
    return tuple(canonical_type(value) for value in item.get("inputs", []))


def readable_items(items: Iterable[dict[str, Any]]) -> str:
    """Render tuple-heavy inputs compactly for the non-authoritative call guide."""
    rendered: list[str] = []
    for item in items:
        value = canonical_type(item)
        if value.startswith("("):
            closing = value.rfind(")")
            suffix = value[closing + 1 :] if closing >= 0 else ""
            value = ("Addys" if item.get("name") == "_a" else "tuple") + suffix
        name = item.get("name", "")
        rendered.append(f"{value} {name}".rstrip())
    return ", ".join(rendered)


def render_optional_argument_guide(
    abi_functions: list[dict[str, Any]],
) -> list[str]:
    """Summarize Vyper default-argument selector families without hiding selectors."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for item in abi_functions:
        groups.setdefault(item["name"], []).append(item)

    rows: list[tuple[str, int, int, str]] = []
    for name, entries in sorted(groups.items()):
        if len(entries) < 2:
            continue
        ordered = sorted(entries, key=lambda entry: len(entry.get("inputs", [])))
        longest = ordered[-1]
        longest_types = input_types(longest)
        if not all(input_types(entry) == longest_types[: len(input_types(entry))] for entry in ordered):
            continue
        accepted_counts = [len(entry.get("inputs", [])) for entry in ordered]
        if accepted_counts != list(range(accepted_counts[0], accepted_counts[-1] + 1)):
            continue
        minimum = accepted_counts[0]
        maximum = accepted_counts[-1]
        optional = ", ".join(
            f"`{item.get('name') or canonical_type(item)}`"
            for item in longest.get("inputs", [])[minimum:]
        )
        rows.append(
            (
                f"{name}({readable_items(longest.get('inputs', []))})",
                minimum,
                maximum,
                optional or "—",
            )
        )

    if not rows:
        return []

    lines = [
        "### Optional-argument call guide",
        "",
        "Vyper exposes one ABI selector for each accepted prefix of a default-argument call. "
        "Use the canonical full call below for readability; the exact selector table that follows "
        "retains every callable arity.",
        "",
        "| Canonical full call | Accepted argument counts | Optional trailing arguments |",
        "| --- | --- | --- |",
    ]
    for signature, minimum, maximum, optional in rows:
        counts = str(minimum) if minimum == maximum else f"{minimum}–{maximum}"
        lines.append(f"| `{signature}` | `{counts}` | {optional} |")
    lines.append("")
    return lines


def normalize_signature(lines: list[str], start: int) -> tuple[str, int]:
    parts: list[str] = []
    depth = 0
    index = start
    while index < len(lines):
        part = lines[index].strip()
        parts.append(part)
        depth += part.count("(") - part.count(")")
        if depth == 0 and part.endswith(":"):
            break
        index += 1
    signature = " ".join(parts)
    signature = re.sub(r"\s+", " ", signature).removesuffix(":")
    return signature, index


def source_declarations(source: str) -> tuple[list[str], list[tuple[str, list[str]]], list[tuple[str, list[str]]]]:
    lines = source.splitlines()
    functions: list[str] = []
    events: list[tuple[str, list[str]]] = []
    structs: list[tuple[str, list[str]]] = []
    external = False
    index = 0
    while index < len(lines):
        line = lines[index]
        # Preserve the column-zero requirement so nested/interface snippets are
        # not ingested, while tolerating harmless trailing whitespace in source.
        if line.rstrip() == "@external":
            external = True
            index += 1
            continue
        if external and line.startswith("@"):
            index += 1
            continue
        if external and line.startswith("def "):
            signature, index = normalize_signature(lines, index)
            functions.append(signature)
            external = False
            index += 1
            continue
        if external and line.strip() and not line.startswith("#"):
            external = False

        declaration = re.match(r"^(event|struct) ([A-Za-z_][A-Za-z0-9_]*):$", line)
        if declaration:
            fields: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                field = lines[cursor]
                if not field.startswith("    ") or not field.strip():
                    break
                fields.append(field.strip())
                cursor += 1
            target = events if declaration.group(1) == "event" else structs
            target.append((declaration.group(2), fields))
            index = cursor
            continue
        index += 1
    return functions, events, structs


def render_named_declarations(title: str, declarations: list[tuple[str, list[str]]]) -> list[str]:
    if not declarations:
        return []
    lines = [f"### {title}", ""]
    for name, fields in declarations:
        body = ", ".join(fields) if fields else "no fields"
        lines.append(f"- `{name}({body})`")
    lines.append("")
    return lines


def strip_solidity_comments(source: str) -> str:
    without_blocks = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", without_blocks)


def matching_brace(source: str, opening: int) -> int:
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {'"', "'"}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise RuntimeError("unterminated Solidity contract body")


def solidity_contract_declarations(source: str) -> list[tuple[str, list[str]]]:
    """Return constructor/function declarations written directly in each contract."""
    cleaned = strip_solidity_comments(source)
    contracts: list[tuple[str, list[str]]] = []
    cursor = 0
    contract_re = re.compile(r"\bcontract\s+([A-Za-z_][A-Za-z0-9_]*)\b")
    declaration_re = re.compile(r"\b(?:constructor|function)\b")

    while match := contract_re.search(cleaned, cursor):
        opening = cleaned.find("{", match.end())
        if opening < 0:
            raise RuntimeError(f"missing body for Solidity contract {match.group(1)}")
        closing = matching_brace(cleaned, opening)
        body = cleaned[opening + 1 : closing]
        declarations: list[str] = []
        index = 0
        depth = 0
        while index < len(body):
            char = body[index]
            if char == "{":
                depth += 1
                index += 1
                continue
            if char == "}":
                depth -= 1
                index += 1
                continue
            if depth != 0:
                index += 1
                continue
            declaration = declaration_re.match(body, index)
            if declaration is None:
                index += 1
                continue

            end = declaration.end()
            parentheses = 0
            while end < len(body):
                value = body[end]
                if value == "(":
                    parentheses += 1
                elif value == ")":
                    parentheses -= 1
                elif parentheses == 0 and value in "{;":
                    break
                end += 1
            signature = re.sub(r"\s+", " ", body[index:end]).strip()
            signature = re.sub(r"\(\s+", "(", signature)
            signature = re.sub(r"\s+\)", ")", signature)
            signature = re.sub(r"\s*,\s*", ", ", signature)
            declarations.append(signature)
            if end < len(body) and body[end] == "{":
                end = matching_brace(body, end)
            index = end + 1

        contracts.append((match.group(1), declarations))
        cursor = closing + 1
    return contracts


def render_solidity_api_block(source_path: str, source: str) -> str:
    contract = Path(source_path).stem
    begin = f"{BEGIN_PREFIX}{contract} -->"
    end = f"{END_PREFIX}{contract} -->"
    lines = [
        begin,
        "## Exact source-declared API reference",
        "",
        f"> Generated from declarations in `{source_path}`. This file has no first-party "
        "tracked ABI under `scripts/abis`; inherited Chainlink members are outside this "
        "source-declared inventory.",
        "",
    ]
    contracts = solidity_contract_declarations(source)
    if not contracts:
        lines.extend(["- No contract declarations found.", ""])
    for name, declarations in contracts:
        lines.extend([f"### `{name}`", ""])
        if declarations:
            lines.extend(f"- `{declaration}`" for declaration in declarations)
        else:
            lines.append("- No constructor or function declarations in this source body.")
        lines.append("")
    lines.append(end)
    return "\n".join(lines).rstrip() + "\n"


def render_api_block(
    contract: str,
    source_path: str,
    source: str,
    abi: list[dict[str, Any]] | None,
) -> str:
    functions, source_events, structs = source_declarations(source)
    begin = f"{BEGIN_PREFIX}{contract} -->"
    end = f"{END_PREFIX}{contract} -->"
    if abi is not None:
        provenance = (
            f"> Generated from `{source_path}` and its tracked ABI. The ABI inventory includes "
            "inherited and exported module members and is the selector-facing reference."
        )
    else:
        provenance = (
            f"> Generated from declarations in `{source_path}`. "
            "This source has no tracked ABI under `scripts/abis`; the inventory therefore covers "
            "the functions, events, and structs declared by this source rather than claiming a "
            "composed host ABI."
        )
    lines = [
        begin,
        "## Exact API reference",
        "",
        provenance,
        "",
    ]

    if abi is not None:
        constructors = [item for item in abi if item.get("type") == "constructor"]
        abi_functions = [item for item in abi if item.get("type") == "function"]
        abi_events = [item for item in abi if item.get("type") == "event"]
        abi_special_entries = [
            item for item in abi if item.get("type") in {"fallback", "receive"}
        ]

        # A tracked ABI is the most complete selector surface because it also
        # contains exported module members. The name-level guard below catches
        # an ABI that entirely omits a function/event declared by the host. It
        # does not independently recompile or prove argument/return/mutability
        # parity; the rendered signature authority remains the pinned tracked
        # ABI and review of that artifact.
        declared_function_names = {
            match.group(1)
            for signature in functions
            if (match := re.match(r"def ([A-Za-z_][A-Za-z0-9_]*)\(", signature))
            and match.group(1) not in {"__default__", "__init__"}
        }
        abi_function_names = {item.get("name") for item in abi_functions}
        missing_function_names = sorted(declared_function_names - abi_function_names)
        declared_event_names = {name for name, _ in source_events}
        abi_event_names = {item.get("name") for item in abi_events}
        missing_event_names = sorted(declared_event_names - abi_event_names)
        source_has_fallback = any(
            signature.startswith("def __default__(") for signature in functions
        )
        missing_fallback = source_has_fallback and not any(
            item.get("type") == "fallback" for item in abi_special_entries
        )
        if missing_function_names or missing_event_names or missing_fallback:
            raise RuntimeError(
                f"tracked ABI for {contract} is stale: "
                f"missing functions={missing_function_names}, "
                f"missing events={missing_event_names}, "
                f"missing fallback={missing_fallback}"
            )

        if constructors:
            lines.extend(["### Constructor", ""])
            for item in constructors:
                lines.append(f"- `constructor({named_items(item.get('inputs', []))})`")
            lines.append("")

        if abi_special_entries:
            lines.extend(["### Fallback and receive", ""])
            for item in abi_special_entries:
                lines.append(
                    f"- `{item['type']}()` — `{item.get('stateMutability', 'nonpayable')}`"
                )
            lines.append("")

        lines.extend(render_optional_argument_guide(abi_functions))
        lines.extend(["### Functions", "", "| Signature | Mutability | Returns |", "| --- | --- | --- |"])
        for item in sorted(
            abi_functions,
            key=lambda entry: (entry.get("name", ""), named_items(entry.get("inputs", []))),
        ):
            signature = f"{item['name']}({named_items(item.get('inputs', []))})"
            lines.append(
                f"| `{signature}` | `{item.get('stateMutability', 'nonpayable')}` | "
                f"{output_items(item.get('outputs', []))} |"
            )
        lines.append("")

        if abi_events:
            lines.extend(["### Events", "", "| Event | Fields |", "| --- | --- |"])
            for item in sorted(abi_events, key=lambda entry: entry.get("name", "")):
                lines.append(
                    f"| `{item['name']}` | `{named_items(item.get('inputs', []), event=True)}` |"
                )
            lines.append("")
    else:
        lines.extend(["### External functions declared by this source", ""])
        if functions:
            lines.extend(f"- `{signature}`" for signature in sorted(functions))
        else:
            lines.append("- None.")
        lines.append("")
        lines.extend(render_named_declarations("Events declared by this source", source_events))

    lines.extend(render_named_declarations("Structs declared by this source", structs))
    lines.append(end)
    return "\n".join(lines).rstrip() + "\n"


def replace_generated_block(content: str, contract: str, block: str) -> str:
    begin = re.escape(f"{BEGIN_PREFIX}{contract} -->")
    end = re.escape(f"{END_PREFIX}{contract} -->")
    pattern = re.compile(begin + r".*?" + end + r"\n?", re.DOTALL)
    if pattern.search(content):
        return pattern.sub(block, content, count=1)
    return content.rstrip() + "\n\n" + block


def pin_source_link(content: str, source_url: str) -> str:
    link = f"[📄 View Source Code]({source_url})"
    if SOURCE_LINK_RE.search(content):
        return SOURCE_LINK_RE.sub(link, content, count=1)
    lines = content.splitlines()
    if lines and lines[0].startswith("# "):
        lines[1:1] = ["", link]
        return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    return link + "\n\n" + content


def first_party_vyper_paths(repo: Path, commit: str) -> list[str]:
    paths = run_git(repo, "ls-tree", "-r", "--name-only", commit, "contracts", "interfaces").splitlines()
    return sorted(
        path
        for path in paths
        if (path.endswith(".vy") or path.endswith(".vyi"))
        and not path.startswith("contracts/mock/")
    )


def first_party_solidity_paths(repo: Path, commit: str) -> list[str]:
    paths = run_git(repo, "ls-tree", "-r", "--name-only", commit, "solidity/src").splitlines()
    root = Path("solidity/src")
    return sorted(
        path
        for path in paths
        if path.endswith(".sol") and Path(path).parent == root
    )


def configured_doc_paths(
    baseline: dict[str, Any], source_paths: list[str]
) -> dict[str, Path]:
    configured = baseline.get("source_docs")
    if not isinstance(configured, dict):
        raise RuntimeError("implementation baseline must contain a source_docs object")

    actual_sources = set(source_paths)
    configured_sources = set(configured)
    missing = sorted(actual_sources - configured_sources)
    stale = sorted(configured_sources - actual_sources)
    if missing or stale:
        raise RuntimeError(
            f"source_docs coverage mismatch: missing mappings={missing}, stale mappings={stale}"
        )

    docs: dict[str, Path] = {}
    used_paths: dict[Path, str] = {}
    for source_path, relative_value in configured.items():
        if not isinstance(relative_value, str) or not relative_value.endswith(".md"):
            raise RuntimeError(f"invalid documentation path for {source_path}: {relative_value!r}")
        doc_path = (DOCS_ROOT / relative_value).resolve()
        try:
            doc_path.relative_to(DOCS_ROOT)
        except ValueError as exc:
            raise RuntimeError(
                f"documentation path escapes repository for {source_path}: {relative_value}"
            ) from exc
        if not doc_path.is_file():
            raise RuntimeError(f"missing documentation page for {source_path}: {relative_value}")
        if doc_path in used_paths:
            raise RuntimeError(
                f"documentation page {relative_value} is mapped from both "
                f"{used_paths[doc_path]} and {source_path}"
            )
        used_paths[doc_path] = source_path
        docs[source_path] = doc_path
    return docs


def validate_generated_marker_topology(docs: dict[str, Path]) -> None:
    """Reject duplicate, orphaned, mismatched, or misplaced generated blocks."""
    expected_by_doc = {
        doc_path.resolve(): Path(source_path).stem
        for source_path, doc_path in docs.items()
    }
    for doc_path in sorted(DOCS_ROOT.rglob("*.md")):
        content = doc_path.read_text()
        begins = GENERATED_BEGIN_RE.findall(content)
        ends = GENERATED_END_RE.findall(content)
        if not begins and not ends:
            continue
        expected = expected_by_doc.get(doc_path.resolve())
        if expected is None:
            raise RuntimeError(
                "generated API marker found outside a mapped component page: "
                f"{doc_path.relative_to(DOCS_ROOT)}"
            )
        if begins != [expected] or ends != [expected]:
            raise RuntimeError(
                f"invalid generated API markers in {doc_path.relative_to(DOCS_ROOT)}: "
                f"expected one {expected!r} block, found begins={begins}, ends={ends}"
            )
        begin_marker = f"{BEGIN_PREFIX}{expected} -->"
        end_marker = f"{END_PREFIX}{expected} -->"
        if content.find(begin_marker) >= content.find(end_marker):
            raise RuntimeError(
                f"generated API markers are out of order in "
                f"{doc_path.relative_to(DOCS_ROOT)}"
            )


def validate_pinned_protocol_links(
    protocol_repo: Path, baseline: dict[str, Any]
) -> int:
    """Verify every commit-pinned protocol blob/tree link without network access."""
    repository = baseline["protocol_repository"].rstrip("/")
    commit = baseline["protocol_commit"]
    pattern = re.compile(
        re.escape(repository)
        + r"/(blob|tree)/([^/]+)/([^\s)#]+)(#[^\s)]+)?"
    )
    errors: list[str] = []
    checked: set[tuple[str, str, str | None]] = set()
    for doc_path in sorted(DOCS_ROOT.rglob("*.md")):
        if ".git" in doc_path.parts:
            continue
        for match in pattern.finditer(doc_path.read_text()):
            kind, ref, source_path, fragment = match.groups()
            label = f"{doc_path.relative_to(DOCS_ROOT)}: {match.group(0)}"
            if ref != commit:
                errors.append(f"unpinned or wrong-baseline protocol link: {label}")
                continue
            identity = (kind, source_path, fragment)
            if identity in checked:
                continue
            checked.add(identity)
            try:
                run_git(protocol_repo, "cat-file", "-e", f"{commit}:{source_path}")
            except subprocess.CalledProcessError:
                errors.append(f"missing pinned protocol path: {label}")
                continue
            if kind == "blob" and fragment:
                line_match = re.fullmatch(r"#L([0-9]+)(?:-L([0-9]+))?", fragment)
                if line_match:
                    start = int(line_match.group(1))
                    end = int(line_match.group(2) or start)
                    line_count = len(git_show(protocol_repo, commit, source_path).splitlines())
                    if start < 1 or end < start or end > line_count:
                        errors.append(
                            f"out-of-range pinned line anchor ({line_count} lines): {label}"
                        )
    if errors:
        raise RuntimeError("\n".join(errors))
    return len(checked)


def abi_paths(repo: Path, commit: str) -> dict[str, str]:
    paths = run_git(repo, "ls-tree", "-r", "--name-only", commit, "scripts/abis").splitlines()
    return {Path(path).stem: path for path in paths if path.endswith(".json")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol-repo",
        type=Path,
        default=Path(os.environ["RIPE_PROTOCOL_REPO"]) if "RIPE_PROTOCOL_REPO" in os.environ else None,
        help="Path to a ripe-protocol clone containing the pinned commit",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.protocol_repo is None:
        parser.error("--protocol-repo or RIPE_PROTOCOL_REPO is required")
    protocol_repo = args.protocol_repo.resolve()
    baseline = json.loads(BASELINE_PATH.read_text())
    if baseline.get("protocol_repository") != EXPECTED_PROTOCOL_REPOSITORY:
        raise RuntimeError(
            "unexpected protocol_repository in implementation baseline: "
            f"{baseline.get('protocol_repository')!r}"
        )
    if baseline.get("protocol_branch") != EXPECTED_PROTOCOL_BRANCH:
        raise RuntimeError(
            "unexpected protocol_branch in implementation baseline: "
            f"{baseline.get('protocol_branch')!r}"
        )
    for identity_field in ("protocol_commit", "protocol_tree"):
        if not re.fullmatch(r"[0-9a-f]{40}", str(baseline.get(identity_field, ""))):
            raise RuntimeError(
                f"invalid {identity_field} in implementation baseline: "
                f"{baseline.get(identity_field)!r}"
            )
    commit = baseline["protocol_commit"]
    expected_tree = baseline["protocol_tree"]

    resolved_commit = run_git(protocol_repo, "rev-parse", f"{commit}^{{commit}}").strip()
    resolved_tree = run_git(protocol_repo, "rev-parse", f"{commit}^{{tree}}").strip()
    if resolved_commit != commit or resolved_tree != expected_tree:
        raise RuntimeError(
            f"protocol identity mismatch: commit={resolved_commit}, tree={resolved_tree}, "
            f"expected commit={commit}, tree={expected_tree}"
        )

    checked_links = validate_pinned_protocol_links(protocol_repo, baseline)
    vyper_sources = first_party_vyper_paths(protocol_repo, commit)
    solidity_sources = first_party_solidity_paths(protocol_repo, commit)
    docs = configured_doc_paths(baseline, vyper_sources + solidity_sources)
    validate_generated_marker_topology(docs)
    abis = abi_paths(protocol_repo, commit)
    changed: list[Path] = []

    for source_path in vyper_sources:
        contract = Path(source_path).stem
        doc_path = docs[source_path]
        source = git_show(protocol_repo, commit, source_path)
        abi = None
        if contract in abis:
            abi = json.loads(git_show(protocol_repo, commit, abis[contract]))
        block = render_api_block(contract, source_path, source, abi)
        current = doc_path.read_text()
        source_url = f"{baseline['protocol_repository']}/blob/{commit}/{source_path}"
        pinned = pin_source_link(current, source_url)
        updated = replace_generated_block(pinned, contract, block)
        if updated != current:
            changed.append(doc_path)
            if args.write:
                doc_path.write_text(updated)

    # Top-level first-party Solidity sources are discovered automatically.
    # They have no first-party tracked ABIs, so generate their directly
    # declared constructors/functions without claiming inherited ABIs.
    for source_path in solidity_sources:
        contract = Path(source_path).stem
        doc_path = docs[source_path]
        source = git_show(protocol_repo, commit, source_path)
        current = doc_path.read_text()
        source_url = f"{baseline['protocol_repository']}/blob/{commit}/{source_path}"
        pinned = pin_source_link(current, source_url)
        block = render_solidity_api_block(source_path, source)
        updated = replace_generated_block(pinned, contract, block)
        if updated != current:
            changed.append(doc_path)
            if args.write:
                doc_path.write_text(updated)

    if args.check and changed:
        print("Generated API reference is out of date:", file=sys.stderr)
        for path in changed:
            print(f"  {path.relative_to(DOCS_ROOT)}", file=sys.stderr)
        return 1

    verb = "updated" if args.write else "verified"
    print(
        f"{verb} {len(vyper_sources)} "
        f"Vyper/interface pages and {len(solidity_sources)} "
        f"first-party Solidity pages; verified {checked_links} pinned protocol links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
