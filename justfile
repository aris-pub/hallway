set dotenv-load
export PATH := env("HOME") + "/.local/bin:" + env("PATH")

# Publish an edition: remove draft, build, deploy, email subscribers
publish NUMBER:
    sed -i '' '/^draft: true$/d' src/no/{{NUMBER}}.md
    node scripts/gen-og-images.js
    npm run build
    git add -A
    git commit -m "Publish No. {{NUMBER}}"
    git push
    uv run --with resend,httpx python agent/broadcast.py {{NUMBER}}

# Run the curation agent (scans sources, writes draft, sends notification email)
agent:
    uv run --with httpx,resend python agent/curate.py

# Preview what the agent would do without scanning or writing
agent-dry:
    uv run --with httpx,resend python agent/curate.py --dry-run

# Run tests
test:
    uv run --with httpx,resend,pytest pytest agent/test_curate.py -v

# Start local dev server
dev:
    npm start
