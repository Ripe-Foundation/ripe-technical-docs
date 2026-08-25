#!/usr/bin/env python3
"""Generate or verify contract API inventories in the technical docs.

The narrative documentation explains intent and behavior. This script enforces
the explicit source-to-page map, pins selector-facing Vyper ABIs, and extracts
directly declared APIs from sources without a tracked ABI at the exact protocol
commit recorded in reference/implementation-baseline.json. Separately compiled
composed Solidity ABIs are hash-pinned with their compiler version and complete
protocol-source blob manifest. When a freshly built artifact root is supplied,
the compiler identity, settings, compilation target, source set, and canonical
ABI are also compared with the reviewed snapshot.

Usage:
    python3 scripts/sync_api_reference.py --protocol-repo /path/to/ripe-protocol --write
    python3 scripts/sync_api_reference.py --protocol-repo /path/to/ripe-protocol --check
    python3 scripts/sync_api_reference.py --protocol-repo /path/to/ripe-protocol \
        --compiled-artifact-root /path/to/ripe-protocol --check
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any, Iterable

from baseline_policy import validate_baseline_identity


DOCS_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = DOCS_ROOT / "reference" / "implementation-baseline.json"
BEGIN_PREFIX = "<!-- BEGIN GENERATED API REFERENCE: "
END_PREFIX = "<!-- END GENERATED API REFERENCE: "
GENERATED_BEGIN_RE = re.compile(r"<!-- BEGIN GENERATED API REFERENCE: ([^>]+) -->")
GENERATED_END_RE = re.compile(r"<!-- END GENERATED API REFERENCE: ([^>]+) -->")
SOURCE_LINK_RE = re.compile(r"\[(?:📄 )?View Source Code\]\([^)]+\)")
SOLIDITY_IDENTIFIER_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
SOLIDITY_VERSION_RE = re.compile(
    r"([0-9]+\.[0-9]+\.[0-9]+)\+commit\.([0-9a-f]{8})"
)


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def run_git_bytes(repo: Path, *args: str) -> bytes:
    """Read a Git object without text decoding or newline normalization."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
    )
    return result.stdout


def git_show(repo: Path, commit: str, path: str) -> str:
    return run_git(repo, "show", f"{commit}:{path}")


def git_show_bytes(repo: Path, commit: str, path: str) -> bytes:
    return run_git_bytes(repo, "show", f"{commit}:{path}")


def cast_keccak256(data: bytes, *, field: str) -> str:
    """Hash exact bytes with Ethereum Keccak through the pinned Foundry toolchain."""
    try:
        result = subprocess.run(
            ["cast", "keccak"],
            input=data,
            check=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"cast is required to verify compiled Solidity source hashes: {field}"
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace").strip() if exc.stderr else ""
        raise RuntimeError(f"cast keccak failed for {field}: {stderr}") from exc
    try:
        digest = result.stdout.decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise RuntimeError(f"cast keccak returned non-ASCII output for {field}") from exc
    if re.fullmatch(r"0x[0-9a-f]{64}", digest) is None:
        raise RuntimeError(f"cast keccak returned an invalid digest for {field}: {digest!r}")
    return digest


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


def named_canonical_type(item: dict[str, Any]) -> str:
    raw_type = item["type"]
    if raw_type.startswith("tuple"):
        components = []
        for component in item.get("components", []):
            components.append(named_canonical_type(component))
        value = "(" + ", ".join(components) + ")" + raw_type[len("tuple") :]
    else:
        value = raw_type
    if item.get("name"):
        value += f" {item['name']}"
    return value


def detailed_items(items: Iterable[dict[str, Any]], *, event: bool = False) -> str:
    """Render ABI items with tuple-component names and event indexing."""
    rendered: list[str] = []
    for item in items:
        value = named_canonical_type(item)
        if event and item.get("indexed"):
            value += " indexed"
        rendered.append(value)
    return ", ".join(rendered) if rendered else "—"


def output_items(items: Iterable[dict[str, Any]]) -> str:
    values = [named_canonical_type(item) for item in items]
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


def source_function_candidates(
    abi_item: dict[str, Any], source_catalog: dict[str, list[dict[str, Any]]]
) -> list[dict[str, Any]]:
    """Find source declarations compatible with an ABI selector."""
    abi_inputs = abi_item.get("inputs", [])
    names = [item.get("name", "") for item in abi_inputs]
    matches: list[dict[str, Any]] = []
    for declaration in source_catalog.get(abi_item.get("name", ""), []):
        arguments = declaration["arguments"]
        if len(arguments) < len(abi_inputs):
            continue
        if any(name and arguments[index]["name"] != name for index, name in enumerate(names)):
            continue
        matches.append(declaration)
    return matches


def unique_source_value(
    candidates: list[dict[str, Any]], key: str
) -> str | None:
    values = {candidate[key] for candidate in candidates if candidate.get(key)}
    return next(iter(values)) if len(values) == 1 else None


def render_optional_argument_guide(
    abi_functions: list[dict[str, Any]],
    source_catalog: dict[str, list[dict[str, Any]]],
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
        candidates = [
            candidate
            for candidate in source_function_candidates(longest, source_catalog)
            if len(candidate["arguments"]) == maximum
            and all(argument["default"] is not None for argument in candidate["arguments"][minimum:])
        ]
        default_sets = {
            tuple(argument["default"] for argument in candidate["arguments"][minimum:])
            for candidate in candidates
        }
        if len(default_sets) != 1:
            raise RuntimeError(
                f"cannot resolve exact defaults for ABI selector family {name}/{maximum}: "
                f"matches={len(candidates)}, defaults={sorted(default_sets)}"
            )
        defaults = next(iter(default_sets))
        optional = ", ".join(
            f"`{item.get('name') or canonical_type(item)} = {default}`"
            for item, default in zip(longest.get("inputs", [])[minimum:], defaults)
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
        part = lines[index].split("#", 1)[0].strip()
        if part:
            parts.append(part)
        depth += part.count("(") - part.count(")")
        if depth == 0 and part.endswith(":"):
            break
        index += 1
    signature = " ".join(parts)
    signature = re.sub(r"\s+", " ", signature).removesuffix(":")
    signature = re.sub(r"\(\s+", "(", signature)
    signature = re.sub(r"\s*,\s*", ", ", signature)
    signature = re.sub(r"\s+\)", ")", signature)
    signature = re.sub(r",\)(\s*(?:->.*)?)$", r")\1", signature)
    return signature, index


def split_top_level(value: str, delimiter: str = ",") -> list[str]:
    """Split a Vyper expression while preserving nested generic/function commas."""
    parts: list[str] = []
    start = 0
    depth = 0
    quote: str | None = None
    escaped = False
    for index, character in enumerate(value):
        if quote is not None:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {'"', "'"}:
            quote = character
        elif character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
        elif character == delimiter and depth == 0:
            parts.append(value[start:index].strip())
            start = index + 1
    tail = value[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def split_assignment(value: str) -> tuple[str, str | None]:
    depth = 0
    for index, character in enumerate(value):
        if character in "([{":
            depth += 1
        elif character in ")]}":
            depth -= 1
        elif character == "=" and depth == 0:
            return value[:index].strip(), value[index + 1 :].strip()
    return value.strip(), None


def parse_source_function(signature: str, decorators: list[str]) -> dict[str, Any]:
    match = re.match(r"def ([A-Za-z_][A-Za-z0-9_]*)\(", signature)
    if match is None:
        raise RuntimeError(f"cannot parse Vyper function declaration: {signature}")
    opening = match.end() - 1
    depth = 0
    closing = -1
    for index in range(opening, len(signature)):
        character = signature[index]
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                closing = index
                break
    if closing < 0:
        raise RuntimeError(f"unterminated Vyper function declaration: {signature}")
    remainder = signature[closing + 1 :].strip()
    if remainder and not remainder.startswith("->"):
        raise RuntimeError(f"cannot parse Vyper function return type: {signature}")
    return_type = remainder.removeprefix("->").strip()
    arguments: list[dict[str, str | None]] = []
    for raw_argument in split_top_level(signature[opening + 1 : closing]):
        declaration, default = split_assignment(raw_argument)
        if ":" not in declaration:
            raise RuntimeError(f"cannot parse Vyper argument: {raw_argument}")
        name, source_type = declaration.split(":", 1)
        arguments.append(
            {"name": name.strip(), "type": source_type.strip(), "default": default}
        )
    decorator_names = [decorator.split("(", 1)[0] for decorator in decorators]
    if "view" in decorator_names:
        mutability = "view"
    elif "pure" in decorator_names:
        mutability = "pure"
    elif "payable" in decorator_names:
        mutability = "payable"
    else:
        mutability = "nonpayable"
    return {
        "name": match.group(1),
        "signature": signature,
        "arguments": arguments,
        "returns": return_type,
        "mutability": mutability,
        "decorators": tuple(decorator_names),
        "external": "external" in decorator_names,
        "initializer": "deploy" in decorator_names,
    }


def unwrap_public_getter(source_type: str) -> tuple[list[str], str]:
    """Infer the source-level key types and value type of a public getter."""
    keys: list[str] = []
    value_type = source_type.strip()
    while value_type.startswith("HashMap[") and value_type.endswith("]"):
        inner = value_type[len("HashMap[") : -1]
        values = split_top_level(inner)
        if len(values) != 2:
            break
        keys.append(values[0])
        value_type = values[1]
    while value_type.startswith("DynArray[") and value_type.endswith("]"):
        inner = split_top_level(value_type[len("DynArray[") : -1])
        if len(inner) != 2:
            break
        keys.append("uint256")
        value_type = inner[0]
    fixed_array = re.fullmatch(r"(.+)\[[^][]+\]", value_type)
    while fixed_array is not None and re.fullmatch(
        r"(?:String|Bytes)\[[0-9]+\]", value_type
    ) is None:
        keys.append("uint256")
        value_type = fixed_array.group(1).strip()
        fixed_array = re.fullmatch(r"(.+)\[[^][]+\]", value_type)
    return keys, value_type


def source_declarations(source: str) -> dict[str, Any]:
    lines = source.splitlines()
    functions: list[dict[str, Any]] = []
    events: list[tuple[str, list[str]]] = []
    structs: list[tuple[str, list[str]]] = []
    flags: list[tuple[str, list[str]]] = []
    constants: list[tuple[str, str, str]] = []
    public_getters: list[tuple[str, list[str], str]] = []
    revert_reasons: set[str] = set()
    decorators: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        for reason in re.findall(r"#\s*dev:\s*([^\n]+)", line):
            revert_reasons.add(reason.strip())
        for reason in re.findall(r"\braise\s+([\"'])(.*?)\1", line):
            revert_reasons.add(reason[1].strip())

        if line.startswith("@"):
            decorators.append(line.strip().removeprefix("@"))
            index += 1
            continue
        if line.startswith("def "):
            signature, index = normalize_signature(lines, index)
            function = parse_source_function(signature, decorators)
            if function["external"] or function["initializer"]:
                functions.append(function)
            decorators = []
            index += 1
            continue
        if line and not line.startswith((" ", "#")):
            decorators = []

        declaration = re.match(r"^(event|struct|flag) ([A-Za-z_][A-Za-z0-9_]*):$", line)
        if declaration:
            fields: list[str] = []
            cursor = index + 1
            while cursor < len(lines):
                field = lines[cursor]
                if not field.startswith("    ") or not field.strip():
                    break
                fields.append(field.strip())
                cursor += 1
            target = {
                "event": events,
                "struct": structs,
                "flag": flags,
            }[declaration.group(1)]
            target.append((declaration.group(2), fields))
            index = cursor
            continue

        code = line.split("#", 1)[0].strip()
        public_match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_]*):\s*public\((.+)\)(?:\s*=\s*.+)?", code
        )
        if public_match:
            getter_type = public_match.group(2).strip()
            for wrapper in ("constant", "immutable"):
                prefix = f"{wrapper}("
                if getter_type.startswith(prefix) and getter_type.endswith(")"):
                    getter_type = getter_type[len(prefix) : -1]
                    break
            keys, return_type = unwrap_public_getter(getter_type)
            public_getters.append((public_match.group(1), keys, return_type))

        constant_match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_]*):\s*(?:public\()?constant\(([^)]+)\)\)?\s*=\s*(.+)",
            code,
        )
        if constant_match:
            constants.append(
                (constant_match.group(1), constant_match.group(2), constant_match.group(3))
            )
        index += 1
    return {
        "functions": functions,
        "events": events,
        "structs": structs,
        "flags": flags,
        "constants": constants,
        "public_getters": public_getters,
        "revert_reasons": sorted(revert_reasons),
    }


