"""Tests for the curation agent's deterministic functions."""

import subprocess
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from curate import (
    BSKY_MAX_CHARS,
    extract_bsky_text,
    extract_urls,
    get_previous_urls,
    next_edition_number,
    next_publish_date,
    parse_sources,
    preflight_claude,
    send_failure_notification,
    verify_links,
    write_edition,
    MIN_CONTENT_LENGTH,
)


@pytest.fixture
def editions_dir(tmp_path):
    """Temporary editions directory."""
    d = tmp_path / "no"
    d.mkdir()
    with patch("curate.EDITIONS_DIR", d):
        yield d


@pytest.fixture
def sources_file(tmp_path):
    """Temporary sources file."""
    f = tmp_path / "sources.md"
    f.write_text(
        "# Sources\n\n"
        "## Section\n\n"
        "- [One Useful Thing](https://www.oneusefulthing.org/) - Ethan Mollick, AI in academic work\n"
        "- [AI Snake Oil](https://aisnakeoil.substack.com/) - Narayanan & Kapoor, AI claims vs reality\n"
        "- [Elicit Blog](https://elicit.com/blog) - AI-assisted literature review tooling\n"
    )
    with patch("curate.SOURCES_FILE", f):
        yield f


class TestParseSources:
    def test_parses_all_entries(self, sources_file):
        sources = parse_sources()
        assert len(sources) == 3

    def test_extracts_name(self, sources_file):
        sources = parse_sources()
        assert sources[0]["name"] == "One Useful Thing"
        assert sources[1]["name"] == "AI Snake Oil"

    def test_extracts_url(self, sources_file):
        sources = parse_sources()
        assert sources[0]["url"] == "https://www.oneusefulthing.org/"
        assert sources[2]["url"] == "https://elicit.com/blog"

    def test_extracts_description(self, sources_file):
        sources = parse_sources()
        assert sources[0]["description"] == "Ethan Mollick, AI in academic work"

    def test_empty_file(self, tmp_path):
        f = tmp_path / "sources.md"
        f.write_text("# Sources\n\nNothing here yet.\n")
        with patch("curate.SOURCES_FILE", f):
            assert parse_sources() == []

    def test_real_sources_file(self):
        """Verify the actual sources.md in the repo parses correctly."""
        sources = parse_sources()
        assert len(sources) >= 10
        for s in sources:
            assert s["name"]
            assert s["url"].startswith("https://")
            assert s["description"]


class TestNextEditionNumber:
    def test_empty_directory(self, editions_dir):
        assert next_edition_number() == 1

    def test_sequential(self, editions_dir):
        (editions_dir / "001.md").write_text("---\n---\n")
        (editions_dir / "002.md").write_text("---\n---\n")
        (editions_dir / "003.md").write_text("---\n---\n")
        assert next_edition_number() == 4

    def test_with_gaps(self, editions_dir):
        (editions_dir / "001.md").write_text("---\n---\n")
        (editions_dir / "005.md").write_text("---\n---\n")
        assert next_edition_number() == 6

    def test_ignores_non_numeric_files(self, editions_dir):
        (editions_dir / "001.md").write_text("---\n---\n")
        (editions_dir / "no.json").write_text("{}")
        assert next_edition_number() == 2

    def test_single_edition(self, editions_dir):
        (editions_dir / "001.md").write_text("---\n---\n")
        assert next_edition_number() == 2


class TestNextPublishDate:
    @patch("curate.datetime")
    def test_returns_next_monday(self, mock_dt):
        # Wednesday March 25, 2026
        mock_dt.now.return_value = datetime(2026, 3, 25)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = next_publish_date()
        assert result == "2026-03-30"  # next Monday

    @patch("curate.datetime")
    def test_monday_returns_following_monday(self, mock_dt):
        # Monday March 30, 2026
        mock_dt.now.return_value = datetime(2026, 3, 30)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = next_publish_date()
        assert result == "2026-04-06"  # following Monday

    @patch("curate.datetime")
    def test_sunday_returns_next_day(self, mock_dt):
        # Sunday March 29, 2026
        mock_dt.now.return_value = datetime(2026, 3, 29)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = next_publish_date()
        assert result == "2026-03-30"  # next day is Monday


