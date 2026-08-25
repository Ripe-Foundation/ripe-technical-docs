from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock
from urllib.error import HTTPError, URLError
from urllib.request import Request

import check_external_links as external


PROTOCOL_REPOSITORY = "https://github.com/Ripe-Foundation/ripe-protocol"
PROTOCOL_COMMIT = "a" * 40


class FakeResponse:
    def __init__(self, status: int, url: str) -> None:
        self.status = status
        self.url = url
        self.read_count = 0

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def getcode(self) -> int:
        return self.status

    def geturl(self) -> str:
        return self.url

    def read(self, size: int = -1) -> bytes:
        self.read_count += 1
        return b"x"[:size]


class ExternalLinkTests(unittest.TestCase):
    def _write_baseline(self, root: Path) -> Path:
        path = root / "reference" / "implementation-baseline.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "protocol_repository": PROTOCOL_REPOSITORY,
                    "protocol_branch": "rh",
                    "protocol_commit": PROTOCOL_COMMIT,
                    "protocol_tree": "b" * 40,
                }
            )
        )
        return path

    def test_discovery_is_published_deduplicated_and_skips_only_exact_pin(self) -> None:
        pinned = (
            f"{PROTOCOL_REPOSITORY}/blob/{PROTOCOL_COMMIT}/contracts/core/Teller.vy"
        )
        wrong_pin = f"{PROTOCOL_REPOSITORY}/blob/{'b' * 40}/contracts/core/Teller.vy"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = self._write_baseline(root)
            ignore = root / ".markdownignore"
            ignore.write_text("private/**\n")
            (root / "README.md").write_text(
                "[Docs](https://docs.ripe.finance/)\n"
                "[Docs again](https://docs.ripe.finance/)\n"
                f"[Pinned source]({pinned})\n"
                f"[Wrong pin]({wrong_pin})\n"
                "```text\n[Hidden code](https://params.ripe.finance/)\n```\n"
            )
            (root / "guide.md").write_text(
                "[Docs](https://docs.ripe.finance/)\n"
                "[Params](https://params.ripe.finance/?tab=deployments)\n"
            )
            hidden = root / "private" / "notes.md"
            hidden.parent.mkdir()
            hidden.write_text("[Hidden](https://outside.example/)\n")

            inventory = external.discover_external_links(root, baseline, ignore)

        self.assertEqual((pinned,), inventory.skipped_pinned_urls)
        self.assertEqual(
            [
                "https://docs.ripe.finance/",
                wrong_pin,
                "https://params.ripe.finance/?tab=deployments",
            ],
            [link.url for link in inventory.links],
        )
        self.assertEqual(
            ("README.md", "guide.md"),
            inventory.links[0].sources,
        )

    def test_repository_inventory_is_within_approved_request_scope(self) -> None:
        inventory = external.discover_external_links()
        out_of_scope = {
            link.url: reason
            for link in inventory.links
            if (reason := external.external_url_scope_error(link.url)) is not None
        }
        self.assertEqual({}, out_of_scope)

    def test_exact_pinned_blob_match_rejects_near_matches(self) -> None:
        exact = f"{PROTOCOL_REPOSITORY}/blob/{PROTOCOL_COMMIT}/contracts/core/Teller.vy"
        self.assertTrue(
            external.is_exact_pinned_protocol_blob(
                exact, PROTOCOL_REPOSITORY, PROTOCOL_COMMIT
            )
        )
        self.assertTrue(
            external.is_exact_pinned_protocol_blob(
                exact + "#L10-L12", PROTOCOL_REPOSITORY, PROTOCOL_COMMIT
            )
        )
        for near_match in (
            PROTOCOL_REPOSITORY,
            exact.replace("/blob/", "/tree/"),
            exact.replace(PROTOCOL_COMMIT, "b" * 40),
            exact + "?plain=1",
            exact + "#functions",
            exact.replace("https://", "http://"),
        ):
            with self.subTest(url=near_match):
                self.assertFalse(
                    external.is_exact_pinned_protocol_blob(
                        near_match, PROTOCOL_REPOSITORY, PROTOCOL_COMMIT
                    )
                )

    def test_discovery_enforces_the_shared_baseline_trust_policy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = self._write_baseline(root)
            payload = json.loads(baseline.read_text())
            payload["protocol_repository"] = "https://evil.example/protocol"
            baseline.write_text(json.dumps(payload))
            (root / "README.md").write_text("[Docs](https://docs.ripe.finance/)\n")

            with self.assertRaisesRegex(RuntimeError, "untrusted protocol_repository"):
                external.discover_external_links(
                    root, baseline, root / ".markdownignore"
                )

    def test_request_scope_is_https_credentials_free_and_explicit(self) -> None:
        for allowed in (
            "https://docs.ripe.finance/guide",
            "https://params.ripe.finance/?tab=deployments",
            "https://github.com/Ripe-Foundation/ripe-protocol",
            "https://docs.ripe.finance:443/",
        ):
            with self.subTest(url=allowed):
                self.assertIsNone(external.external_url_scope_error(allowed))

        for rejected in (
            "http://docs.ripe.finance/",
            "https://evil.example/",
            "https://github.com/another-org/repo",
            "https://user:secret@docs.ripe.finance/",
            "https://docs.ripe.finance:444/",
            "https://docs.ripe.finance/a\nsecond",
        ):
            with self.subTest(url=rejected):
                self.assertIsNotNone(external.external_url_scope_error(rejected))

    def test_redirect_handler_allows_only_approved_https_targets(self) -> None:
        handler = external.ScopedHttpsRedirectHandler()
        request = Request("https://docs.ripe.finance/start")
        redirected = handler.redirect_request(
            request, None, 302, "Found", Message(), "/next"
        )
        self.assertEqual("https://docs.ripe.finance/next", redirected.full_url)

        for target in ("http://docs.ripe.finance/", "https://evil.example/"):
            with (
                self.subTest(url=target),
                self.assertRaises(external.UnsafeExternalUrlError),
            ):
                handler.redirect_request(request, None, 302, "Found", Message(), target)

    def test_check_link_uses_get_user_agent_timeout_and_reads_one_byte(self) -> None:
        url = "https://docs.ripe.finance/"
        link = external.ExternalLink(url, ("README.md",))
        response = FakeResponse(200, url)
        opener = mock.Mock()
        opener.open.return_value = response

        result = external.check_link(link, opener, mock.Mock())

        self.assertTrue(result.ok)
        self.assertEqual(200, result.status)
        self.assertEqual(1, response.read_count)
        request = opener.open.call_args.args[0]
        self.assertEqual("GET", request.get_method())
        self.assertEqual(external.USER_AGENT, request.get_header("User-agent"))
        self.assertEqual(
            external.REQUEST_TIMEOUT_SECONDS,
            opener.open.call_args.kwargs["timeout"],
        )

    def test_check_link_retries_transient_failure_then_succeeds(self) -> None:
        url = "https://params.ripe.finance/"
        link = external.ExternalLink(url, ("README.md",))
        transient = HTTPError(url, 503, "Unavailable", Message(), io.BytesIO())
        opener = mock.Mock()
        opener.open.side_effect = [transient, FakeResponse(200, url)]
        sleeper = mock.Mock()

        result = external.check_link(link, opener, sleeper)

        self.assertTrue(result.ok)
        self.assertEqual(2, result.attempts)
        sleeper.assert_called_once_with(external.RETRY_DELAYS_SECONDS[0])

    def test_check_link_does_not_retry_permanent_or_out_of_scope_failure(self) -> None:
        url = "https://docs.ripe.finance/missing"
        link = external.ExternalLink(url, ("README.md",))
        opener = mock.Mock()
        opener.open.side_effect = HTTPError(
            url, 404, "Not Found", Message(), io.BytesIO()
        )
        sleeper = mock.Mock()

        result = external.check_link(link, opener, sleeper)

        self.assertFalse(result.ok)
        self.assertEqual(1, result.attempts)
        sleeper.assert_not_called()

        opener.reset_mock()
        unsafe = external.check_link(
            external.ExternalLink("https://evil.example/", ("README.md",)),
            opener,
            sleeper,
        )
        self.assertFalse(unsafe.ok)
        self.assertEqual(0, unsafe.attempts)
        opener.open.assert_not_called()

    def test_network_errors_have_bounded_retries(self) -> None:
        url = "https://docs.ripe.finance/"
        link = external.ExternalLink(url, ("README.md",))
        opener = mock.Mock()
        opener.open.side_effect = URLError("offline")
        sleeper = mock.Mock()

        result = external.check_link(link, opener, sleeper)

        self.assertFalse(result.ok)
        self.assertEqual(len(external.RETRY_DELAYS_SECONDS) + 1, result.attempts)
        self.assertEqual(len(external.RETRY_DELAYS_SECONDS), sleeper.call_count)

    def test_report_emits_annotations_and_step_summary(self) -> None:
        passed = external.CheckResult(
            external.ExternalLink("https://docs.ripe.finance/", ("README.md",)),
            True,
            1,
            status=200,
        )
        failed = external.CheckResult(
            external.ExternalLink(
                "https://params.ripe.finance/", ("README.md", "SUMMARY.md")
            ),
            False,
            2,
            status=503,
            error="HTTP 503 Unavailable",
        )
        inventory = external.LinkInventory(
            (passed.link, failed.link), ("https://example.test/pinned",)
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as directory:
            summary = Path(directory) / "summary.md"
            with (
                mock.patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}),
                redirect_stdout(stdout),
                redirect_stderr(stderr),
            ):
                status = external.report_results(inventory, (passed, failed), summary)
            rendered_summary = summary.read_text()

        self.assertEqual(1, status)
        self.assertIn(
            "::warning title=External documentation link unavailable::",
            stdout.getvalue(),
        )
        self.assertIn("FAIL https://params.ripe.finance/", stderr.getvalue())
        self.assertIn("1 of 2 checked link(s) failed", rendered_summary)
        self.assertIn("Skipped 1 exact pinned protocol source URL", rendered_summary)


if __name__ == "__main__":
    unittest.main()
