"""Tests for the Semble card builder (post_semble)."""

from datetime import datetime

from post_semble import (
    build_card,
    edition_datetime,
    stable_rkey,
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


def test_build_card_matches_semble_shape():
    card = build_card(sample_edition(), ["First paragraph.", "Second paragraph."])

    assert card["$type"] == "network.cosmik.card"
    assert card["type"] == "URL"
    # The real Semble-written card has no top-level url; it lives inside content.
    assert "url" not in card

    content = card["content"]
    assert content["$type"] == "network.cosmik.card#urlContent"
    assert content["url"] == "https://hallway.aris.pub/no/030/"

    meta = content["metadata"]
    assert meta["$type"] == "network.cosmik.card#urlMetadata"
    assert meta["type"] == "article"
    assert meta["title"] == "Google Deep Review, AI research taste, AI in dissertations"
    assert meta["siteName"] == "The Hallway Track"
    assert meta["publishedDate"].startswith("2026-10-19T")
    assert meta["imageUrl"] == "https://hallway.aris.pub/images/og/030.png"
    assert card["createdAt"].startswith("2026-10-19T")


def test_description_is_joined_synthesis_without_markdown_links():
    synthesis = ["See [Deep Review](https://example.com/x) today.", "More context here."]
    card = build_card(sample_edition(), synthesis)
    desc = card["content"]["metadata"]["description"]

    assert desc == "See Deep Review today.\n\nMore context here."
    assert "https://example.com/x" not in desc
    assert "](" not in desc


def test_title_falls_back_when_absent():
    edition = sample_edition()
    del edition["title"]
    card = build_card(edition, ["x"])
    assert card["content"]["metadata"]["title"] == "The Hallway Track No. 030"


def test_strip_markdown_links():
    assert strip_markdown_links("a [b](http://c) d") == "a b d"
    assert strip_markdown_links("no links here") == "no links here"


def test_edition_datetime_parses_and_falls_back():
    assert edition_datetime("2026-10-19").year == 2026
    assert edition_datetime(None).year == 2000
    assert edition_datetime("garbage").year == 2000


def test_stable_rkey_is_deterministic_and_tid_shaped():
    when = datetime(2026, 10, 19)
    a = stable_rkey("030", when)
    b = stable_rkey("030", when)
    assert a == b
    assert len(a) == 13
    assert all(c in "234567abcdefghijklmnopqrstuvwxyz" for c in a)


def test_stable_rkey_differs_by_edition():
    when = datetime(2026, 10, 19)
    assert stable_rkey("030", when) != stable_rkey("031", when)
