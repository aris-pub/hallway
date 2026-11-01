// The synthesis paragraph links a phrase to an item by using that item's own URL,
// so email, RSS and the social cards still get a working link to the source. Only
// the web page rewrites those links to jump to the item on the page.

function slugify(text) {
  const words = text
    .replace(/<[^>]+>/g, "")
    .replace(/&[a-z0-9#]+;/gi, " ")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  return words.slice(0, 6).join("-") || "item";
}

function anchorItems(html) {
  const bodyStart = html.indexOf('<div class="edition-body">');
  if (bodyStart === -1) return html;
  const firstHeading = html.indexOf("<h2", bodyStart);
  if (firstHeading === -1) return html;

  const ids = new Map();
  const used = new Set();
  const items = html.slice(firstHeading).replace(
    /<li>(\s*<p><a href="([^"]+)">([\s\S]*?)<\/a>)/g,
    (match, rest, url, title) => {
      if (ids.has(url)) return match;
      let id = slugify(title);
      for (let n = 2; used.has(id); n++) id = `${slugify(title)}-${n}`;
      used.add(id);
      ids.set(url, id);
      return `<li id="${id}">${rest}`;
    }
  );

  const synthesis = html.slice(bodyStart, firstHeading).replace(
    /<a href="([^"]+)">/g,
    (match, url) => (ids.has(url) ? `<a href="#${ids.get(url)}" class="item-ref">` : match)
  );

  return html.slice(0, bodyStart) + synthesis + items;
}

module.exports = { anchorItems, slugify };
