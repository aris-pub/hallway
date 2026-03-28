# Build the site locally (generate og:images + 11ty build)
build:
    node scripts/gen-og-images.js
    npm run build

# Deploy: build, commit, push
deploy: build
    git add -A
    git commit -m "Deploy $(date +%Y-%m-%d)" || true
    git push

# Run the curation agent (generates a draft edition)
agent *FLAGS:
    uv run --with anthropic,httpx,resend python agent/curate.py {{FLAGS}}

# Run the curation agent in dry-run mode (no email)
agent-dry:
    just agent --dry-run

# Broadcast an edition to newsletter subscribers
broadcast NUMBER *FLAGS:
    uv run --with resend,httpx python agent/broadcast.py {{NUMBER}} {{FLAGS}}

# Run tests
test:
    uv run --with anthropic,httpx,resend,pytest pytest agent/test_curate.py -v

# Start local dev server
dev:
    npm start
