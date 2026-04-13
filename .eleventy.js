const pluginRss = require("@11ty/eleventy-plugin-rss");

module.exports = function(eleventyConfig) {
  eleventyConfig.addPlugin(pluginRss);
  eleventyConfig.ignores.add("src/no/*.post.md");
  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/js");
  eleventyConfig.addPassthroughCopy("src/favicon.svg");
  eleventyConfig.addPassthroughCopy("src/images");

  eleventyConfig.addFilter("dateFormat", (date) => {
    const d = new Date(date);
    const months = ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"];
    return `${months[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
  });

  eleventyConfig.addFilter("isoDate", (date) => {
    const d = new Date(date);
    return d.toISOString().split("T")[0];
  });

  eleventyConfig.addFilter("padStart", (num, length) => {
    return String(num).padStart(length, "0");
  });

  eleventyConfig.addFilter("excerpt", (content) => {
    if (!content) return "";
    const stripped = content.replace(/<[^>]+>/g, "");
    return stripped.substring(0, 200).trim() + (stripped.length > 200 ? "..." : "");
  });

  eleventyConfig.addCollection("edition", function(collectionApi) {
    return collectionApi.getFilteredByTag("edition").filter(item => !item.data.draft);
  });

  eleventyConfig.addFilter("absoluteUrl", (url, base) => {
    if (!base) return url;
    return new URL(url, base).toString();
  });

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "_includes",
      layouts: "_layouts",
      data: "_data"
    },
    templateFormats: ["md", "njk", "html"],
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk"
  };
};