class TestExtractUrls:
    def test_extracts_markdown_links(self):
        text = "- [Title](https://example.com)\n- [Other](https://other.com/path)"
        assert extract_urls(text) == ["https://example.com", "https://other.com/path"]

    def test_ignores_non_links(self):
        text = "No links here, just text."
        assert extract_urls(text) == []

    def test_ignores_bare_urls(self):
        text = "Visit https://example.com for more."
        assert extract_urls(text) == []

    def test_handles_mixed_content(self):
        text = (
            "## Tools\n\n"
            "- [Tool A](https://a.com) does things\n\n"
            "Some paragraph text.\n\n"
            "- [Tool B](https://b.com) does other things\n"
        )
        assert extract_urls(text) == ["https://a.com", "https://b.com"]


class TestGetPreviousUrls:
    def test_collects_from_recent_editions(self, editions_dir):
        (editions_dir / "001.md").write_text(
            "---\n---\n- [A](https://a.com)\n- [B](https://b.com)\n"
        )
        (editions_dir / "002.md").write_text(
            "---\n---\n- [C](https://c.com)\n"
        )
        urls = get_previous_urls(n=2)
        assert "https://c.com" in urls
        assert "https://a.com" in urls
        assert "https://b.com" in urls

    def test_respects_limit(self, editions_dir):
        (editions_dir / "001.md").write_text("---\n---\n- [Old](https://old.com)\n")
        (editions_dir / "002.md").write_text("---\n---\n- [Mid](https://mid.com)\n")
        (editions_dir / "003.md").write_text("---\n---\n- [New](https://new.com)\n")
        urls = get_previous_urls(n=1)
        assert "https://new.com" in urls
        assert "https://old.com" not in urls

    def test_empty_directory(self, editions_dir):
        assert get_previous_urls() == []

    def test_ignores_non_numeric_files(self, editions_dir):
        (editions_dir / "no.11tydata.js").write_text("module.exports = {};")
        (editions_dir / "001.md").write_text("---\n---\n- [A](https://a.com)\n")
        urls = get_previous_urls()
        assert urls == ["https://a.com"]


class TestVerifyLinks:
    def test_no_broken_links(self):
        content = "- [Example](https://httpbin.org/status/200)"
        assert verify_links(content) == []

    def test_content_with_no_links(self):
        content = "No links here."
        assert verify_links(content) == []


class TestMinContentLength:
    def test_constant_is_reasonable(self):
        assert MIN_CONTENT_LENGTH > 0
        assert MIN_CONTENT_LENGTH <= 500


class TestWriteEdition:
    def test_creates_file(self, editions_dir):
        path = write_edition(4, "2026-04-06", "Some content")
        assert path.exists()
        assert path.name == "004.md"

    def test_frontmatter(self, editions_dir):
        path = write_edition(4, "2026-04-06", "Some content")
        text = path.read_text()
        assert "number: 4" in text
        assert "date: 2026-04-06" in text
        assert 'pageTitle: "No. 004"' in text
        assert "draft: true" in text

    def test_content_after_frontmatter(self, editions_dir):
        path = write_edition(1, "2026-04-06", "## Tools\n\n- A link")
        text = path.read_text()
        parts = text.split("---")
        body = parts[2]
        assert "## Tools" in body
        assert "- A link" in body

    def test_zero_padded_filename(self, editions_dir):
        path = write_edition(12, "2026-04-06", "Content")
        assert path.name == "012.md"

    def test_description_has_no_em_dash(self, editions_dir):
        path = write_edition(1, "2026-04-06", "Content")
        text = path.read_text()
        assert "\u2014" not in text


