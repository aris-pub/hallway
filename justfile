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

# Post to Bluesky (optionally at a specific time, e.g., just bsky 003 "text" 14:00)
bsky NUMBER TEXT AT="":
    uv run --with httpx python agent/post_bsky.py {{NUMBER}} "{{TEXT}}" {{ if AT != "" { "--at " + AT } else { "" } }}

# Add a link to the inbox for the next edition
inbox LINK:
    echo '\n- {{LINK}}' >> inbox.md
    git add inbox.md && git commit -m "Inbox: {{LINK}}" && git push

# Run tests
test:
    uv run --with httpx,resend,pytest pytest agent/test_curate.py -v

# Start local dev server
dev:
    npm start
