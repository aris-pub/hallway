"""
Send a published edition as a newsletter broadcast via Resend.

Usage:
    uv run --with resend,httpx python agent/broadcast.py 001
    uv run --with resend,httpx python agent/broadcast.py 001 --dry-run
"""

import argparse
import os
import re
import sys
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

    lead_match = re.search(r"^lead:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    lead_url = lead_match.group(1) if lead_match else None

    date_match = re.search(r"^date:\s*(\S+)\s*$", frontmatter, re.MULTILINE)
    date_str = date_match.group(1) if date_match else None

    return {
        "number": padded,
        "body": body,
        "url": f"{SITE_URL}/no/{padded}/",
        "lead": lead_url,
        "date": date_str,
    }


def normalize_url(url: str) -> str:
    """Normalize URL for comparison: strip trailing slash and utm_* params."""
    url = url.strip()
    url = re.sub(r"[?&]utm_[^&]*", "", url)
    url = url.rstrip("?&")
    url = url.rstrip("/")
    return url


def parse_blocks(body: str):
    """Parse edition body into (synthesis_paragraphs, sections)."""
    paragraphs = []
    current = []
    for line in body.split("\n"):
        if line.strip() == "":
            if current:
                paragraphs.append(" ".join(current))
                current = []
        else:
            current.append(line.strip())
    if current:
        paragraphs.append(" ".join(current))

    synthesis = []
    sections = []
    current_section = None
    current_item = None
    in_synthesis = True

    def flush_item():
        nonlocal current_item
        if current_item and current_section is not None:
            current_section["items"].append(current_item)
        current_item = None

    for para in paragraphs:
        if para.startswith("## "):
            flush_item()
            in_synthesis = False
            current_section = {"name": para[3:], "items": []}
            sections.append(current_section)
        elif para.startswith("- ["):
            flush_item()
            match = re.match(r"- \[(.+?)\]\((.+?)\)(.*)", para)
            if match:
                title, url, rest = match.groups()
                current_item = {"title": title, "url": url, "source": "", "description": "", "rest_inline": rest.strip()}
        elif current_item is not None:
            stripped = para.strip()
            if not current_item["source"] and stripped.startswith("*") and stripped.endswith("*"):
                current_item["source"] = stripped.strip("*").strip()
            elif not current_item["description"]:
                current_item["description"] = stripped
            else:
                current_item["description"] += " " + stripped
        elif in_synthesis:
            synthesis.append(para)

    flush_item()
    return synthesis, sections


def format_date(date_str: str) -> str:
    """Convert YYYY-MM-DD to 'MONTH D YYYY' uppercase, no comma."""
    if not date_str:
        return ""
    months = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
              "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]
    try:
        y, m, d = date_str.split("-")
        return f"{months[int(m) - 1]} {int(d)} {y}"
    except (ValueError, IndexError):
        return date_str.upper()


def inline_markdown_to_html(text: str) -> str:
    """Convert inline [text](url) markdown into HTML anchors. Body-text use only."""
    return re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{m.group(2)}" style="color: #157067;">{m.group(1)}</a>',
        text,
    )


def render_item(item: dict, title_size: int = 18) -> str:
    """Render a single item (non-lead) as HTML paragraphs."""
    parts = [
        f'<p style="margin: 0 0 4px 0; font-size: {title_size}px; font-weight: 700; line-height: 1.3;">'
        f'<a href="{item["url"]}" style="color: #111; text-decoration: none;">{item["title"]}</a></p>'
    ]
    if item["source"]:
        parts.append(
            f'<p style="margin: 0 0 8px 0; font-size: 12px; color: #6b6b6b;">{item["source"]}</p>'
        )
    if item["description"]:
        parts.append(
            f'<p style="margin: 0; font-size: 14px; color: #4a4a4a; line-height: 1.5;">{inline_markdown_to_html(item["description"])}</p>'
        )
    return "\n".join(parts)


