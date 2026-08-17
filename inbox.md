# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---


- [Lea: an open-source Lean 4 theorem-proving agent that keeps mathematicians in the loop](https://www.linkedin.com/posts/chinmay-hegde-8a2a153_today-we-are-releasing-lea-lea-is-a-powerful-ugcPost-7494048440834850816-DcrM/)
  Chinmay Hegde (NYU) and team, announced on LinkedIn around August 14 2026. Lea is an open-source AI agent built on Lean 4 for automated theorem proving and formalization, designed to keep the mathematician in the driver's seat rather than fully automate the proof. It has a full UI with backend visibility, a deliberately minimal architecture, and an Overleaf extension that auto-formalizes LaTeX to Lean while you keep writing the manuscript. Hegde says it has closed and formalized multiple open problems, including a long-standing conjecture in nonlinear elliptic PDEs, and it was built through DARPA's expMath program. Team named: Claudio Silva, Sam Westrick, Eduardo Teixeira, Jaume de Dios Pont, Daniel Arturi, Shashwat Patel, Kevin Gomez. Why it matters for the beat: a concrete tool on the Lean-formalization thread (edition 021's Riemann zeta Lean proof and VibeMathed's Lean-verified count), and the human-in-the-loop framing is the direct counterpoint to full-automation results, close to Gowers's line on where humans keep the edge. Curation agent: verify the claims from the post (LinkedIn, hard to cross-check), the exact release date, the PDE conjecture, and find a public link to Lea itself (repo or site) beyond the LinkedIn post.

- [BioNexus: a scientific reliability layer for agentic biology](https://www.linkedin.com/posts/herry-z-70984b401_bioinformatics-computationalbiology-aiforscience-share-7494430559428063233-rihs/)
  Herry Z., announced on LinkedIn around August 2026 (repo: github.com/HERRY423/BioNexus). BioNexus is an open-source project that wraps a reliability layer around AI coding agents (OpenAI Codex, Claude Code, Cursor) doing bioinformatics. Its premise: knowing how to run an analysis is not the same as knowing when that analysis is scientifically valid. Components include machine-readable Capability Contracts (input semantics, preconditions, refusal conditions, evidence requirements), an EvidenceCard that grades a conclusion as PRELIMINARY, SUPPORTED, ROBUST, REPLICATED, FRAGILE, or ABSTAIN, routing that flags invalid analyses like pseudoreplication or incompatible data representations, an eval suite, and a RunBundle artifact that packages reproducible runs with provenance. Target domains: single-cell omics, spatial transcriptomics, and general bioinformatics workflows. Why it matters for the beat: a concrete attempt to build the verification and trust layer that edition 021's lead argued the field needs, here aimed at AI agents doing biology rather than math, with evidence grading and provenance as the trust signals. It also names the failure mode the cognitive-debt pieces warned about, agents that can run an analysis but cannot judge when it is valid. Curation agent: this is an early open-source project announced on LinkedIn, so check the repo for maturity and whether the claims hold up, and confirm the author and any collaborators.
