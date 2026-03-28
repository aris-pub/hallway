"""
Hallway Track curation agent.

Scans sources for links relevant to the beat (how AI is affecting the practice
of science), generates a draft edition, and emails a notification.

Usage:
    uv run --with anthropic,httpx,resend python agent/curate.py
    uv run --with anthropic,httpx,resend python agent/curate.py --dry-run
"""

import argparse
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
import resend

REPO_ROOT = Path(__file__).parent.parent
SOURCES_FILE = REPO_ROOT / "sources.md"
EDITIONS_DIR = REPO_ROOT / "src" / "no"

BEAT = """\
How AI is affecting the practice of science. Specifically: AI agents for \
literature review, automated research pipelines, multi-agent scientific \
collaboration, infrastructure for AI-assisted research, accountability and \
authorship questions, changes to peer review, shifts in how research is \
produced and evaluated.

Excludes: general AI product news, model benchmarks, frontier lab \
announcements (unless they directly affect research practice), AI hype."""

FROM_EMAIL = "hallway@updates.aris.pub"
REPLY_TO = "hello@aris.pub"


def parse_sources() -> list[dict[str, str]]:
    """Parse sources.md into a list of {name, url, description}."""
    text = SOURCES_FILE.read_text()
    sources = []
    for match in re.finditer(r"\[(.+?)\]\((.+?)\)\s*-\s*(.+)", text):
        sources.append({
            "name": match.group(1),
            "url": match.group(2),
            "description": match.group(3).strip(),
        })
    return sources


def next_edition_number() -> int:
    """Determine the next edition number from existing files."""
    existing = list(EDITIONS_DIR.glob("*.md"))
    if not existing:
        return 1
    numbers = []
    for f in existing:
        try:
            numbers.append(int(f.stem))
        except ValueError:
            continue
    return max(numbers) + 1 if numbers else 1


def next_publish_date() -> str:
    """Next Monday from today, as YYYY-MM-DD."""
    today = datetime.now()
    days_ahead = (7 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


def scan_and_curate(sources: list[dict[str, str]]) -> str:
    """Use Claude with web search to find and curate links."""
    client = anthropic.Anthropic()

    source_list = "\n".join(
        f"- {s['name']}: {s['url']} ({s['description']})"
        for s in sources
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        tools=[{"type": "web_search_20250305"}],
        messages=[{
            "role": "user",
            "content": f"""\
You are a research assistant for The Hallway Track, a weekly curated link \
roundup on how AI is affecting the practice of science.

THE BEAT:
{BEAT}

SOURCES TO CHECK (search these and beyond):
{source_list}

YOUR TASK:
Search for notable developments from the past 7 days that fit the beat. \
For each item found, provide:
1. The article/post title (as a link in markdown)
2. A one-sentence framing: why a working researcher should care. Be direct \
and opinionated. No hype.

Group items under 2-4 section headings (e.g., "Tools & Infrastructure", \
"Papers & Methods", "Policy & Practice"). Use ## for headings.

Format each item as a markdown list item with the link as the text, followed \
by a paragraph with the one-line framing. Like this:

- [Title of the article](https://example.com)
  One sentence about why this matters to a working researcher.

Aim for 5-10 items total. Quality over quantity. If something is not clearly \
relevant to the beat, leave it out.""",
        }],
    )

    text_parts = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)
    return "\n".join(text_parts)


def write_edition(number: int, date: str, content: str) -> Path:
    """Write a draft edition markdown file."""
    padded = str(number).zfill(3)
    path = EDITIONS_DIR / f"{padded}.md"

    frontmatter = f"""\
---
number: {number}
date: {date}
pageTitle: "No. {padded}"
description: "The Hallway Track No. {padded} - How AI is affecting the practice of science"
draft: true
---

"""
    path.write_text(frontmatter + content + "\n")
    return path


def send_notification(number: int, file_path: Path, admin_email: str) -> None:
    """Send email notification that a draft is ready for review."""
    padded = str(number).zfill(3)

    resend.Emails.send({
        "from": f"The Hallway Track <{FROM_EMAIL}>",
        "to": [admin_email],
        "reply_to": REPLY_TO,
        "subject": f"Draft ready: No. {padded}",
        "text": (
            f"A new draft edition (No. {padded}) has been generated.\n\n"
            f"File: {file_path}\n\n"
            f"Review the draft, edit as needed, remove the 'draft: true' "
            f"frontmatter field, and publish."
        ),
    })


def main():
    parser = argparse.ArgumentParser(description="Hallway Track curation agent")
    parser.add_argument("--dry-run", action="store_true", help="Print draft to stdout, skip email")
    args = parser.parse_args()

    sources = parse_sources()
    number = next_edition_number()
    date = next_publish_date()

    print(f"Scanning sources for edition No. {str(number).zfill(3)}...")
    content = scan_and_curate(sources)

    path = write_edition(number, date, content)
    print(f"Draft written to {path}")

    if args.dry_run:
        print("\n--- DRAFT ---\n")
        print(path.read_text())
    else:
        api_key = os.environ.get("RESEND_API_KEY")
        admin_email = os.environ.get("ADMIN_EMAIL", "hello@aris.pub")
        if not api_key:
            print("Warning: RESEND_API_KEY not set, skipping email notification")
            return
        resend.api_key = api_key
        send_notification(number, path, admin_email)
        print(f"Notification sent to {admin_email}")


if __name__ == "__main__":
    main()
