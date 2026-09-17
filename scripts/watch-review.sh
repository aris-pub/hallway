#!/bin/bash
# Laptop side of the edition handoff.
#
# The curation agent on syenite files a bead labelled ht-review. The existing
# five-minute beads sync brings it here. This script notices it, gets the draft
# rendered and on screen, and starts a review session, so there is nothing to
# ask for and nothing to run by hand.
#
# Run by launchd every 5 minutes. Safe to run when there is nothing to do.
set -euo pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/Users/leo.torres/.local/bin:/usr/bin:/bin"
REPO="/Users/leo.torres/aris/hallway"
PORT=8099
STATE="$REPO/.review-state"
LOG="$REPO/.review.log"

cd "$REPO"

log() { echo "$(date '+%Y-%m-%dT%H:%M:%S') $*" >> "$LOG"; }

# Manual entry: 'just review NNN' re-opens an edition even when already handled.
FORCE=""
if [ "${1:-}" = "--force" ]; then
    FORCE="1"
    NUMBER="${2:-}"
    if [ -z "$NUMBER" ]; then
        echo "usage: watch-review.sh --force NUMBER" >&2
        exit 2
    fi
    BEAD=$(bd list --label ht-review --status open --json 2>/dev/null | python3 -c "
import sys, json, re
try: d = json.load(sys.stdin)
except Exception: sys.exit(0)
issues = d if isinstance(d, list) else d.get('issues', [])
n = int('$NUMBER')
for i in issues:
    m = re.search(r'No\.\s*(\d+)', i.get('title', ''))
    if m and int(m.group(1)) == n:
        print(i.get('id', '')); break
" 2>/dev/null)
fi

# Which edition, if any, is waiting. Take the oldest open ht-review bead so a
# backlog is worked in order rather than newest-first.
if [ -z "$FORCE" ]; then
read -r BEAD NUMBER <<<"$(bd list --label ht-review --status open --json 2>/dev/null | python3 -c "
import sys, json, re
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
issues = d if isinstance(d, list) else d.get('issues', [])
issues.sort(key=lambda i: i.get('created', ''))
for i in issues:
    m = re.search(r'No\.\s*(\d+)', i.get('title', ''))
    if m:
        print(i.get('id', ''), m.group(1))
        break
" 2>/dev/null)"
fi

[ -n "${NUMBER:-}" ] || exit 0

PADDED=$(printf "%03d" "$((10#$NUMBER))")

# One session per edition. Without this every five minutes opens another window.
if [ -z "$FORCE" ] && [ -f "$STATE" ] && grep -qx "$PADDED" "$STATE"; then
    exit 0
fi

if [ -n "${BEAD:-}" ]; then
    CLOSE_LINE="Then close the bead with: bd close $BEAD && bd dolt push"
else
    CLOSE_LINE="There is no open review bead for this edition, so nothing to close."
fi

log "picked up ${BEAD:-no bead} for No. $PADDED"

git pull --quiet --rebase --autostash 2>>"$LOG" || log "git pull failed, continuing with what is on disk"
[ -d node_modules ] || npm install --silent
INCLUDE_DRAFTS=1 npm run build >/dev/null 2>&1

if [ ! -f "_site/no/$PADDED/index.html" ]; then
    log "build produced no page for No. $PADDED, aborting"
    osascript -e "display notification \"No. $PADDED did not render. See .review.log\" with title \"Hallway Track\"" || true
    exit 1
fi

# Serve over HTTP. Opening the file directly gives an unstyled page, because the
# CSS is referenced from the site root.
if ! lsof -i ":$PORT" -sTCP:LISTEN -t >/dev/null 2>&1; then
    (cd "$REPO/_site" && nohup python3 -m http.server "$PORT" >/dev/null 2>&1 &)
    sleep 1
fi

URL="http://localhost:$PORT/no/$PADDED/"
open "$URL"

PROMPT="The Hallway Track No. $PADDED is ready for Leo to review. It is already pulled, built and open in his browser at $URL, served from $REPO/_site.

Read $REPO/src/no/$PADDED.md and $REPO/src/no/$PADDED.post.md so you know what is in the edition, then tell Leo it is on screen and ask what he wants changed. Summarise the edition in two or three lines first: the lead, the section names and the item count.

When he asks for a change, edit the markdown file, run INCLUDE_DRAFTS=1 npm run build, and tell him to refresh. Do not touch the draft: true line, publishing removes it.

When he approves, run: just publish $PADDED
That removes the draft flag, deploys, and either broadcasts now or schedules it on syenite depending on the day and hour.
$CLOSE_LINE
Then remove $PADDED from $STATE so a later rerun is possible.

Do not publish until he says so."

osascript <<OSA || log "could not open iTerm"
tell application "iTerm"
  activate
  create window with default profile
  tell current session of current window
    write text "cd $REPO && claude $(printf '%q' "$PROMPT")"
  end tell
end tell
OSA

echo "$PADDED" >> "$STATE"
osascript -e "display notification \"No. $PADDED is up for review\" with title \"Hallway Track\"" || true
log "review session started for No. $PADDED"
