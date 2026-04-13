"""
Post a Hallway Track edition to Bluesky.

Usage:
    uv run --with httpx python agent/post_bsky.py 003 "Post text here"
    uv run --with httpx python agent/post_bsky.py 003 "Post text here" --at "14:00"
"""

import argparse
import json
import os
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


def create_post(token: str, did: str, text: str, number: str) -> dict:
    """Create a Bluesky post with a link card embed."""
    padded = number.zfill(3)
    url = f"{SITE_URL}/no/{padded}/"
    image_path = IMAGES_DIR / f"{padded}.png"

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

    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "embed": embed,
    }

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
    parser.add_argument("text", help="Post text")
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

    print(f"Posting edition {args.number}...")
    result = create_post(token, did, args.text, args.number)
    print(f"Posted: {result['uri']}")


if __name__ == "__main__":
    main()
