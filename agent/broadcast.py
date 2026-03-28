"""
Send a published edition as a newsletter broadcast via Resend.

Usage:
    uv run --with resend,httpx python agent/broadcast.py 001
    uv run --with resend,httpx python agent/broadcast.py 001 --dry-run
"""

import argparse
import os
import re
from pathlib import Path

import httpx
import resend

REPO_ROOT = Path(__file__).parent.parent
EDITIONS_DIR = REPO_ROOT / "src" / "no"
SITE_URL = "https://hallway.aris.pub"
FROM_EMAIL = "hallway@updates.aris.pub"
REPLY_TO = "hello@aris.pub"


def read_edition(number: str) -> dict:
    """Read an edition file and return its metadata and content."""
    padded = number.zfill(3)
    path = EDITIONS_DIR / f"{padded}.md"
    if not path.exists():
        raise FileNotFoundError(f"Edition {padded} not found at {path}")

    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse frontmatter in {path}")

    frontmatter = match.group(1)
    body = match.group(2).strip()

    draft = "draft: true" in frontmatter
    if draft:
        raise ValueError(f"Edition {padded} is still a draft. Remove 'draft: true' before broadcasting.")

    return {
        "number": padded,
        "body": body,
        "url": f"{SITE_URL}/no/{padded}/",
    }


def markdown_to_html(edition: dict) -> str:
    """Convert edition markdown to simple HTML for email."""
    body = edition["body"]
    lines = body.split("\n")
    html_parts = []
    for line in lines:
        if line.startswith("## "):
            html_parts.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("- ["):
            match = re.match(r"- \[(.+?)\]\((.+?)\)(.*)", line)
            if match:
                title, url, rest = match.groups()
                html_parts.append(f'<p><strong><a href="{url}">{title}</a></strong>{rest}</p>')
            else:
                html_parts.append(f"<p>{line[2:]}</p>")
        elif line.strip().startswith("["):
            match = re.match(r"\s*\[(.+?)\]\((.+?)\)(.*)", line)
            if match:
                title, url, rest = match.groups()
                html_parts.append(f'<p><strong><a href="{url}">{title}</a></strong>{rest}</p>')
            else:
                html_parts.append(f"<p>{line.strip()}</p>")
        elif line.strip():
            html_parts.append(f"<p>{line.strip()}</p>")

    content = "\n".join(html_parts)

    return f"""\
<div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; font-size: 16px; line-height: 1.6; color: #0a0a0a;">
  <p style="color: #7a7a7a; font-size: 14px;">The Hallway Track / No. {edition["number"]}</p>
  {content}
  <hr style="border: none; border-top: 1px solid #e8e8e4; margin: 32px 0;">
  <p style="font-size: 13px; color: #7a7a7a;">
    <a href="{edition["url"]}">Read online</a> ·
    Part of <a href="https://aris.pub">The Aris Program</a>
  </p>
</div>"""


def main():
    parser = argparse.ArgumentParser(description="Broadcast a Hallway Track edition")
    parser.add_argument("number", help="Edition number (e.g., 001)")
    parser.add_argument("--dry-run", action="store_true", help="Print email HTML, don't send")
    args = parser.parse_args()

    edition = read_edition(args.number)
    html = markdown_to_html(edition)

    if args.dry_run:
        print(f"Subject: The Hallway Track No. {edition['number']}")
        print(f"From: The Hallway Track <{FROM_EMAIL}>")
        print(f"Reply-To: {REPLY_TO}")
        print(f"\n--- HTML ---\n")
        print(html)
        return

    api_key = os.environ.get("RESEND_API_KEY")
    segment_id = os.environ.get("RESEND_SEGMENT_ID")
    if not api_key:
        print("Error: RESEND_API_KEY not set")
        return
    if not segment_id:
        print("Error: RESEND_SEGMENT_ID not set")
        return

    resend.api_key = api_key

    try:
        result = resend.Broadcasts.create({
            "segment_id": segment_id,
            "from": f"The Hallway Track <{FROM_EMAIL}>",
            "reply_to": REPLY_TO,
            "subject": f"The Hallway Track No. {edition['number']}",
            "html": html,
            "send": True,
        })
        print(f"Broadcast sent: {result}")
    except Exception as e:
        print(f"Error sending broadcast: {e}")


if __name__ == "__main__":
    main()
