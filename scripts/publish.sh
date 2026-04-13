#!/bin/bash
set -euo pipefail

NUMBER="$1"
PADDED=$(printf "%03d" "$NUMBER")
FILE="src/no/${PADDED}.md"
POST_FILE="src/no/${PADDED}.post.md"
REMOTE="leo@syenite.local"
REMOTE_DIR="/home/leo/aris/hallway"

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE does not exist"
    exit 1
fi

DAY=$(date +%u)   # 1=Monday, 7=Sunday
HOUR=$(date +%H)

deploy_and_broadcast() {
    if [[ "$(uname)" == "Darwin" ]]; then
        sed -i '' '/^draft: true$/d' "$FILE"
    else
        sed -i '/^draft: true$/d' "$FILE"
    fi
    [ -d node_modules ] || npm install --silent
    node scripts/gen-og-images.js
    npm run build
    git add -A
    git commit -m "Publish No. ${PADDED}"
    git push
    uv run --with resend,httpx python agent/broadcast.py "$PADDED"
    echo "Deployed and broadcast No. ${PADDED}"
}

post_social() {
    if [ ! -f "$POST_FILE" ]; then
        echo "No post file found at $POST_FILE, skipping social."
        return
    fi

    BSKY_TEXT=$(sed -n '1,/^---$/p' "$POST_FILE" | sed '/^---$/d')
    LI_TEXT=$(sed -n '/^---$/,$ p' "$POST_FILE" | sed '1d')

    if [ -n "$BSKY_TEXT" ] && [ -n "${BSKY_HANDLE:-}" ]; then
        uv run --with httpx python agent/post_bsky.py "$PADDED" "$BSKY_TEXT"
        echo "Posted to Bluesky"
    fi

    if [ -n "$LI_TEXT" ]; then
        echo ""
        echo "=== LinkedIn post (copy and paste manually): ==="
        echo ""
        echo "$LI_TEXT"
        echo ""
    fi
}

run_all_now() {
    deploy_and_broadcast
    post_social
    echo "Published No. ${PADDED}"
}

schedule_on_server() {
    echo "Scheduling No. ${PADDED} on syenite..."

    # Push the reviewed edition first so server has it
    git add "$FILE" "$POST_FILE" 2>/dev/null || true
    git commit -m "Review No. ${PADDED}" || true
    git push

    # Deploy + broadcast at Monday 9am (self-deleting)
    DEPLOY_CMD="0 9 * * 1 cd ${REMOTE_DIR} && git pull --quiet && PATH=/home/leo/.local/bin:\$PATH ./scripts/publish.sh ${PADDED} --deploy-only >> /home/leo/.hermes/cron/output/hallway-publish.log 2>&1 && (crontab -l | grep -v 'publish.sh ${PADDED} --deploy-only' | crontab -)"

    # Bluesky post at Monday 2pm (self-deleting)
    BSKY_CMD="0 14 * * 1 cd ${REMOTE_DIR} && PATH=/home/leo/.local/bin:\$PATH ./scripts/publish.sh ${PADDED} --social-only >> /home/leo/.hermes/cron/output/hallway-publish.log 2>&1 && (crontab -l | grep -v 'publish.sh ${PADDED} --social-only' | crontab -)"

    ssh "$REMOTE" "(crontab -l; echo '${DEPLOY_CMD}'; echo '${BSKY_CMD}') | crontab -"

    echo "Scheduled:"
    echo "  Monday 9:00 AM  - deploy + broadcast email"
    echo "  Monday 2:00 PM  - Bluesky post"
    echo "  LinkedIn post will be printed to terminal when you run 'just publish ${PADDED}' on Monday"
}

# Handle internal flags from scheduled cron
if [[ "${2:-}" == "--deploy-only" ]]; then
    deploy_and_broadcast
    exit 0
fi

if [[ "${2:-}" == "--social-only" ]]; then
    post_social
    exit 0
fi

# Normal invocation: decide whether to run now or schedule
if [ "$DAY" -eq 1 ]; then
    if [ "$HOUR" -ge 9 ]; then
        if [ "$HOUR" -ge 10 ]; then
            echo "It's Monday $(date +%H:%M). Edition will publish immediately."
            read -p "Continue? [y/N] " confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                echo "Aborted."
                exit 0
            fi
        fi
        run_all_now
    else
        schedule_on_server
    fi
elif [ "$DAY" -ge 2 ] && [ "$DAY" -le 5 ]; then
    echo "It's $(date +%A) $(date +%H:%M). Edition will publish immediately."
    read -p "Continue? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    run_all_now
else
    schedule_on_server
fi
