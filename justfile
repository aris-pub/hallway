set dotenv-load
export PATH := env("HOME") + "/.local/bin:" + env("PATH")

# Publish an edition (defers to Monday 9am if run on weekends, immediate on Monday+)
publish NUMBER:
    ./scripts/publish.sh {{NUMBER}}

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
