#!/usr/bin/env python3
"""Advisory availability checks for published external documentation links."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    OpenerDirector,
    Request,
    build_opener,
)

import check_markdown as markdown
import baseline_policy


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "reference" / "implementation-baseline.json"
IGNORE_PATH = ROOT / ".markdownignore"

USER_AGENT = (
    "RipeTechnicalDocsLinkCheck/1.0 "
    "(+https://github.com/Ripe-Foundation/ripe-technical-docs)"
)
REQUEST_TIMEOUT_SECONDS = 10.0
RETRY_DELAYS_SECONDS = (0.5, 1.5)
RETRYABLE_HTTP_STATUSES = frozenset({408, 425, 429, 500, 502, 503, 504})

# This job makes requests only to project-controlled sites and the project's
# GitHub organization. Extending the documentation to another origin requires
# an explicit review of this scope first.
APPROVED_HOST_PATHS: dict[str, tuple[str, ...] | None] = {
    "docs.ripe.finance": None,
    "params.ripe.finance": None,
    "github.com": ("/Ripe-Foundation/",),
}
LINE_FRAGMENT_RE = re.compile(r"L[0-9]+(?:-L[0-9]+)?")


@dataclass(frozen=True)
class ExternalLink:
    url: str
    sources: tuple[str, ...]


@dataclass(frozen=True)
class LinkInventory:
    links: tuple[ExternalLink, ...]
    skipped_pinned_urls: tuple[str, ...]


@dataclass(frozen=True)
class CheckResult:
    link: ExternalLink
    ok: bool
    attempts: int
    status: int | None = None
    error: str | None = None


class UnsafeExternalUrlError(ValueError):
    """Raised when an initial URL or redirect leaves the approved HTTPS scope."""


def _ignore_patterns(path: Path) -> tuple[str, ...]:
    if not path.is_file():
        return ()
    return tuple(
        line
        for raw in path.read_text().splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    )


def _is_unpublished(path: Path, root: Path, patterns: tuple[str, ...]) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(
        markdown._matches_root_pattern(relative_parts, pattern)  # noqa: SLF001
        for pattern in patterns
    )


def is_exact_pinned_protocol_blob(
    url: str, protocol_repository: str, protocol_commit: str
) -> bool:
    """Return whether the offline parity job proves this exact source URL."""
    parsed = urlsplit(url)
    repository = urlsplit(protocol_repository.rstrip("/"))
    if (
        parsed.scheme != "https"
        or parsed.scheme != repository.scheme
        or parsed.netloc != repository.netloc
        or parsed.query
    ):
        return False
    prefix = f"{repository.path.rstrip('/')}/blob/{protocol_commit}/"
    if not parsed.path.startswith(prefix) or parsed.path == prefix:
        return False
    return not parsed.fragment or bool(LINE_FRAGMENT_RE.fullmatch(parsed.fragment))


def discover_external_links(
    root: Path = ROOT,
    baseline_path: Path = BASELINE_PATH,
    ignore_path: Path = IGNORE_PATH,
) -> LinkInventory:
    """Collect unique external links from published Markdown only."""
    baseline = json.loads(baseline_path.read_text())
    baseline_policy.validate_baseline_identity(baseline)
    protocol_repository = baseline.get("protocol_repository")
    protocol_commit = baseline.get("protocol_commit")
    if not isinstance(protocol_repository, str) or not isinstance(protocol_commit, str):
        raise ValueError("implementation baseline lacks protocol repository identity")

    patterns = _ignore_patterns(ignore_path)
    sources_by_url: dict[str, set[str]] = {}
    skipped: set[str] = set()
    files = sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)
    for path in files:
        if _is_unpublished(path, root, patterns):
            continue
        source = str(path.relative_to(root))
        for target in markdown.link_targets(path.read_text()):
            if not target.startswith(("http://", "https://")):
                continue
            if is_exact_pinned_protocol_blob(
                target, protocol_repository, protocol_commit
            ):
                skipped.add(target)
                continue
            sources_by_url.setdefault(target, set()).add(source)

    links = tuple(
        ExternalLink(url, tuple(sorted(sources)))
        for url, sources in sorted(sources_by_url.items())
    )
    return LinkInventory(links, tuple(sorted(skipped)))


def external_url_scope_error(url: str) -> str | None:
    """Return a reason when a URL is outside the explicit request scope."""
    if any(ord(char) < 32 or char.isspace() for char in url):
        return "URL contains whitespace or control characters"
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        return f"invalid URL: {error}"
    if parsed.scheme != "https":
        return "only HTTPS URLs are allowed"
    if not parsed.hostname:
        return "URL has no hostname"
    if parsed.username is not None or parsed.password is not None:
        return "credentials in URLs are not allowed"
    if port not in (None, 443):
        return "only the default HTTPS port is allowed"

    path_prefixes = APPROVED_HOST_PATHS.get(parsed.hostname.lower())
    if parsed.hostname.lower() not in APPROVED_HOST_PATHS:
        return f"hostname is outside the approved scope: {parsed.hostname}"
    if path_prefixes is not None and not any(
        parsed.path.startswith(prefix) for prefix in path_prefixes
    ):
        return f"path is outside the approved scope for {parsed.hostname}"
    return None


class ScopedHttpsRedirectHandler(HTTPRedirectHandler):
    max_repeats = 2
    max_redirections = 5

    def redirect_request(  # type: ignore[override]
        self,
        req: Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> Request | None:
        target = urljoin(req.full_url, newurl)
        if reason := external_url_scope_error(target):
            raise UnsafeExternalUrlError(f"refusing redirect to {target}: {reason}")
        return super().redirect_request(req, fp, code, msg, headers, target)


def _error_text(error: BaseException) -> str:
    if isinstance(error, HTTPError):
        return f"HTTP {error.code} {error.reason}"
    if isinstance(error, URLError):
        return f"network error: {error.reason}"
    return str(error) or error.__class__.__name__


def check_link(
    link: ExternalLink,
    opener: OpenerDirector,
    sleeper: Callable[[float], None] = time.sleep,
) -> CheckResult:
    """GET one link with bounded retries and return a structured result."""
    if reason := external_url_scope_error(link.url):
        return CheckResult(link, False, 0, error=reason)

    request = Request(link.url, headers={"User-Agent": USER_AGENT}, method="GET")
    attempts = len(RETRY_DELAYS_SECONDS) + 1
    for attempt in range(1, attempts + 1):
        status: int | None = None
        try:
            with opener.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                final_url = response.geturl() or link.url
                if reason := external_url_scope_error(final_url):
                    raise UnsafeExternalUrlError(
                        f"final response URL {final_url} is not allowed: {reason}"
                    )
                status = response.getcode()
                response.read(1)
            if status is not None and 200 <= status < 400:
                return CheckResult(link, True, attempt, status=status)
            error = f"unexpected HTTP status {status}"
            retryable = status in RETRYABLE_HTTP_STATUSES
        except UnsafeExternalUrlError as caught:
            return CheckResult(link, False, attempt, error=str(caught))
        except HTTPError as caught:
            status = caught.code
            error = _error_text(caught)
            retryable = caught.code in RETRYABLE_HTTP_STATUSES
            if caught.fp is not None:
                caught.close()
            if 300 <= caught.code < 400:
                return CheckResult(link, True, attempt, status=caught.code)
        except (URLError, TimeoutError, OSError) as caught:
            error = _error_text(caught)
            retryable = True

        if not retryable or attempt == attempts:
            return CheckResult(link, False, attempt, status=status, error=error)
        sleeper(RETRY_DELAYS_SECONDS[attempt - 1])

    raise AssertionError("unreachable retry state")


def check_inventory(
    inventory: LinkInventory,
    opener: OpenerDirector | None = None,
    sleeper: Callable[[float], None] = time.sleep,
) -> tuple[CheckResult, ...]:
    active_opener = opener or build_opener(ScopedHttpsRedirectHandler())
    return tuple(check_link(link, active_opener, sleeper) for link in inventory.links)


def _workflow_escape(value: str) -> str:
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _markdown_code(value: str) -> str:
    return f"`{value.replace('`', chr(92) + '`')}`"


def report_results(
    inventory: LinkInventory,
    results: tuple[CheckResult, ...],
    summary_path: Path | None = None,
) -> int:
    failures = tuple(result for result in results if not result.ok)
    for result in results:
        sources = ", ".join(result.link.sources)
        if result.ok:
            print(
                f"PASS {result.link.url} (HTTP {result.status}; "
                f"{result.attempts} attempt(s); {sources})"
            )
            continue
        detail = result.error or "unknown error"
        print(
            f"FAIL {result.link.url} ({detail}; {result.attempts} attempt(s); "
            f"{sources})",
            file=sys.stderr,
        )
        if os.environ.get("GITHUB_ACTIONS") == "true":
            message = _workflow_escape(f"{result.link.url} ({sources}): {detail}")
            print(f"::warning title=External documentation link unavailable::{message}")

    if summary_path is not None:
        lines = ["### Advisory external-link check", ""]
        if failures:
            lines.append(
                f"Warning: {len(failures)} of {len(results)} checked link(s) failed."
            )
            lines.append("")
            for result in failures:
                detail = result.error or "unknown error"
                lines.append(
                    f"- {_markdown_code(result.link.url)}: {detail} "
                    f"({_markdown_code(', '.join(result.link.sources))})"
                )
        else:
            lines.append(f"All {len(results)} checked external link(s) responded.")
        lines.extend(
            [
                "",
                f"Skipped {len(inventory.skipped_pinned_urls)} exact pinned "
                "protocol source URL(s) already covered by offline parity validation.",
                "",
            ]
        )
        with summary_path.open("a") as summary:
            summary.write("\n".join(lines))

    print(
        f"checked {len(results)} external link(s); skipped "
        f"{len(inventory.skipped_pinned_urls)} exact pinned protocol source URL(s)"
    )
    return 1 if failures else 0


def main() -> int:
    inventory = discover_external_links()
    results = check_inventory(inventory)
    raw_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    summary_path = Path(raw_summary) if raw_summary else None
    return report_results(inventory, results, summary_path)


if __name__ == "__main__":
    raise SystemExit(main())
