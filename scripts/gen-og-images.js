const fs = require("fs");
const path = require("path");
const sharp = require("sharp");

const EDITIONS_DIR = path.join(__dirname, "..", "src", "no");
const IMAGES_DIR = path.join(__dirname, "..", "src", "images", "og");

function makeSvg(title, subtitle) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#fafaf8"/>
  <rect x="0" y="0" width="1200" height="4" fill="#AD71F2"/>
  <text x="100" y="200" font-family="Georgia, Garamond, serif" font-size="36" fill="#7a7a7a">The Hallway Track</text>
  <text x="100" y="320" font-family="Georgia, Garamond, serif" font-size="80" font-weight="400" fill="#0a0a0a" letter-spacing="-2">${title}</text>
  <text x="100" y="400" font-family="sans-serif" font-size="28" fill="#7a7a7a">${subtitle}</text>
  <text x="100" y="540" font-family="sans-serif" font-size="20" fill="#b0b0b0">hallway.aris.pub</text>
</svg>`;
}

async function main() {
  fs.mkdirSync(IMAGES_DIR, { recursive: true });

  const files = fs.readdirSync(EDITIONS_DIR).filter(f => /^\d+\.md$/.test(f));

  for (const file of files) {
    const content = fs.readFileSync(path.join(EDITIONS_DIR, file), "utf-8");
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) continue;

    const frontmatter = match[1];
    const numMatch = frontmatter.match(/number:\s*(\d+)/);
    const dateMatch = frontmatter.match(/date:\s*(\S+)/);
    const draftMatch = frontmatter.match(/draft:\s*true/);
    if (!numMatch || draftMatch) continue;

    const number = numMatch[1].padStart(3, "0");
    const date = dateMatch ? dateMatch[1] : "";
    const outPath = path.join(IMAGES_DIR, `${number}.png`);

    if (fs.existsSync(outPath)) continue;

    const svg = makeSvg(`No. ${number}`, date);
    await sharp(Buffer.from(svg)).resize(1200, 630).png().toFile(outPath);
    console.log(`Generated ${outPath}`);
  }

  // Default image
  const defaultPath = path.join(__dirname, "..", "src", "images", "og-default.png");
  if (!fs.existsSync(defaultPath)) {
    const svg = makeSvg("The Hallway Track", "How AI is affecting the practice of science.");
    await sharp(Buffer.from(svg)).resize(1200, 630).png().toFile(defaultPath);
    console.log(`Generated ${defaultPath}`);
  }
}

main().catch(console.error);
