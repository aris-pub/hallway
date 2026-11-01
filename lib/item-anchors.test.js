const test = require("node:test");
const assert = require("node:assert");
const { anchorItems, slugify } = require("./item-anchors");

const page = (synthesis, items) =>
  `<html><div class="edition-body">${synthesis}<h2>Section</h2>\n<ul>\n${items}</ul></div></html>`;

const item = (url, title) =>
  `<li>\n<p><a href="${url}">${title}</a></p>\n<p>Framing.</p>\n</li>\n`;

test("synthesis link to an item becomes an in-page link", () => {
  const out = anchorItems(page(
    '<p>See <a href="https://a.com/x">this study</a>.</p>\n',
    item("https://a.com/x", "Distributed AI agents at scale"),
  ));
  assert.match(out, /<a href="#distributed-ai-agents-at-scale" class="item-ref">this study<\/a>/);
  assert.match(out, /<li id="distributed-ai-agents-at-scale">/);
});

test("synthesis link to a URL that is not an item stays external", () => {
  const out = anchorItems(page(
    '<p>See <a href="https://other.com">elsewhere</a>.</p>\n',
    item("https://a.com/x", "Title"),
  ));
  assert.match(out, /<a href="https:\/\/other.com">elsewhere<\/a>/);
});

test("item titles are not rewritten", () => {
  const out = anchorItems(page("", item("https://a.com/x", "Title")));
  assert.match(out, /<p><a href="https:\/\/a.com\/x">Title<\/a><\/p>/);
});

test("items with the same title get distinct ids", () => {
  const out = anchorItems(page("", item("https://a.com", "Same") + item("https://b.com", "Same")));
  assert.match(out, /<li id="same">/);
  assert.match(out, /<li id="same-2">/);
});

test("links in item descriptions are left alone", () => {
  const items = `<li>\n<p><a href="https://a.com">A</a></p>\n<p>Hosting a <a href="https://b.com">briefing</a>.</p>\n</li>\n`;
  const out = anchorItems(page("", items));
  assert.match(out, /<a href="https:\/\/b.com">briefing<\/a>/);
});

test("pages without an edition body are unchanged", () => {
  const html = '<p><a href="https://a.com">x</a></p>';
  assert.strictEqual(anchorItems(html), html);
});

test("slugify keeps the first six words and drops punctuation", () => {
  assert.strictEqual(
    slugify("Major Revision, Minor Accountability: LLMs as Reviewers of Published Articles"),
    "major-revision-minor-accountability-llms-as",
  );
  assert.strictEqual(slugify("Lemma by Axiomatic AI"), "lemma-by-axiomatic-ai");
});
