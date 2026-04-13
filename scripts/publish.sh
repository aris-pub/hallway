#!/bin/bash
set -euo pipefail

NUMBER="$1"
PADDED=$(printf "%03d" "$NUMBER")
FILE="src/no/${PADDED}.md"
REMOTE="leo@syenite.local"
REMOTE_DIR="/home/leo/aris/hallway"

if [ ! -f "$FILE" ]; then
    echo "Error: $FILE does not exist"
    exit 1
fi

DAY=$(date +%u)   # 1=Monday, 7=Sunday
HOUR=$(date +%H)

run_now() {
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
    echo "Published No. ${PADDED}"
}

schedule_on_server() {
    echo "Scheduling No. ${PADDED} for Monday 9:00 AM on syenite..."

    # Push the reviewed edition first so server has it
    git add "$FILE"
    git commit -m "Review No. ${PADDED}" || true
    git push

    # Create a self-deleting cron entry on syenite
    CRON_CMD="0 9 * * 1 cd ${REMOTE_DIR} && git pull --quiet && PATH=/home/leo/.local/bin:\$PATH just publish ${PADDED} >> /home/leo/.hermes/cron/output/hallway-publish.log 2>&1 && (crontab -l | grep -v 'just publish ${PADDED}' | crontab -)"
    ssh "$REMOTE" "(crontab -l; echo '${CRON_CMD}') | crontab -"

    echo "Scheduled. No. ${PADDED} will publish Monday at 9:00 AM."
}

if [ "$DAY" -eq 1 ]; then
    # Monday
    if [ "$HOUR" -ge 9 ]; then
        if [ "$HOUR" -ge 10 ]; then
            echo "It's Monday $(date +%H:%M). Edition will publish immediately."
            read -p "Continue? [y/N] " confirm
            if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
                echo "Aborted."
                exit 0
            fi
        fi
        run_now
    else
        # Monday before 9am
        schedule_on_server
    fi
elif [ "$DAY" -ge 2 ] && [ "$DAY" -le 5 ]; then
    # Tuesday-Friday: you're late
    echo "It's $(date +%A) $(date +%H:%M). Edition will publish immediately."
    read -p "Continue? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    run_now
else
    # Saturday or Sunday
    schedule_on_server
fi
