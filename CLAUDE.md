# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:b9766037 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

## Landing the Plane (Session Completion)

**When ending a work session**, you MUST complete ALL steps below. Beads must always be synced. Whether the repo's own files get pushed depends on step 4.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **SYNC** - What this means depends on whether beads live in git.

   Check with `bd config get no-git-ops`.

   **Stealth mode (`no-git-ops: true`, which is the current setting in every Aris repo).**
   Beads sync through Dolt, not git, so push the beads and leave the repo's own files to
   the normal commit rule:
   ```bash
   bd dolt pull && bd dolt push
   ```
   Repo files follow the global rule in `~/.claude/CLAUDE.md`: say when you are ready to
   commit, and commit only when told.

   **Beads in git (`no-git-ops: false`).** Beads data is part of the working tree, so
   leaving it uncommitted strands it. Push without asking:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - Beads synced. Repo files committed and pushed only if beads are in git, or
   if the user asked for it
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- `bd dolt push` is never optional. Beads left unsynced are lost to the next session
- When beads are in git, work is not complete until `git push` succeeds, and you push
  rather than announcing you are ready to
- When beads are in stealth, the global commit rule applies: ready to commit is something
  you say, committing is something the user asks for
- If a push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## Weekly Workflow

1. **Saturday night** - Cron runs `just agent` on syenite. Writes draft, commits, pushes, emails notification to hello@aris.pub.
2. **Sunday** - `git pull` on laptop. Review `src/no/NNN.md`, edit content, remove `draft: true` from frontmatter.
3. **Monday** - `just publish NNN` (builds og:images, builds site, deploys to Netlify, emails subscribers).
4. **Monday** - Post on Bluesky and LinkedIn. Lead with strongest single link, not "new edition out."
5. **After publishing** - Remind Leo to reach out to one person featured in this edition: a genuine note (email or Bluesky) telling them their work was featured. Suggest who, offer to draft it, but Leo sends it. This is the main audience-growth lever (it builds peer relationships and opens cross-recommendations), not a pitch.

## Commands

```bash
just publish NNN   # Build, deploy, email subscribers
just agent         # Run curation agent (normally via cron)
just agent-dry     # Preview what agent would do
just test          # Run pytest
just dev           # Local dev server
```

## Architecture

- **Site**: 11ty (Eleventy) static site, Netlify hosting, hallway.aris.pub
- **Agent**: Python script using Claude Code CLI for web search + curation
- **Newsletter**: Resend (contacts, segments, broadcasts). Netlify Function for signups.
- **Analytics**: Umami Cloud (free tier)
- **Sources**: Defined in sources.md (28 sources)
- **Prompt**: Agent prompt in agent/prompt.txt
- **Template**: Edition format in agent/edition-template.md
- **Cron**: Runs on syenite (home server), Saturday night

## Conventions

- Editions are called "editions", not "issues" or "numbers"
- No em dashes anywhere
- Edition URLs: /no/001/, /no/002/, etc.
- Footer: "Part of The Aris Program" (never Leo's name)
- Voice: researcher to researcher, no hype, no excitement
- No punchy writing anywhere in the newsletter, the social posts, or the site copy. No paired short
  sentences for rhythm ("The use is real. The record does not reflect it."), no scene-setting openers
  ("Two data points arrived this week from opposite directions"), no dramatic one-liners or reversals.
  Leo is a scientist writing to scientists, not a journalist. Ordinary full sentences, content first.
- `draft: true` in frontmatter prevents rendering and collection inclusion
