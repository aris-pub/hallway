module.exports = {
  layout: "edition.njk",
  tags: "edition",
  eleventyComputed: {
    permalink: data => {
      if (data.draft) return false;
      return `/no/${String(data.number).padStart(3, "0")}/`;
    }
  }
};
