from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import check_markdown as markdown


class MarkdownValidationTests(unittest.TestCase):
    def test_inline_destinations_support_titles_balancing_and_escapes(self) -> None:
        content = r"""
[inline](guide.md "Guide")
[angle](<path with spaces.md> "Title")
[balanced](guide_(v2).md)
[escaped](guide_\(v3\).md)
[escaped-close](guide\).md)
"""
        self.assertEqual(
            markdown.link_targets(content),
            [
                "guide.md",
                "path with spaces.md",
                "guide_(v2).md",
                "guide_(v3).md",
                "guide).md",
            ],
        )

    def test_malformed_inline_destinations_and_escaped_syntax_are_not_links(self) -> None:
        content = r"""
[unbalanced](guide_(v2.md)
[bad-title](guide.md "unterminated)
\[escaped-open](ignored.md)
[escaped-paren]\(ignored-too.md)
"""
        self.assertEqual([], markdown.link_targets(content))

    def test_reference_links_normalize_labels_and_support_shortcuts(self) -> None:
        content = r"""
[reference][docs]
[normalized][ MIXED   label ]
[collapsed][]
[shortcut]
[escaped-label][bracket\]]

[docs]: reference/page.md "Reference"
[mixed   LABEL]: normalized.md
[collapsed]: collapsed.md
[shortcut]: shortcut.md
[bracket\]]: escaped.md
"""
        self.assertEqual(
            markdown.link_targets(content),
            [
                "reference/page.md",
                "normalized.md",
                "collapsed.md",
                "shortcut.md",
                "escaped.md",
            ],
        )
        self.assertEqual([], markdown.undefined_reference_labels(content))

    def test_undefined_explicit_references_are_reported_but_shortcut_text_is_not(self) -> None:
        content = (
            "[missing][docs]\n[also-missing][]\n"
            "[ordinary bracketed text]\n"
            "`position[user][asset]`\n"
            "```text\nnot[a][link]\n```\n"
        )
        self.assertEqual(
            ["also-missing", "docs"],
            markdown.undefined_reference_labels(content),
        )

    def test_multibacktick_and_multiline_code_spans_mask_links(self) -> None:
        content = """
``code with `embedded` ticks
[hidden][docs]
and [hidden-inline](hidden.md)``
[visible][docs]

[docs]: visible.md
"""
        self.assertEqual(["visible.md"], markdown.link_targets(content))
        self.assertEqual([], markdown.undefined_reference_labels(content))

    def test_unclosed_or_escaped_backticks_remain_markdown_prose(self) -> None:
        content = "\\`[escaped](two.md)\n`[unclosed](one.md)\n"
        self.assertEqual(["two.md", "one.md"], markdown.link_targets(content))

    def test_fences_allow_zero_to_three_spaces_and_valid_longer_closers(self) -> None:
        content = "   ```python\n[hidden](missing.md)\n  ````   \n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "page.md"
            path.write_text(content)
            errors: list[str] = []
            with mock.patch.object(markdown, "ROOT", root):
                markdown.check_fences(path, errors)
            self.assertEqual([], errors)
        self.assertEqual([], markdown.link_targets(content))

    def test_four_space_indentation_is_not_a_fence(self) -> None:
        content = "    ```python\n[visible](page.md)\n    ```\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "page.md"
            path.write_text(content)
            errors: list[str] = []
            with mock.patch.object(markdown, "ROOT", root):
                markdown.check_fences(path, errors)
            self.assertEqual([], errors)
        self.assertEqual(["page.md"], markdown.link_targets(content))

    def test_fence_closer_rejects_trailing_content(self) -> None:
        content = "```text\ncontent\n``` not-a-closer\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "page.md"
            path.write_text(content)
            errors: list[str] = []
            with mock.patch.object(markdown, "ROOT", root):
                markdown.check_fences(path, errors)
            self.assertEqual(["page.md:1: unclosed ``` fence"], errors)

    def test_backtick_fence_info_cannot_contain_backticks(self) -> None:
        content = "```language `invalid`\n[visible](page.md)\n"
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            path = root / "page.md"
            path.write_text(content)
            errors: list[str] = []
            with mock.patch.object(markdown, "ROOT", root):
                markdown.check_fences(path, errors)
            self.assertEqual([], errors)
        self.assertEqual(["page.md"], markdown.link_targets(content))

    def test_unpublished_patterns_are_root_relative_and_recursive_only_with_globstar(
        self,
    ) -> None:
        patterns = ("CONTRIBUTING.md", "reference/*.md", ".github/**", "**/draft.md")
        self.assertTrue(markdown.is_unpublished(markdown.ROOT / "CONTRIBUTING.md", patterns))
        self.assertFalse(
            markdown.is_unpublished(
                markdown.ROOT / "nested" / "CONTRIBUTING.md", patterns
            )
        )
        self.assertTrue(
            markdown.is_unpublished(
                markdown.ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md", patterns
            )
        )
        self.assertTrue(
            markdown.is_unpublished(markdown.ROOT / "reference" / "Guide.md", patterns)
        )
        self.assertFalse(
            markdown.is_unpublished(
                markdown.ROOT / "reference" / "nested" / "Guide.md", patterns
            )
        )
        self.assertTrue(
            markdown.is_unpublished(markdown.ROOT / "nested" / "draft.md", patterns)
        )
        self.assertFalse(markdown.is_unpublished(markdown.ROOT / "README.md", patterns))

    def test_navigation_gate_ignores_only_configured_pages(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / ".github").mkdir()
            (root / "reference").mkdir()
            (root / "SUMMARY.md").write_text("# Contents\n\n- [Home](README.md)\n")
            (root / "README.md").write_text("# Home\n")
            (root / "missing.md").write_text("# Missing\n")
            (root / "CONTRIBUTING.md").write_text("# Contributing\n")
            (root / ".github" / "PULL_REQUEST_TEMPLATE.md").write_text("# Template\n")
            (root / "reference" / "Maintenance.md").write_text("# Maintenance\n")
            (root / ".markdownignore").write_text(
                "CONTRIBUTING.md\nreference/*.md\n.github/**\n"
            )

            with mock.patch.object(markdown, "ROOT", root), mock.patch.object(
                markdown, "IGNORE_PATH", root / ".markdownignore"
            ):
                output = io.StringIO()
                with redirect_stderr(output), redirect_stdout(output):
                    self.assertEqual(1, markdown.main())
                (root / "SUMMARY.md").write_text(
                    "# Contents\n\n- [Home](README.md)\n- [Missing](missing.md)\n"
                )
                with redirect_stderr(output), redirect_stdout(output):
                    self.assertEqual(0, markdown.main())


if __name__ == "__main__":
    unittest.main()