def render_named_declarations(title: str, declarations: list[tuple[str, list[str]]]) -> list[str]:
    if not declarations:
        return []
    lines = [f"### {title}", ""]
    for name, fields in declarations:
        body = ", ".join(fields) if fields else "no fields"
        lines.append(f"- `{name}({body})`")
    lines.append("")
    return lines


def render_source_revert_reasons(reasons: list[str]) -> list[str]:
    if not reasons:
        return []
    lines = [
        "### Source-declared revert reasons",
        "",
        "These are explicit source annotations or string reasons, not an exhaustive list of "
        "typed-call failures, arithmetic panics, or inherited-module reverts.",
        "",
    ]
    lines.extend(f"- `{reason}`" for reason in reasons)
    lines.append("")
    return lines


def required_argument_count(function: dict[str, Any]) -> int:
    arguments = function["arguments"]
    return next(
        (
            index
            for index, argument in enumerate(arguments)
            if argument["default"] is not None
        ),
        len(arguments),
    )


def source_call_form(function: dict[str, Any], arity: int) -> str:
    arguments = ", ".join(
        f"{argument['type']} {argument['name']}"
        for argument in function["arguments"][:arity]
    )
    return f"{function['name']}({arguments})"


def strip_solidity_comments(source: str) -> str:
    """Mask Solidity comments without treating comment tokens in strings as syntax."""
    output: list[str] = []
    index = 0
    quote: str | None = None
    escaped = False
    while index < len(source):
        char = source[index]
        following = source[index + 1] if index + 1 < len(source) else ""
        if quote is not None:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            output.append(char)
            index += 1
            continue
        if char == "/" and following == "/":
            output.extend((" ", " "))
            index += 2
            while index < len(source) and source[index] != "\n":
                output.append(" ")
                index += 1
            continue
        if char == "/" and following == "*":
            output.extend((" ", " "))
            index += 2
            while index < len(source):
                if source[index] == "*" and index + 1 < len(source) and source[index + 1] == "/":
                    output.extend((" ", " "))
                    index += 2
                    break
                output.append("\n" if source[index] == "\n" else " ")
                index += 1
            else:
                raise RuntimeError("unterminated Solidity block comment")
            continue
        output.append(char)
        index += 1
    return "".join(output)


def solidity_import_paths(source: str) -> tuple[str, ...]:
    """Extract import literals while ignoring comments and string contents."""
    cleaned = strip_solidity_comments(source)
    imports: list[str] = []
    index = 0
    quote: str | None = None
    escaped = False
    while index < len(cleaned):
        char = cleaned[index]
        if quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            index += 1
            continue
        if (
            cleaned.startswith("import", index)
            and (index == 0 or not (cleaned[index - 1].isalnum() or cleaned[index - 1] == "_"))
            and (
                index + len("import") == len(cleaned)
                or not (
                    cleaned[index + len("import")].isalnum()
                    or cleaned[index + len("import")] == "_"
                )
            )
        ):
            end = index + len("import")
            statement_quote: str | None = None
            statement_escaped = False
            while end < len(cleaned):
                value = cleaned[end]
                if statement_quote is not None:
                    if statement_escaped:
                        statement_escaped = False
                    elif value == "\\":
                        statement_escaped = True
                    elif value == statement_quote:
                        statement_quote = None
                elif value in {'"', "'"}:
                    statement_quote = value
                elif value == ";":
                    break
                end += 1
            if end >= len(cleaned):
                raise RuntimeError("unterminated Solidity import statement")
            statement = cleaned[index : end + 1]
            literals = re.findall(r"(?:\"([^\"]+)\"|'([^']+)')", statement)
            paths = [double or single for double, single in literals]
            if len(paths) != 1:
                raise RuntimeError(f"cannot parse Solidity import statement: {statement.strip()}")
            imports.append(paths[0])
            index = end + 1
            continue
        index += 1
    return tuple(imports)


def resolve_solidity_import(importer: str, imported: str) -> str:
    """Resolve one relative Solidity import inside the protocol's Solidity tree."""
    if not imported.startswith(("./", "../")):
        raise RuntimeError(
            f"non-relative Solidity import is not supported in {importer}: {imported}"
        )
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(importer), imported))
    if not resolved.startswith("solidity/") or not resolved.endswith(".sol"):
        raise RuntimeError(f"Solidity import escapes source tree in {importer}: {imported}")
    return resolved


