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

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## Weekly Workflow

1. **Saturday night** - Cron runs `just agent` on syenite. Writes draft, commits, pushes, emails notification to hello@aris.pub.
2. **Sunday** - `git pull` on laptop. Review `src/no/NNN.md`, edit content, remove `draft: true` from frontmatter.
3. **Monday** - `just publish NNN` (builds og:images, builds site, deploys to Netlify, emails subscribers).
4. **Monday** - Post on Bluesky and LinkedIn. Lead with strongest single link, not "new edition out."

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
- `draft: true` in frontmatter prevents rendering and collection inclusion
