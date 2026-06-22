"""
Post a Hallway Track edition to Bluesky.

Usage:
    uv run --with httpx python agent/post_bsky.py 003 "Post text here"
    uv run --with httpx python agent/post_bsky.py 003 "Post text here" --at "14:00"

Multi-paragraph text (paragraphs separated by blank lines) posts as a thread:
the first paragraph becomes the root post with the edition's link-card embed,
each subsequent paragraph posts as a reply. `@handle.tld` mentions in any
paragraph are resolved to DIDs and rendered as real BSky tags.
"""

import argparse
import os
import re
import time
from datetime import datetime
from pathlib import Path

import httpx

REPO_ROOT = Path(__file__).parent.parent
IMAGES_DIR = REPO_ROOT / "src" / "images" / "og"
SITE_URL = "https://hallway.aris.pub"
PDS_HOST = "https://bsky.social"


def login(handle: str, password: str) -> tuple[str, str]:
    """Authenticate and return (access_token, did)."""
    resp = httpx.post(f"{PDS_HOST}/xrpc/com.atproto.server.createSession", json={
        "identifier": handle,
        "password": password,
    })
    resp.raise_for_status()
    data = resp.json()
    return data["accessJwt"], data["did"]


def upload_image(token: str, image_path: Path) -> dict:
    """Upload an image blob and return the blob reference."""
    with open(image_path, "rb") as f:
        image_data = f.read()
    resp = httpx.post(
        f"{PDS_HOST}/xrpc/com.atproto.repo.uploadBlob",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "image/png",
        },
        content=image_data,
    )
    resp.raise_for_status()
    return resp.json()["blob"]


def resolve_handle(handle: str) -> str:
    """Resolve a Bluesky handle to its DID for tagging mentions."""
    resp = httpx.get(
        "https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle",
        params={"handle": handle},
    )
    resp.raise_for_status()
    return resp.json()["did"]


def build_facets(text: str) -> list[dict]:
    """Build rich-text facets for @mentions in the post text."""
    facets = []
    for m in re.finditer(r"@([a-zA-Z0-9_.-]+\.[a-zA-Z0-9_.-]+)", text):
        handle = m.group(1)
        try:
            did = resolve_handle(handle)
        except Exception:
            continue
        byte_start = len(text[: m.start()].encode("utf-8"))
        byte_end = len(text[: m.end()].encode("utf-8"))
        facets.append({
            "index": {"byteStart": byte_start, "byteEnd": byte_end},
            "features": [{"$type": "app.bsky.richtext.facet#mention", "did": did}],
        })
    return facets


def create_post(token: str, did: str, text: str, number: str, reply_to: dict | None = None) -> dict:
    """Create a Bluesky post. Root post gets the link-card embed; replies don't."""
    padded = number.zfill(3)
    image_path = IMAGES_DIR / f"{padded}.png"

    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
    }
    facets = build_facets(text)
    if facets:
        record["facets"] = facets

    if reply_to is None:
        url = f"{SITE_URL}/no/{padded}/"
        embed = {
            "$type": "app.bsky.embed.external",
            "external": {
                "uri": url,
                "title": f"No. {padded} - The Hallway Track",
                "description": "How AI is affecting the practice of science.",
            },
        }
        if image_path.exists():
            blob = upload_image(token, image_path)
            embed["external"]["thumb"] = blob
        record["embed"] = embed
    else:
        record["reply"] = {"root": reply_to["root"], "parent": reply_to["parent"]}

    resp = httpx.post(
        f"{PDS_HOST}/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": record,
        },
    )
    resp.raise_for_status()
    return resp.json()


def wait_until(target_time: str):
    """Wait until HH:MM today."""
    now = datetime.now()
    hour, minute = map(int, target_time.split(":"))
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        print(f"Target time {target_time} already passed. Posting now.")
        return
    wait_seconds = (target - now).total_seconds()
    print(f"Waiting until {target_time} ({int(wait_seconds)}s)...")
    time.sleep(wait_seconds)


def main():
    parser = argparse.ArgumentParser(description="Post edition to Bluesky")
    parser.add_argument("number", help="Edition number (e.g., 003)")
    parser.add_argument("text", help="Post text. Blank-line-separated paragraphs post as a thread.")
    parser.add_argument("--at", help="Wait until HH:MM to post (e.g., 14:00)")
    args = parser.parse_args()

    handle = os.environ.get("BSKY_HANDLE")
    password = os.environ.get("BSKY_PASSWORD")
    if not handle or not password:
        print("Error: BSKY_HANDLE and BSKY_PASSWORD must be set")
        return

    if args.at:
        wait_until(args.at)

    print(f"Logging in as {handle}...")
    token, did = login(handle, password)

    paragraphs = [p.strip() for p in args.text.split("\n\n") if p.strip()]

    print(f"Posting edition {args.number} ({len(paragraphs)} post{'s' if len(paragraphs) > 1 else ''})...")
    first = create_post(token, did, paragraphs[0], args.number)
    print(f"Posted: {first['uri']}")
    root_ref = {"uri": first["uri"], "cid": first["cid"]}
    parent_ref = root_ref

    for i, paragraph in enumerate(paragraphs[1:], start=2):
        print(f"Posting reply {i}/{len(paragraphs)}...")
        reply = create_post(
            token, did, paragraph, args.number,
            reply_to={"root": root_ref, "parent": parent_ref},
        )
        print(f"Posted: {reply['uri']}")
        parent_ref = {"uri": reply["uri"], "cid": reply["cid"]}


if __name__ == "__main__":
    main()
