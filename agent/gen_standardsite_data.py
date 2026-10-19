"""
Regenerate the committed standard.site data the eleventy build reads.

Writes two files from the editions on disk:
  - src/_data/standardsite.json  : { did, publicationUri, documents: {NNN: tid} }
  - src/.well-known/site.standard.publication : the publication AT-URI

The document keys are deterministic TIDs (post_standard_site.document_rkey), so
this map always matches what the publisher writes to atproto. Run it before the
eleventy build so a new edition's document key is present for its link tag.
"""

import json
from pathlib import Path

from broadcast import read_edition
from post_semble import edition_datetime
from post_standard_site import HT_DID, document_rkey, publication_uri

REPO = Path(__file__).parent.parent
EDITIONS = REPO / "src" / "no"
DATA = REPO / "src" / "_data" / "standardsite.json"
WELLKNOWN = REPO / "src" / ".well-known" / "site.standard.publication"


def main():
    documents = {}
    for path in sorted(EDITIONS.glob("[0-9][0-9][0-9].md")):
        number = path.stem
        if number == "000":
            # The intro page (frontmatter number: 0) is a non-edition to the
            # template's {% if number %} guard, so it carries no link tag and
            # gets no document record.
            continue
        try:
            edition = read_edition(number)
        except (FileNotFoundError, ValueError):
            # Skip drafts and anything that does not parse.
            continue
        documents[number] = document_rkey(number, edition_datetime(edition.get("date")))

    pub_uri = publication_uri(HT_DID)
    DATA.write_text(
        json.dumps({"did": HT_DID, "publicationUri": pub_uri, "documents": documents}, indent=2) + "\n"
    )
    WELLKNOWN.parent.mkdir(parents=True, exist_ok=True)
    WELLKNOWN.write_text(pub_uri + "\n")
    print(f"wrote {DATA} ({len(documents)} documents)")
    print(f"wrote {WELLKNOWN}")


if __name__ == "__main__":
    main()