def recursive_solidity_source_closure(
    protocol_repo: Path, commit: str, entry_source: str
) -> set[str]:
    """Derive the exact relative-import closure rooted at one Solidity source."""
    closure: set[str] = set()
    pending = [entry_source]
    while pending:
        source_path = pending.pop()
        if source_path in closure:
            continue
        try:
            source = git_show(protocol_repo, commit, source_path)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"missing Solidity compiler input at {commit}: {source_path}"
            ) from exc
        closure.add(source_path)
        for imported in solidity_import_paths(source):
            resolved = resolve_solidity_import(source_path, imported)
            if resolved not in closure:
                pending.append(resolved)
    return closure


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


def render_solidity_api_block(
    source_path: str,
    source: str,
    *,
    documentation_path: Path | None = None,
    inherited_reference: dict[str, Any] | None = None,
) -> str:
    contract = Path(source_path).stem
    begin = f"{BEGIN_PREFIX}{contract} -->"
    end = f"{END_PREFIX}{contract} -->"
    if inherited_reference is None:
        provenance = (
            f"> Generated from declarations written directly in `{source_path}`. "
            "This source-only inventory does not claim inherited APIs."
        )
    else:
        if documentation_path is None:
            raise RuntimeError(
                f"documentation_path is required for inherited Solidity API {source_path}"
            )
        try:
            current_page = documentation_path.resolve().relative_to(DOCS_ROOT)
            inherited_page = inherited_reference[
                "documentation_path_resolved"
            ].resolve().relative_to(DOCS_ROOT)
        except (KeyError, ValueError) as exc:
            raise RuntimeError(
                f"invalid inherited Solidity API reference for {source_path}"
            ) from exc
        relative_link = posixpath.relpath(
            inherited_page.as_posix(), current_page.parent.as_posix()
        )
        provenance = (
            f"> Generated from declarations written directly in `{source_path}`. The concrete "
            "contracts also expose the inherited operational surface documented in the "
            f"[composed {inherited_reference['display_name']} reference]({relative_link})."
        )
    lines = [
        begin,
        "## Ripe-specific source delta",
        "",
        provenance,
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


def code_cell(value: str) -> str:
    return "—" if value == "—" else f"`{value}`"


def render_composed_solidity_abi_block(
    marker: str, reference: dict[str, Any]
) -> str:
    """Render an exact inherited Solidity API from a compiled ABI snapshot."""
    abi = reference["abi"]
    artifact_path: Path = reference["artifact_path_resolved"]
    begin = f"{BEGIN_PREFIX}{marker} -->"
    end = f"{END_PREFIX}{marker} -->"
    lines = [
        begin,
        "## Exact composed ABI reference",
        "",
        f"> Generated from the hash-pinned `{reference['contract_name']}` ABI in "
        f"`{artifact_path.relative_to(DOCS_ROOT)}`, compiled with Solidity "
        f"`{reference['compiler_version']}`. The baseline records and verifies every "
        "compiler-input Git blob used by this inherited surface.",
        "",
    ]

    constructors = [item for item in abi if item.get("type") == "constructor"]
    if constructors:
        lines.extend(["### Constructor", "", "| Inputs | Mutability |", "| --- | --- |"])
        for item in constructors:
            lines.append(
                f"| {code_cell(detailed_items(item.get('inputs', [])))} | "
                f"`{item.get('stateMutability', 'nonpayable')}` |"
            )
        lines.append("")

    functions = [item for item in abi if item.get("type") == "function"]
    lines.extend(
        [
            "### Functions",
            "",
            "| Function | Inputs | Mutability | Returns |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in sorted(
        functions,
        key=lambda entry: (entry.get("name", ""), canonical_type_list(entry.get("inputs", []))),
    ):
        lines.append(
            f"| `{item['name']}` | {code_cell(detailed_items(item.get('inputs', [])))} | "
            f"`{item.get('stateMutability', 'nonpayable')}` | "
            f"{code_cell(detailed_items(item.get('outputs', [])))} |"
        )
    lines.append("")

    special_entries = [
        item for item in abi if item.get("type") in {"fallback", "receive"}
    ]
    if special_entries:
        lines.extend(["### Fallback and receive", ""])
        lines.extend(
            f"- `{item['type']}()` — `{item.get('stateMutability', 'nonpayable')}`"
            for item in special_entries
        )
        lines.append("")

    events = [item for item in abi if item.get("type") == "event"]
    if events:
        lines.extend(["### Events", "", "| Event | Fields |", "| --- | --- |"])
        for item in sorted(events, key=lambda entry: entry.get("name", "")):
            event_name = item["name"] + (" (anonymous)" if item["anonymous"] else "")
            lines.append(
                f"| `{event_name}` | "
                f"{code_cell(detailed_items(item.get('inputs', []), event=True))} |"
            )
        lines.append("")

    errors = [item for item in abi if item.get("type") == "error"]
    if errors:
        lines.extend(
            ["### Custom errors", "", "| Error | Inputs |", "| --- | --- |"]
        )
        for item in sorted(errors, key=lambda entry: entry.get("name", "")):
            lines.append(
                f"| `{item['name']}` | "
                f"{code_cell(detailed_items(item.get('inputs', [])))} |"
            )
        lines.append("")

    lines.append(end)
    return "\n".join(lines).rstrip() + "\n"


def canonical_type_list(items: Iterable[dict[str, Any]]) -> tuple[str, ...]:
    return tuple(canonical_type(item) for item in items)


def render_api_block(
    contract: str,
    source_path: str,
    source: str,
    abi: list[dict[str, Any]] | None,
    source_catalog: dict[str, list[dict[str, Any]]],
) -> str:
    declarations = source_declarations(source)
    functions = declarations["functions"]
    source_events = declarations["events"]
    structs = declarations["structs"]
    local_source_catalog: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for function in functions:
        if function["external"]:
            local_source_catalog[function["name"]].append(function)
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
            "deployment/module initializers, external functions and their default-argument call "
            "forms, compiler-generated public getters inferred from declarations, events, flags, "
            "constants, structs, and source-declared revert reasons found in this source. It does "
            "not claim a composed host ABI or canonical runtime selector surface."
        )
    lines = [
        begin,
        "## Exact API reference" if abi is not None else "## Exact source-declared API reference",
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
            function["name"]
            for function in functions
            if function["external"] and function["name"] not in {"__default__", "__init__"}
        }
        abi_function_names = {item.get("name") for item in abi_functions}
        missing_function_names = sorted(declared_function_names - abi_function_names)
        declared_event_names = {name for name, _ in source_events}
        abi_event_names = {item.get("name") for item in abi_events}
        missing_event_names = sorted(declared_event_names - abi_event_names)
        source_has_fallback = any(
            function["name"] == "__default__" for function in functions
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

        lines.extend(render_optional_argument_guide(abi_functions, source_catalog))
        lines.extend(
            [
                "### Functions",
                "",
                "| Signature | Mutability | ABI returns | Source return type |",
                "| --- | --- | --- | --- |",
            ]
        )
        for item in sorted(
            abi_functions,
            key=lambda entry: (entry.get("name", ""), named_items(entry.get("inputs", []))),
        ):
            signature = f"{item['name']}({named_items(item.get('inputs', []))})"
            source_return = unique_source_value(
                source_function_candidates(item, local_source_catalog), "returns"
            )
            lines.append(
                f"| `{signature}` | `{item.get('stateMutability', 'nonpayable')}` | "
                f"{output_items(item.get('outputs', []))} | "
                f"{f'`{source_return}`' if source_return else '—'} |"
            )
        lines.append("")

        if abi_events:
            lines.extend(["### Events", "", "| Event | Fields |", "| --- | --- |"])
            for item in sorted(abi_events, key=lambda entry: entry.get("name", "")):
                lines.append(
                    f"| `{item['name']}` | `{named_items(item.get('inputs', []), event=True)}` |"
                )
            lines.append("")

        abi_errors = [item for item in abi if item.get("type") == "error"]
        if abi_errors:
            lines.extend(["### ABI custom errors", "", "| Error | Inputs |", "| --- | --- |"])
            for item in sorted(abi_errors, key=lambda entry: entry.get("name", "")):
                lines.append(
                    f"| `{item['name']}` | `{named_items(item.get('inputs', []))}` |"
                )
            lines.append("")
    else:
        initializers = [function for function in functions if function["initializer"]]
        external_functions = [function for function in functions if function["external"]]
        if initializers:
            lines.extend(
                [
                    "### Deployment/module initializer declared by this source",
                    "",
                    "A `@deploy` initializer is constructor context when this source is deployed or "
                    "module-initialization context when composed. It is not a runtime selector.",
                    "",
                ]
            )
            lines.extend(f"- `{function['signature']}`" for function in initializers)
            lines.append("")

        lines.extend(
            [
                "### External functions declared by this source",
                "",
                "| Source declaration | Accepted arities | Mutability | Returns |",
                "| --- | --- | --- | --- |",
            ]
        )
        if external_functions:
            for function in sorted(external_functions, key=lambda item: item["signature"]):
                maximum = len(function["arguments"])
                minimum = required_argument_count(function)
                arities = str(minimum) if minimum == maximum else f"{minimum}–{maximum}"
                returns = f"`{function['returns']}`" if function["returns"] else "—"
                lines.append(
                    f"| `{function['signature']}` | `{arities}` | "
                    f"`{function['mutability']}` | {returns} |"
                )
        else:
            lines.append("| None | — | — | — |")
        lines.append("")

        if external_functions:
            lines.extend(
                [
                    "### Source-declared call forms",
                    "",
                    "Each row is one source-level call form permitted by the declaration's trailing "
                    "defaults. These signatures use Vyper source notation; they are not canonical "
                    "ABI signatures or selector-hash preimages. Without a tracked compiled ABI, "
                    "this table does not claim the exact runtime selector surface.",
                    "",
                    "| Source call form | Mutability | Returns |",
                    "| --- | --- | --- |",
                ]
            )
            for function in sorted(external_functions, key=lambda item: item["signature"]):
                returns = f"`{function['returns']}`" if function["returns"] else "—"
                for arity in range(
                    required_argument_count(function), len(function["arguments"]) + 1
                ):
                    lines.append(
                        f"| `{source_call_form(function, arity)}` | "
                        f"`{function['mutability']}` | {returns} |"
                    )
            lines.append("")

        if declarations["public_getters"]:
            lines.extend(
                [
                    "### Compiler-generated public getters",
                    "",
                    "| Getter | Mutability | Source return type |",
                    "| --- | --- | --- |",
                ]
            )
            for name, keys, return_type in sorted(declarations["public_getters"]):
                parameters = ", ".join(
                    f"{key_type} key{index + 1}" for index, key_type in enumerate(keys)
                )
                lines.append(f"| `{name}({parameters})` | `view` | `{return_type}` |")
            lines.append("")

        lines.extend(render_named_declarations("Events declared by this source", source_events))

        if declarations["flags"]:
            lines.extend(
                [
                    "### Flags declared by this source",
                    "",
                    "Flag members are powers of two in declaration order; zero is the empty flag, "
                    "and members may be combined with bitwise OR.",
                    "",
                ]
            )
            for flag_name, members in declarations["flags"]:
                lines.append(f"- `{flag_name}`")
                for index, member in enumerate(members):
                    lines.append(
                        f"  - `{member} = {1 << index}` (`1 << {index}`)"
                    )
            lines.append("")

        if declarations["constants"]:
            lines.extend(["### Constants declared by this source", ""])
            lines.extend(
                f"- `{name}: {source_type} = {value}`"
                for name, source_type, value in declarations["constants"]
            )
            lines.append("")

    lines.extend(render_named_declarations("Structs declared by this source", structs))
    lines.extend(render_source_revert_reasons(declarations["revert_reasons"]))
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
    # Keep the source link in one predictable location immediately after the H1.
    without_links = SOURCE_LINK_RE.sub("", content)
    # Removing a link from its old paragraph can leave a second empty line.
    # Normalize those artifacts so regeneration does not degrade page spacing.
    without_links = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", without_links)
    lines = without_links.splitlines()
    if lines and lines[0].startswith("# "):
        while len(lines) > 1 and not lines[1].strip():
            lines.pop(1)
        lines[1:1] = ["", link, ""]
        return "\n".join(lines) + ("\n" if content.endswith("\n") else "")
    return link + "\n\n" + without_links.lstrip()


def first_party_vyper_paths(repo: Path, commit: str) -> list[str]:
    paths = run_git(repo, "ls-tree", "-r", "--name-only", commit, "contracts", "interfaces").splitlines()
    excluded_segments = {"mock", "testing"}
    return sorted(
        path
        for path in paths
        if (path.endswith(".vy") or path.endswith(".vyi"))
        and not excluded_segments.intersection(Path(path).parts)
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


def docs_path(relative_value: Any, *, field: str) -> Path:
    if not isinstance(relative_value, str):
        raise RuntimeError(f"invalid {field}: {relative_value!r}")
    path = (DOCS_ROOT / relative_value).resolve()
    try:
        path.relative_to(DOCS_ROOT)
    except ValueError as exc:
        raise RuntimeError(f"{field} escapes repository: {relative_value}") from exc
    return path


def relative_posix_path(
    value: Any, *, field: str, required_prefix: str | None = None, suffix: str | None = None
) -> str:
    """Validate a repository-relative POSIX path without normalizing it silently."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise RuntimeError(f"invalid {field}: {value!r}")
    normalized = posixpath.normpath(value)
    if value.startswith("/") or normalized != value or normalized.startswith("../"):
        raise RuntimeError(f"invalid {field}: {value!r}")
    if required_prefix is not None and not value.startswith(required_prefix):
        raise RuntimeError(f"invalid {field}: {value!r}")
    if suffix is not None and not value.endswith(suffix):
        raise RuntimeError(f"invalid {field}: {value!r}")
    return value


def verify_protocol_blob(
    protocol_repo: Path,
    commit: str,
    source_path: str,
    expected_blob: Any,
    *,
    field: str,
) -> None:
    """Verify that a pinned protocol path resolves to the expected Git blob."""
    if not re.fullmatch(r"[0-9a-f]{40}", str(expected_blob)):
        raise RuntimeError(f"invalid {field}: {expected_blob!r}")
    try:
        object_type = run_git(
            protocol_repo, "cat-file", "-t", f"{commit}:{source_path}"
        ).strip()
        actual_blob = run_git(
            protocol_repo, "rev-parse", f"{commit}:{source_path}"
        ).strip()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"missing protocol blob for {field}: {source_path}") from exc
    if object_type != "blob":
        raise RuntimeError(
            f"protocol object for {field} is {object_type}, not blob: {source_path}"
        )
    if actual_blob != expected_blob:
        raise RuntimeError(
            f"protocol source drift for {field}: {source_path} "
            f"actual={actual_blob}, expected={expected_blob}"
        )


def foundry_default_profile(config_source: str, *, field: str) -> dict[str, Any]:
    """Read Foundry's default profile from a pinned TOML source."""
    try:
        config = tomllib.loads(config_source)
        profile = config["profile"]["default"]
    except (tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(f"cannot read default Foundry profile from {field}") from exc
    if not isinstance(profile, dict):
        raise RuntimeError(f"invalid default Foundry profile in {field}")
    if (
        not isinstance(profile.get("evm_version"), str)
        or not profile["evm_version"]
        or not isinstance(profile.get("optimizer"), bool)
        or not isinstance(profile.get("optimizer_runs"), int)
        or isinstance(profile.get("optimizer_runs"), bool)
        or profile["optimizer_runs"] < 0
        or not isinstance(profile.get("via_ir"), bool)
        or profile.get("bytecode_hash") not in {"ipfs", "bzzr1", "none"}
    ):
        raise RuntimeError(f"incomplete compiler settings in {field}")
    return profile


def foundry_solc_version(config_source: str, *, field: str) -> str:
    """Read the exact solc release configured for Foundry's default profile."""
    version = foundry_default_profile(config_source, field=field).get("solc_version")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise RuntimeError(f"invalid solc_version in {field}: {version!r}")
    return version


def validate_abi_parameter(
    parameter: Any, *, field: str, event_parameter: bool = False
) -> None:
    if not isinstance(parameter, dict):
        raise RuntimeError(f"{field} must be an object")
    allowed_fields = {"name", "type", "internalType"}
    if event_parameter:
        allowed_fields.add("indexed")
    raw_type = parameter.get("type")
    if isinstance(raw_type, str) and raw_type.startswith("tuple"):
        allowed_fields.add("components")
    unexpected_fields = sorted(set(parameter) - allowed_fields)
    if unexpected_fields:
        raise RuntimeError(
            f"unexpected ABI parameter field(s) in {field}: {unexpected_fields}"
        )
    name = parameter.get("name")
    if not isinstance(name, str) or (
        name and SOLIDITY_IDENTIFIER_RE.fullmatch(name) is None
    ):
        raise RuntimeError(f"invalid ABI parameter name in {field}: {name!r}")
    if not isinstance(raw_type, str):
        raise RuntimeError(f"invalid ABI parameter type in {field}: {raw_type!r}")
    array_match = re.fullmatch(r"([^\[]+)((?:\[[0-9]*\])*)", raw_type)
    if array_match is None:
        raise RuntimeError(f"invalid ABI parameter type in {field}: {raw_type!r}")
    base_type, arrays = array_match.groups()
    for length in re.findall(r"\[([0-9]*)\]", arrays):
        if length and int(length) == 0:
            raise RuntimeError(f"invalid zero-length ABI array in {field}: {raw_type}")
    valid_base = base_type in {"address", "bool", "bytes", "function", "string", "tuple"}
    bytes_match = re.fullmatch(r"bytes([0-9]+)", base_type)
    integer_match = re.fullmatch(r"(u?int)([0-9]+)", base_type)
    fixed_match = re.fullmatch(r"u?fixed([0-9]+)x([0-9]+)", base_type)
    if bytes_match is not None:
        valid_base = 1 <= int(bytes_match.group(1)) <= 32
    elif integer_match is not None:
        bits = int(integer_match.group(2))
        valid_base = 8 <= bits <= 256 and bits % 8 == 0
    elif fixed_match is not None:
        bits = int(fixed_match.group(1))
        decimals = int(fixed_match.group(2))
        valid_base = 8 <= bits <= 256 and bits % 8 == 0 and 1 <= decimals <= 80
    if not valid_base:
        raise RuntimeError(f"invalid ABI parameter type in {field}: {raw_type!r}")

    components = parameter.get("components")
    if base_type == "tuple":
        if not isinstance(components, list) or not components:
            raise RuntimeError(f"tuple ABI parameter lacks components in {field}")
        for index, component in enumerate(components):
            validate_abi_parameter(component, field=f"{field}.components[{index}]")
    elif components is not None:
        raise RuntimeError(f"non-tuple ABI parameter has components in {field}")

    internal_type = parameter.get("internalType")
    if internal_type is not None and (
        not isinstance(internal_type, str) or not internal_type
    ):
        raise RuntimeError(f"invalid internalType in {field}: {internal_type!r}")
    if event_parameter:
        if not isinstance(parameter.get("indexed"), bool):
            raise RuntimeError(f"event ABI parameter lacks boolean indexed in {field}")
    elif "indexed" in parameter:
        raise RuntimeError(f"non-event ABI parameter has indexed in {field}")


def validate_abi_parameters(
    parameters: Any, *, field: str, event_parameters: bool = False
) -> None:
    if not isinstance(parameters, list):
        raise RuntimeError(f"{field} must be an array")
    for index, parameter in enumerate(parameters):
        validate_abi_parameter(
            parameter,
            field=f"{field}[{index}]",
            event_parameter=event_parameters,
        )


def validate_abi_payload(marker: str, abi: Any) -> list[dict[str, Any]]:
    """Validate the ABI schema and reject duplicate canonical declarations."""
    if not isinstance(abi, list) or not abi:
        raise RuntimeError(f"invalid composed Solidity ABI payload for {marker}")
    allowed_types = {"constructor", "error", "event", "fallback", "function", "receive"}
    allowed_fields = {
        "constructor": {"type", "inputs", "stateMutability"},
        "error": {"type", "name", "inputs"},
        "event": {"type", "name", "inputs", "anonymous"},
        "fallback": {"type", "stateMutability"},
        "function": {"type", "name", "inputs", "outputs", "stateMutability"},
        "receive": {"type", "stateMutability"},
    }
    state_mutabilities = {"nonpayable", "payable", "pure", "view"}
    counts = {item_type: 0 for item_type in allowed_types}
    identities: set[tuple[str, str, tuple[str, ...]]] = set()
    for index, item in enumerate(abi):
        field = f"{marker}.abi[{index}]"
        if not isinstance(item, dict):
            raise RuntimeError(f"{field} must be an object")
        item_type = item.get("type")
        if item_type not in allowed_types:
            raise RuntimeError(f"unexpected ABI entry type in {field}: {item_type!r}")
        unexpected_fields = sorted(set(item) - allowed_fields[item_type])
        if unexpected_fields:
            raise RuntimeError(
                f"unexpected ABI entry field(s) in {field}: {unexpected_fields}"
            )
        counts[item_type] += 1

        if item_type in {"function", "event", "error"}:
            name = item.get("name")
            if not isinstance(name, str) or SOLIDITY_IDENTIFIER_RE.fullmatch(name) is None:
                raise RuntimeError(f"invalid ABI declaration name in {field}: {name!r}")
            validate_abi_parameters(
                item.get("inputs"),
                field=f"{field}.inputs",
                event_parameters=item_type == "event",
            )
            identity = (item_type, name, canonical_type_list(item["inputs"]))
            if identity in identities:
                signature = f"{name}({','.join(identity[2])})"
                raise RuntimeError(
                    f"duplicate composed Solidity ABI declaration for {marker}: "
                    f"{item_type} {signature}"
                )
            identities.add(identity)
        if item_type == "function":
            validate_abi_parameters(item.get("outputs"), field=f"{field}.outputs")
            if item.get("stateMutability") not in state_mutabilities:
                raise RuntimeError(f"invalid function mutability in {field}")
        elif item_type == "event":
            if not isinstance(item.get("anonymous"), bool):
                raise RuntimeError(f"event ABI entry lacks boolean anonymous in {field}")
        elif item_type == "constructor":
            validate_abi_parameters(item.get("inputs"), field=f"{field}.inputs")
            if item.get("stateMutability") not in {"nonpayable", "payable"}:
                raise RuntimeError(f"invalid constructor mutability in {field}")
        elif item_type in {"fallback", "receive"}:
            mutability = item.get("stateMutability")
            if mutability not in {"nonpayable", "payable"}:
                raise RuntimeError(f"invalid {item_type} mutability in {field}")
            if item_type == "receive" and mutability != "payable":
                raise RuntimeError(f"receive ABI entry must be payable in {field}")

    if counts["constructor"] != 1:
        raise RuntimeError(
            f"expected exactly one constructor in composed Solidity ABI for {marker}"
        )
    for unique_type in ("fallback", "receive"):
        if counts[unique_type] > 1:
            raise RuntimeError(f"multiple {unique_type} ABI entries for {marker}")
    for required_type in ("function", "event", "error"):
        if counts[required_type] == 0:
            raise RuntimeError(
                f"composed Solidity ABI for {marker} has no {required_type} entries"
            )
    return abi


def canonical_abi_payload(abi: list[dict[str, Any]]) -> tuple[str, ...]:
    """Canonicalize ABI entry/key ordering without discarding reviewed metadata."""
    return tuple(
        sorted(json.dumps(item, sort_keys=True, separators=(",", ":")) for item in abi)
    )


def compiled_artifact_metadata(
    payload: dict[str, Any], *, field: str
) -> tuple[dict[str, Any], ...]:
    """Load compiler metadata documents embedded in a Foundry artifact."""
    structured = payload.get("metadata")
    if not isinstance(structured, dict):
        raise RuntimeError(f"missing structured compiler metadata in {field}")
    raw_value = payload.get("rawMetadata")
    if not isinstance(raw_value, str):
        raise RuntimeError(f"missing raw compiler metadata in {field}")
    try:
        raw = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid rawMetadata JSON in {field}") from exc
    if not isinstance(raw, dict):
        raise RuntimeError(f"rawMetadata must contain an object in {field}")
    for label, metadata in (("metadata", structured), ("rawMetadata", raw)):
        if metadata.get("language") != "Solidity":
            raise RuntimeError(f"invalid compiler language in {field}.{label}")
    return structured, raw


def compiled_artifact_metadata_abi(
    payload: dict[str, Any], *, field: str
) -> list[dict[str, Any]]:
    """Return the compiler-emitted ABI embedded in raw Solidity metadata."""
    _structured, raw = compiled_artifact_metadata(payload, field=field)
    output = raw.get("output")
    if not isinstance(output, dict):
        raise RuntimeError(f"missing compiler metadata output in {field}")
    return validate_abi_payload(f"{field}.rawMetadata.output", output.get("abi"))


def validate_compiled_method_identifiers(
    payload: dict[str, Any], abi: list[dict[str, Any]], *, field: str
) -> None:
    """Require an exact, collision-free Forge method-identifier inventory."""
    expected_signatures = {
        f"{item['name']}({','.join(canonical_type_list(item.get('inputs', [])))})"
        for item in abi
        if item.get("type") == "function"
    }
    identifiers = payload.get("methodIdentifiers")
    if not isinstance(identifiers, dict):
        raise RuntimeError(f"missing methodIdentifiers in {field}")
    if set(identifiers) != expected_signatures:
        raise RuntimeError(
            f"compiled Solidity method-identifier inventory mismatch in {field}: "
            f"missing={sorted(expected_signatures - set(identifiers))}, "
            f"extra={sorted(set(identifiers) - expected_signatures)}"
        )
    selectors: dict[str, list[str]] = defaultdict(list)
    for signature, selector in identifiers.items():
        if not isinstance(selector, str) or re.fullmatch(r"[0-9a-f]{8}", selector) is None:
            raise RuntimeError(
                f"invalid compiled Solidity selector in {field}: "
                f"{signature}={selector!r}"
            )
        selectors[selector].append(signature)
    collisions = {
        selector: signatures
        for selector, signatures in selectors.items()
        if len(signatures) > 1
    }
    if collisions:
        raise RuntimeError(
            f"compiled Solidity selector collision(s) in {field}: {collisions}"
        )


def compiled_artifact_version(payload: dict[str, Any], *, field: str) -> str:
    """Extract the full solc identity recorded by a Foundry compiler artifact."""
    candidates: set[str] = set()
    for metadata in compiled_artifact_metadata(payload, field=field):
        compiler = metadata.get("compiler")
        if isinstance(compiler, dict) and isinstance(compiler.get("version"), str):
            candidates.add(compiler["version"])
    if len(candidates) != 1:
        raise RuntimeError(
            f"cannot resolve one compiler version from {field}: {sorted(candidates)}"
        )
    return next(iter(candidates))


def compiled_artifact_source_manifest(
    payload: dict[str, Any], *, compiler_config_path: str, field: str
) -> dict[str, str]:
    """Return normalized source paths and content hashes from compiler metadata."""
    manifests: dict[str, dict[str, str]] = {}
    compiler_root = posixpath.dirname(compiler_config_path)
    for metadata in compiled_artifact_metadata(payload, field=field):
        sources = metadata.get("sources")
        if not isinstance(sources, dict):
            raise RuntimeError(f"missing compiler source manifest in {field}")
        normalized_sources: dict[str, str] = {}
        for raw_path, source_metadata in sources.items():
            source_path = relative_posix_path(
                raw_path, field=f"{field}.metadata.sources", suffix=".sol"
            )
            if not source_path.startswith("solidity/"):
                source_path = posixpath.normpath(
                    posixpath.join(compiler_root, source_path)
                )
            if not source_path.startswith("solidity/"):
                raise RuntimeError(
                    f"compiler metadata source escapes Solidity root in {field}: {raw_path}"
                )
            if source_path in normalized_sources:
                raise RuntimeError(
                    f"duplicate normalized compiler source in {field}: {source_path}"
                )
            if not isinstance(source_metadata, dict):
                raise RuntimeError(
                    f"invalid compiler source metadata in {field}: {raw_path}"
                )
            content_hash = source_metadata.get("keccak256")
            if (
                not isinstance(content_hash, str)
                or re.fullmatch(r"0x[0-9a-f]{64}", content_hash) is None
            ):
                raise RuntimeError(
                    f"invalid compiler source keccak256 in {field}: "
                    f"{raw_path}={content_hash!r}"
                )
            normalized_sources[source_path] = content_hash
        canonical = json.dumps(
            normalized_sources, sort_keys=True, separators=(",", ":")
        )
        manifests[canonical] = normalized_sources
    if len(manifests) != 1:
        raise RuntimeError(
            f"cannot resolve one compiler source manifest from {field}: "
            f"{len(manifests)} candidates"
        )
    return next(iter(manifests.values()))


def compiled_artifact_settings(
    payload: dict[str, Any], *, field: str
) -> dict[str, Any]:
    """Resolve one compiler settings object from a Foundry artifact."""
    settings_by_json: dict[str, dict[str, Any]] = {}
    for metadata in compiled_artifact_metadata(payload, field=field):
        settings = metadata.get("settings")
        if isinstance(settings, dict):
            canonical = json.dumps(settings, sort_keys=True, separators=(",", ":"))
            settings_by_json[canonical] = settings
    if len(settings_by_json) != 1:
        raise RuntimeError(
            f"cannot resolve one compiler settings object from {field}: "
            f"{len(settings_by_json)} candidates"
        )
    return next(iter(settings_by_json.values()))


def validate_compiled_artifact_settings(
    payload: dict[str, Any],
    *,
    config_source: str,
    config_path: str,
    entry_source: str,
    contract_name: str,
    field: str,
) -> None:
    """Bind compiler metadata settings and compilation target to foundry.toml."""
    profile = foundry_default_profile(config_source, field=config_path)
    settings = compiled_artifact_settings(payload, field=field)
    expected_settings = {
        "evmVersion": profile.get("evm_version"),
        "viaIR": profile.get("via_ir"),
        "optimizer": {
            "enabled": profile.get("optimizer"),
            "runs": profile.get("optimizer_runs"),
        },
        "bytecodeHash": profile.get("bytecode_hash"),
    }
    actual_settings = {
        "evmVersion": settings.get("evmVersion"),
        "viaIR": settings.get("viaIR"),
        "optimizer": settings.get("optimizer"),
        "bytecodeHash": (
            settings.get("metadata", {}).get("bytecodeHash")
            if isinstance(settings.get("metadata"), dict)
            else None
        ),
    }
    if actual_settings != expected_settings:
        raise RuntimeError(
            f"compiled Solidity settings mismatch in {field}: "
            f"actual={actual_settings}, expected={expected_settings}"
        )

    compilation_target = settings.get("compilationTarget")
    if not isinstance(compilation_target, dict) or len(compilation_target) != 1:
        raise RuntimeError(f"invalid compilationTarget in {field}: {compilation_target!r}")
    raw_target, actual_contract = next(iter(compilation_target.items()))
    target_source = relative_posix_path(
        raw_target, field=f"{field}.settings.compilationTarget", suffix=".sol"
    )
    if not target_source.startswith("solidity/"):
        target_source = posixpath.normpath(
            posixpath.join(posixpath.dirname(config_path), target_source)
        )
    if target_source != entry_source or actual_contract != contract_name:
        raise RuntimeError(
            f"compiled Solidity target mismatch in {field}: "
            f"actual={target_source}:{actual_contract}, "
            f"expected={entry_source}:{contract_name}"
        )


def path_within(root: Path, relative_value: Any, *, field: str) -> Path:
    relative = relative_posix_path(relative_value, field=field)
    root = root.resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeError(f"{field} escapes artifact root: {relative}") from exc
    return resolved


def composed_solidity_abi_references(
    protocol_repo: Path,
    baseline: dict[str, Any],
    compiled_artifact_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Verify reviewed Solidity ABIs, exact import closures, and optional fresh builds."""
    configured = baseline.get("composed_solidity_abis", {})
    if not isinstance(configured, dict):
        raise RuntimeError("composed_solidity_abis must be an object")

    commit = baseline["protocol_commit"]
    abi_directory = (DOCS_ROOT / "reference" / "abis").resolve()
    if compiled_artifact_root is not None:
        compiled_artifact_root = compiled_artifact_root.resolve()
        if not compiled_artifact_root.is_dir():
            raise RuntimeError(
                f"missing Solidity compiler artifact root: {compiled_artifact_root}"
            )
    references: dict[str, dict[str, Any]] = {}
    used_docs: set[Path] = set()
    used_artifacts: set[Path] = set()
    used_compiled_artifacts: set[str] = set()
    expected_entry_fields = {
        "contract_name",
        "display_name",
        "entry_source",
        "compiler_version",
        "compiler_config_path",
        "compiler_config_blob",
        "artifact_path",
        "artifact_sha256",
        "compiled_artifact_path",
        "documentation_path",
        "source_blobs",
    }
    for marker, value in sorted(configured.items()):
        if (
            not isinstance(marker, str)
            or SOLIDITY_IDENTIFIER_RE.fullmatch(marker) is None
            or not isinstance(value, dict)
        ):
            raise RuntimeError(f"invalid composed Solidity ABI entry: {marker!r}")
        missing_fields = sorted(expected_entry_fields - set(value))
        unexpected_fields = sorted(set(value) - expected_entry_fields)
        if missing_fields or unexpected_fields:
            raise RuntimeError(
                f"invalid composed Solidity ABI schema for {marker}: "
                f"missing={missing_fields}, unexpected={unexpected_fields}"
            )
        contract_name = value.get("contract_name")
        display_name = value.get("display_name")
        compiler_version = value.get("compiler_version")
        if (
            not isinstance(contract_name, str)
            or SOLIDITY_IDENTIFIER_RE.fullmatch(contract_name) is None
        ):
            raise RuntimeError(f"invalid contract_name for {marker}")
        if (
            not isinstance(display_name, str)
            or not display_name.strip()
            or display_name != display_name.strip()
            or re.fullmatch(r"[A-Za-z0-9_. -]+", display_name) is None
        ):
            raise RuntimeError(f"invalid display_name for {marker}: {display_name!r}")
        compiler_match = SOLIDITY_VERSION_RE.fullmatch(str(compiler_version))
        if compiler_match is None:
            raise RuntimeError(f"invalid compiler_version for {marker}: {compiler_version!r}")

        entry_source = relative_posix_path(
            value.get("entry_source"),
            field=f"{marker}.entry_source",
            required_prefix="solidity/",
            suffix=".sol",
        )
        config_path = relative_posix_path(
            value.get("compiler_config_path"),
            field=f"{marker}.compiler_config_path",
            required_prefix="solidity/",
            suffix=".toml",
        )
        verify_protocol_blob(
            protocol_repo,
            commit,
            config_path,
            value.get("compiler_config_blob"),
            field=f"{marker}.compiler_config_blob",
        )
        try:
            config_source = git_show(protocol_repo, commit, config_path)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"missing compiler config for {marker}: {config_path}") from exc
        configured_solc = foundry_solc_version(
            config_source, field=f"{marker}.compiler_config_path"
        )
        if configured_solc != compiler_match.group(1):
            raise RuntimeError(
                f"compiler version/config mismatch for {marker}: "
                f"artifact={compiler_version}, foundry={configured_solc}"
            )

        source_blobs = value.get("source_blobs")
        if not isinstance(source_blobs, dict) or not source_blobs:
            raise RuntimeError(f"missing source_blobs for {marker}")
        manifest_paths: set[str] = set()
        for source_path, expected_blob in source_blobs.items():
            validated_path = relative_posix_path(
                source_path,
                field=f"{marker}.source_blobs path",
                required_prefix="solidity/",
                suffix=".sol",
            )
            manifest_paths.add(validated_path)
            if not re.fullmatch(r"[0-9a-f]{40}", str(expected_blob)):
                raise RuntimeError(
                    f"invalid composed Solidity source blob for {marker}: "
                    f"{source_path!r}={expected_blob!r}"
                )
        source_closure = recursive_solidity_source_closure(
            protocol_repo, commit, entry_source
        )
        missing_manifest_paths = sorted(source_closure - manifest_paths)
        extra_manifest_paths = sorted(manifest_paths - source_closure)
        if missing_manifest_paths or extra_manifest_paths:
            raise RuntimeError(
                f"composed Solidity source manifest mismatch for {marker}: "
                f"missing={missing_manifest_paths}, extra={extra_manifest_paths}"
            )
        for source_path, expected_blob in sorted(source_blobs.items()):
            verify_protocol_blob(
                protocol_repo,
                commit,
                source_path,
                expected_blob,
                field=f"{marker}.source_blobs[{source_path}]",
            )

        artifact_path = docs_path(value.get("artifact_path"), field=f"{marker}.artifact_path")
        doc_path = docs_path(value.get("documentation_path"), field=f"{marker}.documentation_path")
        try:
            artifact_path.relative_to(abi_directory)
        except ValueError as exc:
            raise RuntimeError(
                f"composed Solidity ABI artifact must be under reference/abis: {artifact_path}"
            ) from exc
        if artifact_path in used_artifacts or doc_path in used_docs:
            raise RuntimeError(f"duplicate composed Solidity artifact or page for {marker}")
        used_artifacts.add(artifact_path)
        used_docs.add(doc_path)
        if not artifact_path.is_file() or artifact_path.suffix != ".json":
            raise RuntimeError(f"missing composed Solidity ABI artifact: {artifact_path}")
        if not doc_path.is_file() or doc_path.suffix != ".md":
            raise RuntimeError(f"missing composed Solidity ABI page: {doc_path}")

        expected_sha256 = value.get("artifact_sha256")
        actual_sha256 = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if not re.fullmatch(r"[0-9a-f]{64}", str(expected_sha256)):
            raise RuntimeError(f"invalid artifact_sha256 for {marker}: {expected_sha256!r}")
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"composed Solidity ABI hash mismatch for {marker}: "
                f"actual={actual_sha256}, expected={expected_sha256}"
            )

        try:
            abi = validate_abi_payload(marker, json.loads(artifact_path.read_text()))
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"invalid composed Solidity ABI JSON for {marker}") from exc

        compiled_artifact_relative = relative_posix_path(
            value.get("compiled_artifact_path"),
            field=f"{marker}.compiled_artifact_path",
            required_prefix="solidity/out/",
            suffix=".json",
        )
        if compiled_artifact_relative in used_compiled_artifacts:
            raise RuntimeError(
                f"duplicate composed Solidity build artifact: {compiled_artifact_relative}"
            )
        used_compiled_artifacts.add(compiled_artifact_relative)
        compiled_artifact_path: Path | None = None
        if compiled_artifact_root is not None:
            compiled_artifact_path = path_within(
                compiled_artifact_root,
                compiled_artifact_relative,
                field=f"{marker}.compiled_artifact_path",
            )
            if not compiled_artifact_path.is_file():
                raise RuntimeError(
                    f"missing freshly compiled Solidity artifact for {marker}: "
                    f"{compiled_artifact_path}"
                )
            try:
                compiled_payload = json.loads(compiled_artifact_path.read_text())
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"invalid freshly compiled Solidity artifact JSON for {marker}"
                ) from exc
            if not isinstance(compiled_payload, dict):
                raise RuntimeError(
                    f"freshly compiled Solidity artifact must be an object for {marker}"
                )
            actual_compiler_version = compiled_artifact_version(
                compiled_payload, field=str(compiled_artifact_path)
            )
            if actual_compiler_version != compiler_version:
                raise RuntimeError(
                    f"compiled Solidity version mismatch for {marker}: "
                    f"actual={actual_compiler_version}, expected={compiler_version}"
                )
            validate_compiled_artifact_settings(
                compiled_payload,
                config_source=config_source,
                config_path=config_path,
                entry_source=entry_source,
                contract_name=contract_name,
                field=str(compiled_artifact_path),
            )
            compiled_source_manifest = compiled_artifact_source_manifest(
                compiled_payload,
                compiler_config_path=config_path,
                field=str(compiled_artifact_path),
            )
            compiled_sources = set(compiled_source_manifest)
            missing_compiled_sources = sorted(source_closure - compiled_sources)
            extra_compiled_sources = sorted(compiled_sources - source_closure)
            if missing_compiled_sources or extra_compiled_sources:
                raise RuntimeError(
                    f"compiled Solidity source-set mismatch for {marker}: "
                    f"missing={missing_compiled_sources}, extra={extra_compiled_sources}"
                )
            for source_path, expected_keccak in sorted(
                compiled_source_manifest.items()
            ):
                try:
                    source_bytes = git_show_bytes(protocol_repo, commit, source_path)
                except subprocess.CalledProcessError as exc:
                    raise RuntimeError(
                        f"missing pinned Solidity source bytes for {marker}: {source_path}"
                    ) from exc
                actual_keccak = cast_keccak256(
                    source_bytes,
                    field=f"{marker}.compiled source {source_path}",
                )
                if actual_keccak != expected_keccak:
                    raise RuntimeError(
                        f"compiled Solidity source-content mismatch for {marker}: "
                        f"{source_path} actual={actual_keccak}, "
                        f"expected={expected_keccak}"
                    )
            compiled_abi = validate_abi_payload(
                f"{marker}.compiled", compiled_payload.get("abi")
            )
            metadata_abi = compiled_artifact_metadata_abi(
                compiled_payload, field=str(compiled_artifact_path)
            )
            if canonical_abi_payload(metadata_abi) != canonical_abi_payload(compiled_abi):
                raise RuntimeError(
                    f"compiled Solidity artifact/metadata ABI mismatch for {marker}: "
                    f"{compiled_artifact_path}"
                )
            validate_compiled_method_identifiers(
                compiled_payload, compiled_abi, field=str(compiled_artifact_path)
            )
            if canonical_abi_payload(compiled_abi) != canonical_abi_payload(abi):
                raise RuntimeError(
                    f"freshly compiled Solidity ABI mismatch for {marker}: "
                    f"{compiled_artifact_path}"
                )
        references[marker] = {
            **value,
            "artifact_path_resolved": artifact_path,
            "documentation_path_resolved": doc_path,
            "compiled_artifact_path_resolved": compiled_artifact_path,
            "abi": abi,
        }

    actual_artifacts = (
        {path.resolve() for path in abi_directory.rglob("*.json") if path.is_file()}
        if abi_directory.is_dir()
        else set()
    )
    orphan_artifacts = sorted(actual_artifacts - used_artifacts)
    if orphan_artifacts:
        raise RuntimeError(
            "unconfigured composed Solidity ABI artifact(s): "
            + ", ".join(str(path.relative_to(DOCS_ROOT)) for path in orphan_artifacts)
        )
    return references


def configured_solidity_inherited_api_references(
    baseline: dict[str, Any],
    solidity_sources: Iterable[str],
    composed_references: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Resolve only explicitly configured inherited APIs for top-level sources."""
    configured = baseline.get("solidity_inherited_api_markers", {})
    if not isinstance(configured, dict):
        raise RuntimeError("solidity_inherited_api_markers must be an object")
    source_set = set(solidity_sources)
    references: dict[str, dict[str, Any]] = {}
    for raw_source_path, marker in configured.items():
        source_path = relative_posix_path(
            raw_source_path,
            field="solidity_inherited_api_markers source path",
            required_prefix="solidity/",
            suffix=".sol",
        )
        if source_path not in source_set:
            raise RuntimeError(
                "inherited Solidity API configured for undiscovered source: "
                f"{source_path}"
            )
        if not isinstance(marker, str) or marker not in composed_references:
            raise RuntimeError(
                f"unknown composed Solidity API marker for {source_path}: {marker!r}"
            )
        references[source_path] = composed_references[marker]
    return references


def validate_generated_marker_topology(
    docs: dict[str, Path], extra_expected: dict[Path, str] | None = None
) -> None:
    """Reject duplicate, orphaned, mismatched, or misplaced generated blocks."""
    expected_by_doc = {
        doc_path.resolve(): Path(source_path).stem
        for source_path, doc_path in docs.items()
    }
    for doc_path, marker in (extra_expected or {}).items():
        resolved = doc_path.resolve()
        if resolved in expected_by_doc:
            raise RuntimeError(
                f"multiple generated API markers configured for {doc_path.relative_to(DOCS_ROOT)}"
            )
        expected_by_doc[resolved] = marker
    marker_paths: dict[str, list[Path]] = defaultdict(list)
    for doc_path, marker in expected_by_doc.items():
        marker_paths[marker].append(doc_path)
    collisions = {
        marker: paths for marker, paths in marker_paths.items() if len(paths) > 1
    }
    if collisions:
        rendered = "; ".join(
            f"{marker}: "
            + ", ".join(str(path.relative_to(DOCS_ROOT)) for path in sorted(paths))
            for marker, paths in sorted(collisions.items())
        )
        raise RuntimeError(f"generated API marker collision(s): {rendered}")
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
    json_paths = [path for path in paths if path.endswith(".json")]
    prefix = "scripts/abis/"
    nested_paths: list[str] = []
    paths_by_stem: dict[str, list[str]] = defaultdict(list)

    for path in json_paths:
        if not path.startswith(prefix):
            raise RuntimeError(
                f"tracked ABI JSON path is outside {prefix.rstrip('/')}: {path}"
            )
        relative_path = path[len(prefix) :]
        if not relative_path or "/" in relative_path:
            nested_paths.append(path)
        paths_by_stem[Path(relative_path).stem].append(path)

    duplicate_stems = {
        stem: candidates
        for stem, candidates in paths_by_stem.items()
        if len(candidates) > 1
    }
    layout_errors: list[str] = []
    if nested_paths:
        layout_errors.append(
            "nested ABI JSON paths are not allowed; expected direct scripts/abis/*.json "
            f"children: {sorted(nested_paths)}"
        )
    if duplicate_stems:
        layout_errors.append(f"duplicate ABI stems: {duplicate_stems}")
    if layout_errors:
        raise RuntimeError("; ".join(layout_errors))

    return {
        stem: candidates[0]
        for stem, candidates in paths_by_stem.items()
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--protocol-repo",
        type=Path,
        default=Path(os.environ["RIPE_PROTOCOL_REPO"]) if "RIPE_PROTOCOL_REPO" in os.environ else None,
        help="Path to a ripe-protocol clone containing the pinned commit",
    )
    parser.add_argument(
        "--compiled-artifact-root",
        type=Path,
        default=(
            Path(os.environ["RIPE_COMPILED_ARTIFACT_ROOT"])
            if "RIPE_COMPILED_ARTIFACT_ROOT" in os.environ
            else None
        ),
        help=(
            "Root containing freshly compiled artifacts at the baseline's "
            "compiled_artifact_path values"
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.protocol_repo is None:
        parser.error("--protocol-repo or RIPE_PROTOCOL_REPO is required")
    protocol_repo = args.protocol_repo.resolve()
    baseline = json.loads(BASELINE_PATH.read_text())
    validate_baseline_identity(baseline)
    commit = baseline["protocol_commit"]
    expected_tree = baseline["protocol_tree"]

    resolved_commit = run_git(protocol_repo, "rev-parse", f"{commit}^{{commit}}").strip()
    resolved_tree = run_git(protocol_repo, "rev-parse", f"{commit}^{{tree}}").strip()
    if resolved_commit != commit or resolved_tree != expected_tree:
        raise RuntimeError(
            f"protocol identity mismatch: commit={resolved_commit}, tree={resolved_tree}, "
            f"expected commit={commit}, tree={expected_tree}"
        )

    vyper_sources = first_party_vyper_paths(protocol_repo, commit)
    solidity_sources = first_party_solidity_paths(protocol_repo, commit)
    docs = configured_doc_paths(baseline, vyper_sources + solidity_sources)
    composed_references = composed_solidity_abi_references(
        protocol_repo,
        baseline,
        args.compiled_artifact_root,
    )
    inherited_solidity_references = configured_solidity_inherited_api_references(
        baseline, solidity_sources, composed_references
    )
    validate_generated_marker_topology(
        docs,
        {
            reference["documentation_path_resolved"]: marker
            for marker, reference in composed_references.items()
        },
    )
    abis = abi_paths(protocol_repo, commit)
    changed: list[Path] = []
    source_by_path = {
        source_path: git_show(protocol_repo, commit, source_path)
        for source_path in vyper_sources
    }
    source_catalog: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for source in source_by_path.values():
        for function in source_declarations(source)["functions"]:
            if function["external"]:
                source_catalog[function["name"]].append(function)

    for source_path in vyper_sources:
        contract = Path(source_path).stem
        doc_path = docs[source_path]
        source = source_by_path[source_path]
        abi = None
        if contract in abis:
            abi = json.loads(git_show(protocol_repo, commit, abis[contract]))
        block = render_api_block(contract, source_path, source, abi, source_catalog)
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
        block = render_solidity_api_block(
            source_path,
            source,
            documentation_path=doc_path,
            inherited_reference=inherited_solidity_references.get(source_path),
        )
        updated = replace_generated_block(pinned, contract, block)
        if updated != current:
            changed.append(doc_path)
            if args.write:
                doc_path.write_text(updated)

    # Inherited vendored Solidity surfaces are represented by compiled ABI
    # snapshots whose artifact hash and complete compiler-input blob manifest
    # are bound in the baseline.
    for marker, reference in composed_references.items():
        doc_path = reference["documentation_path_resolved"]
        current = doc_path.read_text()
        block = render_composed_solidity_abi_block(marker, reference)
        updated = replace_generated_block(current, marker, block)
        if updated != current:
            changed.append(doc_path)
            if args.write:
                doc_path.write_text(updated)

    if args.check and changed:
        print("Generated API reference is out of date:", file=sys.stderr)
        for path in changed:
            print(f"  {path.relative_to(DOCS_ROOT)}", file=sys.stderr)
        return 1

    checked_links = validate_pinned_protocol_links(protocol_repo, baseline)

    verb = "updated" if args.write else "verified"
    compiled_reference_count = sum(
        reference["compiled_artifact_path_resolved"] is not None
        for reference in composed_references.values()
    )
    print(
        f"{verb} {len(vyper_sources)} "
        f"Vyper/interface pages and {len(solidity_sources)} "
        f"first-party Solidity pages plus {len(composed_references)} "
        f"composed Solidity ABI reference; verified {compiled_reference_count} "
        f"fresh compiled Solidity ABI and {checked_links} pinned protocol links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
