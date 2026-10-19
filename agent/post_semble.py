"""
Post a published Hallway Track edition to Semble as one card.

For each edition we write a single network.cosmik.card (a URL card) to the
dedicated Hallway Track atproto account. The card points at the edition
permalink and carries the edition title and the editorial synthesis paragraph.
Semble picks the record up from the atproto firehose, so there is no Semble-side
registration step: whatever the account writes to network.cosmik.* shows up on
Semble. The record shape matches the card Semble itself writes for a hand pull.

Usage:
    uv run python agent/post_semble.py 030
    uv run python agent/post_semble.py 030 --dry-run

Environment:
    HT_ATPROTO_HANDLE    the dedicated Hallway Track atproto handle
    HT_ATPROTO_PASSWORD  an app password for that account
"""

import argparse
import hashlib
import json
import os
import re
from datetime import datetime

import httpx

from broadcast import SITE_URL, parse_blocks, read_edition
from post_bsky import PDS_HOST, login

CARD_COLLECTION = "network.cosmik.card"
SITE_NAME = "The Hallway Track"

# base32-sortable alphabet used by atproto TIDs
_S32 = "234567abcdefghijklmnopqrstuvwxyz"


def _s32encode(value: int) -> str:
    out = ""
    for _ in range(13):
        out = _S32[value & 31] + out
        value >>= 5
    return out


def edition_datetime(date_str) -> datetime:
    """Parse YYYY-MM-DD to a datetime, or a fixed fallback if absent/bad."""
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            pass
    return datetime(2000, 1, 1)


def iso_z(when: datetime) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def stable_tid(when: datetime, seed: str) -> str:
    """Deterministic, valid TID from a timestamp and a seed string.

    Several atproto lexicons (network.cosmik.card, site.standard.*) require
    TID-format record keys. Using the edition date for the timestamp and the
    seed for the low clock bits gives one stable key per (date, seed), so a
    re-run overwrites the same record instead of creating a duplicate, and keys
    sort by publish date.
    """
    micros = int(when.timestamp() * 1_000_000) & ((1 << 53) - 1)
    clock_id = int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) & 0x3FF
    return _s32encode(((micros << 10) | clock_id) & ((1 << 63) - 1))


def stable_rkey(number: str, when: datetime) -> str:
    """The Semble card's deterministic TID key for an edition."""
    return stable_tid(when, f"ht-card:{number}")


def strip_markdown_links(text: str) -> str:
    """Turn [label](url) into label, for a plain-text card description."""
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)


def build_card(edition: dict, synthesis: list) -> dict:
    """Build the network.cosmik.card record for one edition."""
    published = iso_z(edition_datetime(edition.get("date")))
    description = strip_markdown_links("\n\n".join(synthesis)).strip()
    title = edition.get("title") or f"The Hallway Track No. {edition['number']}"

    metadata = {
        "$type": "network.cosmik.card#urlMetadata",
        "type": "article",
        "title": title,
        "description": description,
        "author": SITE_NAME,
        "siteName": SITE_NAME,
        "publishedDate": published,
        "imageUrl": f"{SITE_URL}/images/og/{edition['number']}.png",
    }
    return {
        "$type": CARD_COLLECTION,
        "type": "URL",
        "content": {
            "$type": "network.cosmik.card#urlContent",
            "url": edition["url"],
            "metadata": metadata,
        },
        "createdAt": published,
    }


def put_record(jwt: str, did: str, collection: str, rkey: str, record: dict) -> str:
    resp = httpx.post(
        f"{PDS_HOST}/xrpc/com.atproto.repo.putRecord",
        headers={"Authorization": f"Bearer {jwt}"},
        json={"repo": did, "collection": collection, "rkey": rkey, "record": record},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["uri"]


def main():
    parser = argparse.ArgumentParser(description="Post an edition to Semble as one card")
    parser.add_argument("number", help="Edition number (e.g., 030)")
    parser.add_argument("--dry-run", action="store_true", help="Print the card, write nothing")
    args = parser.parse_args()

    edition = read_edition(args.number)
    synthesis, _ = parse_blocks(edition["body"])
    record = build_card(edition, synthesis)
    rkey = stable_rkey(edition["number"], edition_datetime(edition.get("date")))

    if args.dry_run:
        print(f"[dry-run] {CARD_COLLECTION} {rkey}")
        print(json.dumps(record, indent=2))
        return

    handle = os.environ.get("HT_ATPROTO_HANDLE")
    password = os.environ.get("HT_ATPROTO_PASSWORD")
    if not handle or not password:
        print("HT_ATPROTO_HANDLE/HT_ATPROTO_PASSWORD not set, skipping Semble card.")
        return

    jwt, did = login(handle, password)
    uri = put_record(jwt, did, CARD_COLLECTION, rkey, record)
    print(f"Posted Semble card: {uri}")


if __name__ == "__main__":
    main()
