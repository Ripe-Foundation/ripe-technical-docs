"""Trust policy for protocol objects consumed by documentation tooling."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys
from typing import Any


TRUSTED_PROTOCOL_REPOSITORY = "https://github.com/Ripe-Foundation/ripe-protocol"
TRUSTED_PROTOCOL_BRANCHES = frozenset({"master", "rh"})


def validate_baseline_identity(baseline: dict[str, Any]) -> None:
    """Reject untrusted repositories/branches and malformed Git identities."""
    repository = baseline.get("protocol_repository")
    branch = baseline.get("protocol_branch")
    if repository != TRUSTED_PROTOCOL_REPOSITORY:
        raise RuntimeError(f"untrusted protocol_repository: {repository!r}")
    if branch not in TRUSTED_PROTOCOL_BRANCHES:
        raise RuntimeError(f"untrusted protocol_branch: {branch!r}")
    for field in ("protocol_commit", "protocol_tree"):
        value = baseline.get(field)
        if not re.fullmatch(r"[0-9a-f]{40}", str(value or "")):
            raise RuntimeError(f"invalid {field}: {value!r}")


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("reference/implementation-baseline.json")
    validate_baseline_identity(json.loads(path.read_text()))
    print(f"verified trusted protocol identity policy in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
