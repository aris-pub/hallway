"""
Hallway Track curation agent.

Tells Claude Code to scan sources, curate links, and write a draft
edition file directly to disk.

Usage:
    uv run --with httpx,resend python agent/curate.py
    uv run --with httpx,resend python agent/curate.py --dry-run
"""

import argparse
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import httpx
import resend

REPO_ROOT = Path(__file__).parent.parent
AGENT_DIR = Path(__file__).parent
SOURCES_FILE = REPO_ROOT / "sources.md"
EDITIONS_DIR = REPO_ROOT / "src" / "no"
TEMPLATE_FILE = AGENT_DIR / "edition-template.md"
PROMPT_FILE = AGENT_DIR / "prompt.txt"
MIN_CONTENT_LENGTH = 100
DEDUP_EDITIONS = 3

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


def extract_urls(text: str) -> list[str]:
    """Extract markdown link URLs from text."""
    return re.findall(r"\[.+?\]\((https?://[^\)]+)\)", text)


def get_previous_urls(n: int = DEDUP_EDITIONS) -> list[str]:
    """Collect URLs from the most recent n editions for deduplication."""
    files = sorted(EDITIONS_DIR.glob("*.md"), reverse=True)
    urls = []
    count = 0
    for f in files:
        try:
            int(f.stem)
        except ValueError:
            continue
        urls.extend(extract_urls(f.read_text()))
        count += 1
        if count >= n:
            break
    return urls


def verify_links(content: str) -> list[str]:
    """Check that URLs in the curated content actually resolve. Returns list of broken URLs."""
    urls = extract_urls(content)
    broken = []
    with httpx.Client(timeout=10, follow_redirects=True) as client:
        for url in urls:
            try:
                resp = client.head(url)
                if resp.status_code >= 400:
                    broken.append(f"  {resp.status_code}: {url}")
            except httpx.RequestError:
                broken.append(f"  UNREACHABLE: {url}")
    return broken


def build_prompt(sources: list[dict[str, str]], number: int, date: str,
                 output_path: Path, previous_urls: list[str] | None = None) -> str:
    """Build the prompt that tells Claude Code to write the edition file."""
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    padded = str(number).zfill(3)

    source_list = "\n".join(
        f"- {s['name']}: {s['url']} ({s['description']})"
        for s in sources
    )

    template = TEMPLATE_FILE.read_text()

    dedup_block = ""
    if previous_urls:
        url_list = "\n".join(f"- {u}" for u in previous_urls)
        dedup_block = f"""
ALREADY COVERED (do not include these URLs or stories about the same topic):
{url_list}
"""

    prompt_template = PROMPT_FILE.read_text()
    return prompt_template.format(
        padded=padded,
        week_ago=week_ago,
        today=today,
        output_path=output_path,
        template=template,
        number=number,
        date=date,
        beat=BEAT,
        source_list=source_list,
        dedup_block=dedup_block,
    )


def run_claude(prompt: str) -> tuple[int, str]:
    """Run Claude Code with the given prompt. Returns (exit_code, output)."""
    result = subprocess.run(
        ["claude", "-p", prompt, "--allowedTools", "WebSearch,WebFetch,Write,Read"],
        capture_output=True,
        text=True,
        timeout=600,
    )
    return result.returncode, result.stdout.strip()


def write_edition(number: int, date: str, content: str) -> Path:
    """Write a draft edition markdown file (fallback if Claude doesn't write it)."""
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
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without scanning or writing anything")
    args = parser.parse_args()

    sources = parse_sources()
    if not sources:
        print("Error: No sources found in sources.md. Aborting.")
        return

    number = next_edition_number()
    date = next_publish_date()
    padded = str(number).zfill(3)
    output_path = EDITIONS_DIR / f"{padded}.md"
    previous_urls = get_previous_urls()

    if args.dry_run:
        print(f"Would scan {len(sources)} sources")
        print(f"Would write edition No. {padded} to {output_path}")
        print(f"Publish date: {date}")
        if previous_urls:
            print(f"Would exclude {len(previous_urls)} URLs from recent editions")
        return

    if previous_urls:
        print(f"Dedup: excluding {len(previous_urls)} URLs from recent editions")

    print(f"Scanning sources for edition No. {padded}...")
    prompt = build_prompt(sources, number, date, output_path, previous_urls)

    try:
        exit_code, output = run_claude(prompt)
    except subprocess.TimeoutExpired:
        print("Error: Claude Code timed out after 10 minutes.")
        return

    print(f"Claude: {output}")

    if exit_code != 0:
        print(f"Error: Claude Code exited with code {exit_code}")
        return

    if not output_path.exists():
        print(f"Error: Expected file {output_path} was not created.")
        return

    content = output_path.read_text()
    if len(content.strip()) < MIN_CONTENT_LENGTH:
        print(f"Error: Edition file is too short ({len(content.strip())} chars). Review manually.")
        return

    broken = verify_links(content)
    if broken:
        print(f"Warning: {len(broken)} broken link(s) found:")
        for b in broken:
            print(b)

    print(f"Draft written to {output_path}")

    # Commit and push draft so it can be reviewed from any machine
    subprocess.run(["git", "add", str(output_path)], cwd=REPO_ROOT)
    subprocess.run(
        ["git", "commit", "-m", f"Draft: No. {padded}"],
        cwd=REPO_ROOT,
    )
    subprocess.run(["git", "push"], cwd=REPO_ROOT)
    print("Draft committed and pushed")

    api_key = os.environ.get("RESEND_API_KEY")
    admin_email = os.environ.get("ADMIN_EMAIL", "hello@aris.pub")
    if not api_key:
        print("Warning: RESEND_API_KEY not set, skipping email notification")
        return
    resend.api_key = api_key
    send_notification(number, output_path, admin_email)
    print(f"Notification sent to {admin_email}")


if __name__ == "__main__":
    main()
