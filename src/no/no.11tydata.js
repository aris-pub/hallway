module.exports = {
  layout: "edition.njk",
  tags: "edition",
  eleventyComputed: {
    // Drafts render only for preview builds. Production never sets
    // INCLUDE_DRAFTS, so an unreviewed edition cannot reach the live site.
    permalink: data => {
      if (data.draft && !process.env.INCLUDE_DRAFTS) return false;
      return `/no/${String(data.number).padStart(3, "0")}/`;
    }
  }
};
