"""
Post a published Hallway Track edition to Semble as a collection of links.

Each edition becomes one network.cosmik.collection on the dedicated Hallway
Track atproto account, and every link the edition references becomes one
network.cosmik.card inside it. The card and the collection are tied together by
a network.cosmik.collectionLink join record. This mirrors how Semble itself
models a collection, so a person browsing the Hallway Track profile sees each
week's curation as a set of link cards, not a single newsletter card.

Semble picks the records up from the atproto firehose, so there is no Semble
registration step: whatever the account writes to network.cosmik.* shows up.

Record keys are deterministic (a TID derived from the edition date and a seed),
so a re-run overwrites the same records instead of creating duplicates.

Usage:
    uv run python agent/post_semble.py 030
    uv run python agent/post_semble.py 030 --dry-run
    uv run python agent/post_semble.py all          # backfill every edition

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

from broadcast import EDITIONS_DIR, SITE_URL, parse_blocks, read_edition
from post_bsky import PDS_HOST, login

CARD_COLLECTION = "network.cosmik.card"
COLLECTION_COLLECTION = "network.cosmik.collection"
LINK_COLLECTION = "network.cosmik.collectionLink"
SITE_NAME = "The Hallway Track"
ACCESS_TYPE = "CLOSED"
DESCRIPTION_LIMIT = 500

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
    """Deterministic, collision-resistant TID from a timestamp and a seed.

    The cosmik lexicons key on TIDs. Every record in one edition shares the same
    date, so the seed has to carry enough entropy to keep their keys apart. The
    high bits hold the edition date in seconds (so keys still sort by date) and
    the low 30 bits come from the seed hash, which gives a billion slots per
    date. That keeps distinct seeds on the same date from colliding, where the
    old 10-bit clock field did not.
    """
    secs = int(when.timestamp())
    low = int(hashlib.sha256(seed.encode()).hexdigest(), 16) & ((1 << 30) - 1)
    return _s32encode(((secs << 30) | low) & ((1 << 63) - 1))


def collection_rkey(number: str, when: datetime) -> str:
    return stable_tid(when, f"ht-collection:{number}")


def card_rkey(number: str, url: str, when: datetime) -> str:
    return stable_tid(when, f"ht-card:{number}:{url}")


def link_rkey(number: str, url: str, when: datetime) -> str:
    return stable_tid(when, f"ht-link:{number}:{url}")


def strip_markdown_links(text: str) -> str:
    """Turn [label](url) into label, for plain-text card and collection text."""
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)


def edition_links(sections: list) -> list:
    """All link items across an edition's sections, de-duplicated by URL,
    in document order."""
    seen = set()
    out = []
    for section in sections:
        for item in section["items"]:
            url = item["url"]
            if url in seen:
                continue
            seen.add(url)
            out.append(item)
    return out


def collection_description(synthesis: list, url: str) -> str:
    """The editorial synthesis, markdown links flattened, trimmed to fit the
    500-character limit, with a pointer back to the full edition."""
    text = strip_markdown_links(" ".join(synthesis)).strip()
    suffix = f" Full edition: {url}"
    limit = DESCRIPTION_LIMIT - len(suffix)
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0].rstrip(".,;: ") + "."
    return text + suffix


def build_collection(edition: dict, synthesis: list) -> dict:
    published = iso_z(edition_datetime(edition.get("date")))
    name = (edition.get("title") or f"The Hallway Track No. {edition['number']}")[:100]
    return {
        "$type": COLLECTION_COLLECTION,
        "name": name,
        "accessType": ACCESS_TYPE,
        "description": collection_description(synthesis, edition["url"]),
        "createdAt": published,
        "updatedAt": published,
    }


def build_card(item: dict, published: str) -> dict:
    """Build a URL card for one referenced link. Metadata keys with no value
    are left out."""
    metadata = {"$type": "network.cosmik.card#urlMetadata", "type": "article"}
    if item.get("title"):
        metadata["title"] = item["title"]
    description = strip_markdown_links(item.get("description", "")).strip()
    if description:
        metadata["description"] = description
    if item.get("source"):
        metadata["siteName"] = item["source"]
    return {
        "$type": CARD_COLLECTION,
        "type": "URL",
        "content": {
            "$type": "network.cosmik.card#urlContent",
            "url": item["url"],
            "metadata": metadata,
        },
        "createdAt": published,
    }


def build_link(collection_ref: dict, card_ref: dict, did: str, added_at: str) -> dict:
    return {
        "$type": LINK_COLLECTION,
        "collection": collection_ref,
        "card": card_ref,
        "addedBy": did,
        "addedAt": added_at,
        "createdAt": added_at,
    }


def put_record(jwt: str, did: str, collection: str, rkey: str, record: dict) -> dict:
    """Write one record. Returns the strong reference (uri and cid)."""
    resp = httpx.post(
        f"{PDS_HOST}/xrpc/com.atproto.repo.putRecord",
        headers={"Authorization": f"Bearer {jwt}"},
        json={"repo": did, "collection": collection, "rkey": rkey, "record": record},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return {"uri": data["uri"], "cid": data["cid"]}


def process_edition(jwt: str, did: str, number: str) -> dict:
    """Write one edition's collection, cards and links. Returns a small tally."""
    edition = read_edition(number)
    synthesis, sections = parse_blocks(edition["body"])
    links = edition_links(sections)
    when = edition_datetime(edition.get("date"))
    published = iso_z(when)

    if not links:
        print(f"  no links, skipping edition {number}")
        return {"collections": 0, "cards": 0, "links": 0}

    col_ref = put_record(
        jwt, did, COLLECTION_COLLECTION,
        collection_rkey(number, when), build_collection(edition, synthesis),
    )

    for item in links:
        card_ref = put_record(
            jwt, did, CARD_COLLECTION,
            card_rkey(number, item["url"], when), build_card(item, published),
        )
        put_record(
            jwt, did, LINK_COLLECTION,
            link_rkey(number, item["url"], when),
            build_link(col_ref, card_ref, did, published),
        )

    tally = {"collections": 1, "cards": len(links), "links": len(links)}
    print(f"  edition {number}: 1 collection, {len(links)} cards, {len(links)} links")
    return tally


