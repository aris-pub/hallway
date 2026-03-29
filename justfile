set dotenv-load
export PATH := env("HOME") + "/.local/bin:" + env("PATH")

# Build the site locally (generate og:images + 11ty build)
build:
    node scripts/gen-og-images.js
    npm run build

# Deploy: build, commit, push
deploy: build
    git add -A
    git commit -m "Deploy $(date +%Y-%m-%d)" || true
    git push

# Run the curation agent (scans sources, writes draft, sends notification email)
agent:
    uv run --with httpx,resend python agent/curate.py

# Preview what the agent would do without scanning or writing
agent-dry:
    uv run --with httpx,resend python agent/curate.py --dry-run

# Broadcast an edition to newsletter subscribers
broadcast NUMBER *FLAGS:
    uv run --with resend,httpx python agent/broadcast.py {{NUMBER}} {{FLAGS}}

# Run tests
test:
    uv run --with httpx,resend,pytest pytest agent/test_curate.py -v

# Start local dev server
dev:
    npm start
