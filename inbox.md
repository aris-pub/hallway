# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---

- [AI Assistant Tool QED Scores bioRxiv Preprint Quality](https://www.the-scientist.com/can-ai-tools-spot-great-science-before-reviewers-do-74677)
  The Scientist covering QED Science's June 24 2026 launch (globenewswire.com/news-release/2026/06/24/3317037): an AI-based quality metric that scored all 57,455 bioRxiv preprints from May 2025 to April 2026 on originality and validity, blinded to author, institution, and journal. Claims AUC 0.867 against a 925-paper expert-labeled test set. Published "The 1%" — the 574 top-scoring preprints — as its first public output. Angela Andersen (LinkedIn, 2026-07-05, linkedin.com/posts/angela-andersen-1572634_biorxiv-posted-57455-life-science-preprints-share-7479867571312414720-1Uex) raises the sharpest critique: the top 1% still concentrates at prestigious well-funded institutions with bigger papers and richer figures. Is QED measuring quality or measuring resources? Pairs with the AI-in-peer-review thread that ran through edition 015 (Google PAT, Turner's DIY Claude skill, Frontiers policy piece, NeurIPS hidden prompts) and extends it upstream from "AI reviews the paper" to "AI ranks the paper before anyone reviews it." Also pairs with Hao et al.'s 41.3M-paper productivity/monoculture study in edition 014 (Nature 649, 1237): if AI-augmented researchers already publish 3x more and receive 5x citations, and AI now ranks the whole preprint corpus by algorithmic quality, the compounding of institutional advantage is straightforward to argue.

- [OpenScience: the open-source AI workbench for scientific research](https://www.openscience.sh/)
  Synthetic Sciences (a US AI-for-science lab, syntheticsciences.ai) shipped OpenScience on 2026-07-03 (github.com/synthetic-sciences/openscience, Apache-2.0, ~880 stars and 115 forks within four days). Browser-based, model-agnostic, bring-your-own-key, local-first. Given a goal, it runs the full research loop like an AI collaborator: reads the relevant papers, forms a hypothesis, writes and runs code, runs experiments on real compute, queries scientific databases, and writes up the result (ML, biology, physics, chemistry). Explicitly positioned as the open-source alternative to Anthropic's Claude Science. The productized, open, fast-adopting version of the agentic-AI-scientist thread this newsletter has covered in the recent AI-Scientist cluster (Sakana's end-to-end AI Scientist, Jimenez et al.'s Denario, AI2's Asta). The angle worth drawing: the same loop those papers demonstrated is now a one-click open-source desktop tool with real traction, and the open-vs-closed split (OpenScience vs Claude Science) is the next axis. Every tool like this that ships widens the gap between how fast research gets produced and how fast anyone can verify it.
