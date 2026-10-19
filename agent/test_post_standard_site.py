"""Tests for the standard.site record builders (post_standard_site)."""

from datetime import datetime

from post_standard_site import (
    DOCUMENT_COLLECTION,
    PUBLICATION_COLLECTION,
    PUBLICATION_RKEY,
    build_document,
    build_publication,
    document_rkey,
    publication_uri,
)

S32 = "234567abcdefghijklmnopqrstuvwxyz"


def sample_edition():
    return {
        "number": "030",
        "url": "https://hallway.aris.pub/no/030/",
        "date": "2026-10-19",
        "title": "Google Deep Review, AI research taste, AI in dissertations",
        "description": "The Hallway Track No. 030 - How AI is affecting the practice of science",
        "body": "",
    }


def test_build_publication_required_fields():
    pub = build_publication()
    assert pub["$type"] == "site.standard.publication"
    assert pub["url"] == "https://hallway.aris.pub"
    assert pub["name"] == "The Hallway Track"
    assert pub["description"]


def test_publication_rkey_is_a_tid():
    # The PDS validates site.standard.* keys as TIDs, so "self" is not allowed.
    assert len(PUBLICATION_RKEY) == 13
    assert all(c in S32 for c in PUBLICATION_RKEY)


def test_publication_uri_uses_the_tid_key():
    uri = publication_uri("did:plc:abc123")
    assert uri == f"at://did:plc:abc123/site.standard.publication/{PUBLICATION_RKEY}"


def test_document_rkey_is_deterministic_tid():
    when = datetime(2026, 10, 19)
    a = document_rkey("030", when)
    b = document_rkey("30", when)  # zero-padded internally
    assert a == b
    assert len(a) == 13
    assert all(c in S32 for c in a)


def test_document_rkey_differs_by_edition():
    when = datetime(2026, 10, 19)
    assert document_rkey("030", when) != document_rkey("029", when)


def test_build_document_required_and_optional_fields():
    pub_uri = publication_uri("did:plc:abc123")
    doc = build_document(sample_edition(), ["First para.", "Second para."], pub_uri)

    assert doc["$type"] == "site.standard.document"
    # Required by the lexicon: site, title, publishedAt.
    assert doc["site"] == pub_uri
    assert doc["title"] == "Google Deep Review, AI research taste, AI in dissertations"
    assert doc["publishedAt"].startswith("2026-10-19T")
    assert doc["path"] == "/no/030/"
    assert doc["textContent"] == "First para.\n\nSecond para."
    assert doc["description"]


def test_build_document_strips_markdown_links_in_textcontent():
    pub_uri = publication_uri("did:plc:abc123")
    doc = build_document(
        sample_edition(),
        ["See [Deep Review](https://example.com/x) today."],
        pub_uri,
    )
    assert doc["textContent"] == "See Deep Review today."
    assert "](" not in doc["textContent"]


def test_build_document_title_fallback_and_no_description():
    edition = sample_edition()
    del edition["title"]
    del edition["description"]
    doc = build_document(edition, ["x"], publication_uri("did:plc:abc123"))
    assert doc["title"] == "The Hallway Track No. 030"
    assert "description" not in doc


def test_collection_constants():
    assert PUBLICATION_COLLECTION == "site.standard.publication"
    assert DOCUMENT_COLLECTION == "site.standard.document"
