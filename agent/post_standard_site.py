"""
Publish Hallway Track editions to the AT Protocol as standard.site records.

standard.site ("RSS on atproto") makes the feed subscribable in long-form
atproto readers (Leaflet, Offprint, pckt) and visible to standard.site
indexers. We keep one site.standard.publication record for the whole feed
(created once) and write one site.standard.document per edition on publish, to
the dedicated Hallway Track atproto account. This is independent of the Semble
card (post_semble.py); both write to the same account.

Record keys must be TIDs (the PDS validates site.standard.* keys as TIDs), so
both the publication key and each document key are deterministic TIDs. The
per-edition document key cannot be recomputed in the eleventy template, so
gen_standardsite_data.py writes a committed number -> key map the template
reads for its <link rel="site.standard.document"> tag, and the
/.well-known/site.standard.publication file.

The publication is verified by that /.well-known file on hallway.aris.pub and
each edition page carries the link tag. Those two site-serving pieces live in
the eleventy build, not here.

Usage:
    uv run python agent/post_standard_site.py 030
    uv run python agent/post_standard_site.py 030 --dry-run

Environment:
    HT_ATPROTO_HANDLE / HT_ATPROTO_PASSWORD  the dedicated HT atproto account
"""

import argparse
import json
import os
from datetime import datetime

from broadcast import SITE_URL, parse_blocks, read_edition
from post_bsky import login
from post_semble import edition_datetime, iso_z, put_record, stable_tid, strip_markdown_links

PUBLICATION_COLLECTION = "site.standard.publication"
DOCUMENT_COLLECTION = "site.standard.document"

# The dedicated Hallway Track atproto account. Used to shape the committed
# .well-known and _data files without a login; the publisher logs in and the
# resolved DID matches this.
HT_DID = "did:plc:xecjm3k6r7lqozkjbtikugva"

# Deterministic TID for the one publication record (fixed seed, fixed epoch).
PUBLICATION_RKEY = stable_tid(datetime(2026, 1, 1), "ht-publication")

PUBLICATION_NAME = "The Hallway Track"
PUBLICATION_DESCRIPTION = "How AI is affecting the practice of science."


def build_publication() -> dict:
    """The single site.standard.publication record for the HT feed."""
    return {
        "$type": PUBLICATION_COLLECTION,
        "url": SITE_URL,
        "name": PUBLICATION_NAME,
        "description": PUBLICATION_DESCRIPTION,
        "preferences": {"showInDiscover": True},
    }


def publication_uri(did: str = HT_DID) -> str:
    return f"at://{did}/{PUBLICATION_COLLECTION}/{PUBLICATION_RKEY}"


def document_rkey(number: str, when: datetime) -> str:
    """Deterministic TID key for an edition's document."""
    return stable_tid(when, f"ht-doc:{number.zfill(3)}")


def build_document(edition: dict, synthesis: list, pub_uri: str) -> dict:
    """One site.standard.document for an edition."""
    published = iso_z(edition_datetime(edition.get("date")))
    text = strip_markdown_links("\n\n".join(synthesis)).strip()
    record = {
        "$type": DOCUMENT_COLLECTION,
        "site": pub_uri,
        "title": edition.get("title") or f"The Hallway Track No. {edition['number']}",
        "path": f"/no/{edition['number']}/",
        "publishedAt": published,
        "textContent": text,
    }
    if edition.get("description"):
        record["description"] = edition["description"]
    return record


def main():
    parser = argparse.ArgumentParser(description="Publish an edition as standard.site records")
    parser.add_argument("number", help="Edition number (e.g., 030)")
    parser.add_argument("--dry-run", action="store_true", help="Print the records, write nothing")
    args = parser.parse_args()

    edition = read_edition(args.number)
    synthesis, _ = parse_blocks(edition["body"])
    when = edition_datetime(edition.get("date"))
    doc_rk = document_rkey(edition["number"], when)
    pub_uri = publication_uri()

    if args.dry_run:
        print(f"[dry-run] {PUBLICATION_COLLECTION} {PUBLICATION_RKEY}")
        print(json.dumps(build_publication(), indent=2))
        print(f"\n[dry-run] {DOCUMENT_COLLECTION} {doc_rk}")
        print(json.dumps(build_document(edition, synthesis, pub_uri), indent=2))
        return

    handle = os.environ.get("HT_ATPROTO_HANDLE")
    password = os.environ.get("HT_ATPROTO_PASSWORD")
    if not handle or not password:
        print("HT_ATPROTO_HANDLE/HT_ATPROTO_PASSWORD not set, skipping standard.site publish.")
        return

    jwt, did = login(handle, password)
    pub_uri = publication_uri(did)

    put_record(jwt, did, PUBLICATION_COLLECTION, PUBLICATION_RKEY, build_publication())
    doc_uri = put_record(
        jwt, did, DOCUMENT_COLLECTION, doc_rk,
        build_document(edition, synthesis, pub_uri),
    )
    print(f"Published standard.site document: {doc_uri}")
    print(f"Publication AT-URI: {pub_uri}")


if __name__ == "__main__":
    main()