def render_lead(item: dict) -> str:
    """Render the lead item with bold left bar and tinted background."""
    inner_parts = [
        f'<p style="margin: 0 0 8px 0; font-size: 11px; letter-spacing: 0.1em; '
        f'text-transform: uppercase; color: #157067; font-weight: 600;">This Week</p>',
        f'<p style="margin: 0 0 6px 0; font-size: 22px; font-weight: 700; line-height: 1.25; color: #111;">'
        f'<a href="{item["url"]}" style="color: #111; text-decoration: none;">{item["title"]}</a></p>'
    ]
    if item["source"]:
        inner_parts.append(
            f'<p style="margin: 0 0 10px 0; font-size: 12px; color: #6b6b6b;">{item["source"]}</p>'
        )
    if item["description"]:
        inner_parts.append(
            f'<p style="margin: 0; font-size: 14px; color: #4a4a4a; line-height: 1.5;">{inline_markdown_to_html(item["description"])}</p>'
        )
    inner = "\n".join(inner_parts)
    return (
        f'<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="margin: 32px 0;">'
        f'<tr><td style="border-left: 5px solid #157067; background: #ecf4f0; padding: 20px 22px; border-radius: 4px;">{inner}</td></tr>'
        f'</table>'
    )


def markdown_to_html(edition: dict) -> str:
    """Render edition as HTML for the email broadcast."""
    synthesis, sections = parse_blocks(edition["body"])

    lead_url_norm = normalize_url(edition["lead"]) if edition["lead"] else None
    lead_item = None
    if lead_url_norm:
        for section in sections:
            for item in section["items"]:
                if normalize_url(item["url"]) == lead_url_norm:
                    lead_item = item
                    section["items"].remove(item)
                    break
            if lead_item:
                break

    header_date = format_date(edition["date"])
    header_html = (
        f'<p style="margin: 0 0 4px 0; font-size: 12px; letter-spacing: 0.08em; '
        f'text-transform: uppercase; color: #6b6b6b;">'
        f'THE HALLWAY TRACK&nbsp;&nbsp;&nbsp;NO. {edition["number"]}'
        f'</p>'
    )
    if header_date:
        header_html += (
            f'<p style="margin: 0; font-size: 12px; letter-spacing: 0.08em; '
            f'text-transform: uppercase; color: #6b6b6b;">{header_date}</p>'
        )

    synthesis_html = ""
    if synthesis:
        parts = [
            f'<p style="margin: 0 0 16px 0; font-size: 16px; color: #111; line-height: 1.6;">{inline_markdown_to_html(p)}</p>'
            for p in synthesis
        ]
        synthesis_html = "\n".join(parts)

    rule = '<hr style="border: none; border-top: 1px solid #e5e5e5; margin: 32px 0;">'

    lead_html = render_lead(lead_item) if lead_item else ""

    sections_html_parts = []
    first_section = True
    for section in sections:
        if not section["items"]:
            continue
        section_header = (
            f'<p style="margin: 0 0 16px 0; font-size: 11px; letter-spacing: 0.1em; '
            f'text-transform: uppercase; color: #6b6b6b; font-weight: 600;">{section["name"]}</p>'
        )
        items_html = '<div style="margin-bottom: 24px;"></div>'.join(render_item(item) for item in section["items"])
        prefix = "" if first_section else rule
        sections_html_parts.append(prefix + section_header + items_html)
        first_section = False
    sections_html = "\n".join(sections_html_parts)

    footer_html = (
        f'<p style="margin: 0; font-size: 12px; color: #6b6b6b; text-align: center;">'
        f'<a href="{edition["url"]}" style="color: #6b6b6b; text-decoration: underline;">Read online</a>'
        f'&nbsp;&middot;&nbsp;'
        f'<a href="{{{{{{RESEND_UNSUBSCRIBE_URL}}}}}}" style="color: #6b6b6b; text-decoration: underline;">Unsubscribe</a>'
        f'&nbsp;&middot;&nbsp;'
        f'Part of <a href="https://aris.pub" style="color: #6b6b6b; text-decoration: underline;">The Aris Program</a>'
        f'</p>'
    )

    return f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background: #ffffff;">
<table cellpadding="0" cellspacing="0" border="0" width="100%" role="presentation" style="background: #ffffff;">
<tr><td align="center" style="padding: 32px 16px;">
<table cellpadding="0" cellspacing="0" border="0" width="600" role="presentation" style="max-width: 600px; width: 100%;">
<tr><td style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #111;">
{header_html}
<div style="height: 32px;"></div>
{synthesis_html}
{lead_html}
{sections_html}
<hr style="border: none; border-top: 1px solid #e5e5e5; margin: 32px 0;">
{footer_html}
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""


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
        sys.exit("Error: RESEND_API_KEY not set")
    if not segment_id:
        sys.exit("Error: RESEND_SEGMENT_ID not set")

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