class TestPreflightClaude:
    @patch("curate.subprocess.run")
    def test_returns_ok_when_claude_succeeds(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="ok\n", stderr="")
        ok, msg = preflight_claude()
        assert ok is True
        assert msg == "ok"

    @patch("curate.subprocess.run")
    def test_returns_failure_on_nonzero_exit(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Failed to authenticate. API Error: 401",
            stderr="",
        )
        ok, msg = preflight_claude()
        assert ok is False
        assert "exited 1" in msg
        assert "401" in msg

    @patch("curate.subprocess.run")
    def test_returns_failure_when_claude_missing(self, mock_run):
        mock_run.side_effect = FileNotFoundError()
        ok, msg = preflight_claude()
        assert ok is False
        assert "not found" in msg.lower()

    @patch("curate.subprocess.run")
    def test_returns_failure_on_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=60)
        ok, msg = preflight_claude()
        assert ok is False
        assert "timed out" in msg.lower()


class TestExtractBskyText:
    def test_returns_text_before_first_separator(self):
        content = "BSky post here.\n---\nLinkedIn post here.\n"
        assert extract_bsky_text(content) == "BSky post here."

    def test_handles_multiline_bsky_section(self):
        content = "Line 1.\nLine 2.\nLine 3.\n---\nLinkedIn.\n"
        assert extract_bsky_text(content) == "Line 1.\nLine 2.\nLine 3."

    def test_strips_surrounding_whitespace(self):
        content = "\n\n  BSky.  \n\n---\nLI.\n"
        assert extract_bsky_text(content) == "BSky."

    def test_no_separator_returns_full_text(self):
        content = "Just one section, no separator."
        assert extract_bsky_text(content) == "Just one section, no separator."

    def test_three_section_post_returns_only_bsky(self):
        """Mirrors a future post.md format with @aris-pub section appended."""
        content = "BSky text.\n---\nLinkedIn text.\n---\n@aris-pub framing.\n"
        assert extract_bsky_text(content) == "BSky text."

    def test_real_edition_007_post_under_limit(self):
        """Edition 007's BSky text was within the limit. Regression guard."""
        content = (
            "1 in 277 biomedical papers now contains fabricated citations, up 12x since 2023. "
            "A Lancet audit of 97 million references traced the sharpest rise to the adoption "
            "of AI writing tools. This week's edition covers what that means alongside "
            "zero-click readership and vibe physics. hallway.aris.pub/no/007/\n"
            "---\nLI text\n"
        )
        bsky = extract_bsky_text(content)
        assert len(bsky) <= BSKY_MAX_CHARS

    def test_edition_008_actual_text_exceeds_limit(self):
        """Edition 008's BSky text was 308 chars and caused a 400 from the BSky API."""
        content = (
            "Google's AI co-mathematician helped an Oxford researcher close a 60-year-old "
            "open problem from the Kourovka Notebook. The system's trick: maintaining state "
            "across a full research session, not just answering one-shot questions. Plus: "
            "$172M in new open infrastructure for academic AI.\n\nhallway.aris.pub/no/008/\n"
            "---\nLI text\n"
        )
        bsky = extract_bsky_text(content)
        assert len(bsky) > BSKY_MAX_CHARS


class TestSendFailureNotification:
    @patch("curate.resend.Emails.send")
    def test_includes_edition_label(self, mock_send):
        send_failure_notification("boom", 7, "test@example.com")
        payload = mock_send.call_args[0][0]
        assert "No. 007" in payload["subject"]
        assert "No. 007" in payload["text"]
        assert "boom" in payload["text"]
        assert payload["to"] == ["test@example.com"]

    @patch("curate.resend.Emails.send")
    def test_handles_unknown_edition(self, mock_send):
        send_failure_notification("preflight failed", None, "test@example.com")
        payload = mock_send.call_args[0][0]
        assert "unknown" in payload["subject"].lower() or "unknown" in payload["text"].lower()

    @patch("curate.resend.Emails.send")
    def test_swallows_email_errors(self, mock_send, capsys):
        mock_send.side_effect = RuntimeError("resend down")
        # Must not raise
        send_failure_notification("boom", 7, "test@example.com")
        captured = capsys.readouterr()
        assert "resend down" in captured.out
