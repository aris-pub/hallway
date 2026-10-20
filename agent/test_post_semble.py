"""Tests for the Semble collection publisher (post_semble)."""

from datetime import datetime

from post_semble import (
    build_card,
    build_collection,
    build_link,
    card_rkey,
    collection_description,
    collection_rkey,
    edition_datetime,
    edition_links,
    link_rkey,
    stable_tid,
    strip_markdown_links,
)


def sample_edition():
    return {
        "number": "030",
        "url": "https://hallway.aris.pub/no/030/",
        "date": "2026-10-19",
        "title": "Google Deep Review, AI research taste, AI in dissertations",
        "body": "",
    }


def sample_item():
    return {
        "title": "Google launches Deep Review",
        "url": "https://www.rdworldonline.com/google-launches-deep-review/",
        "source": "R&D World, October 14 2026",
        "description": "Google Research released [Deep Review](https://example.com/x), a checker.",
    }


def test_collection_shape():
    col = build_collection(sample_edition(), ["First paragraph.", "Second one."])
    assert col["$type"] == "network.cosmik.collection"
    assert col["name"] == "Google Deep Review, AI research taste, AI in dissertations"
    assert col["accessType"] == "CLOSED"
    assert col["createdAt"].startswith("2026-10-19T")
    assert col["updatedAt"].startswith("2026-10-19T")
    assert "https://hallway.aris.pub/no/030/" in col["description"]


def test_collection_name_falls_back_and_truncates():
    edition = sample_edition()
    del edition["title"]
    col = build_collection(edition, ["x"])
    assert col["name"] == "The Hallway Track No. 030"

    edition2 = sample_edition()
    edition2["title"] = "A" * 150
    col2 = build_collection(edition2, ["x"])
    assert len(col2["name"]) == 100


def test_collection_description_fits_limit_and_strips_links():
    synthesis = ["See [Deep Review](https://example.com/x) today. " + "word " * 200]
    desc = collection_description(synthesis, "https://hallway.aris.pub/no/030/")
    assert len(desc) <= 500
    assert "https://example.com/x" not in desc
    assert "](" not in desc
    assert desc.endswith("Full edition: https://hallway.aris.pub/no/030/")


def test_card_shape_from_link_item():
    card = build_card(sample_item(), "2026-10-19T00:00:00.000Z")
    assert card["$type"] == "network.cosmik.card"
    assert card["type"] == "URL"
    assert "url" not in card  # url lives inside content, like a real Semble card

    content = card["content"]
    assert content["$type"] == "network.cosmik.card#urlContent"
    assert content["url"] == "https://www.rdworldonline.com/google-launches-deep-review/"

    meta = content["metadata"]
    assert meta["$type"] == "network.cosmik.card#urlMetadata"
    assert meta["type"] == "article"
    assert meta["title"] == "Google launches Deep Review"
    assert meta["siteName"] == "R&D World, October 14 2026"
    # Markdown links inside the description are flattened to their text.
    assert meta["description"] == "Google Research released Deep Review, a checker."
    assert card["createdAt"] == "2026-10-19T00:00:00.000Z"


def test_card_omits_empty_metadata_fields():
    item = {"title": "", "url": "https://x.example/", "source": "", "description": ""}
    meta = build_card(item, "2026-10-19T00:00:00.000Z")["content"]["metadata"]
    assert "title" not in meta
    assert "siteName" not in meta
    assert "description" not in meta
    assert meta["type"] == "article"


def test_link_record_shape():
    col_ref = {"uri": "at://did/col/1", "cid": "bafycol"}
    card_ref = {"uri": "at://did/card/2", "cid": "bafycard"}
    link = build_link(col_ref, card_ref, "did:plc:ht", "2026-10-19T00:00:00.000Z")
    assert link["$type"] == "network.cosmik.collectionLink"
    assert link["collection"] == col_ref
    assert link["card"] == card_ref
    assert link["addedBy"] == "did:plc:ht"
    assert link["addedAt"] == "2026-10-19T00:00:00.000Z"


def test_edition_links_dedupes_by_url():
    sections = [
        {"name": "A", "items": [{"url": "u1", "title": "t1"}, {"url": "u2", "title": "t2"}]},
        {"name": "B", "items": [{"url": "u1", "title": "dup"}, {"url": "u3", "title": "t3"}]},
    ]
    links = edition_links(sections)
    assert [i["url"] for i in links] == ["u1", "u2", "u3"]


def test_strip_markdown_links():
    assert strip_markdown_links("a [b](http://c) d") == "a b d"
    assert strip_markdown_links("no links here") == "no links here"


def test_edition_datetime_parses_and_falls_back():
    assert edition_datetime("2026-10-19").year == 2026
    assert edition_datetime(None).year == 2000
    assert edition_datetime("garbage").year == 2000


def test_rkeys_are_deterministic_and_tid_shaped():
    when = datetime(2026, 10, 19)
    url = "https://x.example/"
    for fn, args in [
        (collection_rkey, ("030", when)),
        (card_rkey, ("030", url, when)),
        (link_rkey, ("030", url, when)),
    ]:
        a = fn(*args)
        b = fn(*args)
        assert a == b
        assert len(a) == 13
        assert all(c in "234567abcdefghijklmnopqrstuvwxyz" for c in a)


def test_card_rkey_differs_by_url_and_edition():
    when = datetime(2026, 10, 19)
    assert card_rkey("030", "u1", when) != card_rkey("030", "u2", when)
    assert card_rkey("030", "u1", when) != card_rkey("031", "u1", when)


def test_collection_and_card_and_link_keys_are_distinct():
    when = datetime(2026, 10, 19)
    url = "https://x.example/"
    keys = {
        collection_rkey("030", when),
        card_rkey("030", url, when),
        link_rkey("030", url, when),
    }
    assert len(keys) == 3


def test_no_card_key_collision_within_an_edition():
    # Every card in one edition shares the edition date, so the seed is the only
    # thing keeping the keys apart. A whole edition of distinct URLs on one date
    # must produce distinct keys.
    when = datetime(2026, 10, 19)
    urls = [f"https://example.com/{i}" for i in range(50)]
    keys = {card_rkey("030", u, when) for u in urls}
    assert len(keys) == len(urls)