def all_edition_numbers() -> list:
    """Every main edition file (NNN.md), excluding the .aris and .post variants."""
    numbers = []
    for path in sorted(EDITIONS_DIR.glob("[0-9][0-9][0-9].md")):
        numbers.append(path.stem)
    return numbers


def main():
    parser = argparse.ArgumentParser(description="Post an edition to Semble as a collection of links")
    parser.add_argument("number", help="Edition number (e.g., 030), or 'all' to backfill")
    parser.add_argument("--dry-run", action="store_true", help="Print the records, write nothing")
    args = parser.parse_args()

    if args.dry_run:
        if args.number == "all":
            parser.error("--dry-run works on a single edition, not 'all'")
        edition = read_edition(args.number)
        synthesis, sections = parse_blocks(edition["body"])
        links = edition_links(sections)
        when = edition_datetime(edition.get("date"))
        published = iso_z(when)
        print(f"[dry-run] {COLLECTION_COLLECTION} {collection_rkey(args.number, when)}")
        print(json.dumps(build_collection(edition, synthesis), indent=2))
        for item in links:
            print(f"\n[dry-run] {CARD_COLLECTION} {card_rkey(args.number, item['url'], when)}")
            print(json.dumps(build_card(item, published), indent=2))
        print(f"\n[dry-run] {len(links)} collectionLink records would tie these cards to the collection.")
        return

    handle = os.environ.get("HT_ATPROTO_HANDLE")
    password = os.environ.get("HT_ATPROTO_PASSWORD")
    if not handle or not password:
        print("HT_ATPROTO_HANDLE/HT_ATPROTO_PASSWORD not set, skipping Semble post.")
        return

    jwt, did = login(handle, password)
    numbers = all_edition_numbers() if args.number == "all" else [args.number.zfill(3)]

    total = {"collections": 0, "cards": 0, "links": 0}
    for number in numbers:
        tally = process_edition(jwt, did, number)
        for key in total:
            total[key] += tally[key]

    print(
        f"Done: {total['collections']} collections, {total['cards']} cards, "
        f"{total['links']} links across {len(numbers)} edition(s)."
    )


if __name__ == "__main__":
    main()
