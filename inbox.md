# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---

- [Self-Revising Discovery Systems for Science: A Categorical Framework for Agentic Artificial Intelligence](https://arxiv.org/abs/2606.01444)
  Wang & Buehler (MIT, arXiv May 31 2026): category-theory framework that formally distinguishes retrieval, search, and discovery for AI-driven materials science. Discovery is defined as "verified regime transition" where old artifacts are preserved via left Kan extension. Demonstrated with Builder/Breaker (protein mechanics) and CategoryScienceClaw (knowledge-computation graph). On-beat: formal foundations for the AI-scientist governance/capability question raised in editions 010-011. Replaces a LinkedIn post by Raphaël Mansuy.

- https://www.nature.com/articles/s41562-026-02492-7
  Nature Human Behaviour, June 2026 — agent should WebFetch the article to identify title and findings (article too recent to be in search index).

- [ErdosBench: A Research-Mathematics Benchmark Built from Synthetic Erdős-Style Problems](https://ulam.ai/research/ErdosBench.pdf)
  Chojecki et al. (ulam.ai, June 2026): 226 problems derived from open Erdős problems, 14 public, evaluates frontier models on research-level math reasoning — "finding obstructions, partial results, computational heuristics." Motivated by standard math benchmarks becoming saturated. Pairs with the sum-product disproof (edition 011) and OpenAI Erdős unit-distance disproof (edition 008) as the AI-for-math evaluation infrastructure. GitHub: https://github.com/ulamai/erdosbench. Replaces a LinkedIn post by Przemek Chojecki.

- [The social consequences of AI delegation](https://arxiv.org/abs/2606.11058)
  Ferraz de Arruda & Moreno (arXiv, June 9 2026): reframes the LLMs-in-research question from "can LLMs replace human study participants" to "are humans starting to use LLMs as surrogates for their own deliberation" — in healthcare, legal, financial, education, and personal-guidance domains. Argues LLMs should be treated as social entities influencing choices, norms, and group interactions. Connects to authorship/accountability threads (009-011) by shifting the unit of analysis from authorship to deliberation.

- [The Leiden Declaration on Artificial Intelligence and Mathematics](https://leidendeclaration.ai/)
  June 2026: 16 mathematicians (led by Jim Portegies, including Ursula Martin, Rodrigo Ochigame, Michael Harris) issue a community statement on protecting proof, attribution, and insight from AI risks. Endorsed by the International Mathematical Union; signed by Fields Medalist Peter Scholze and 130+ others. Concerns: reliability of AI-generated proofs, attribution when proprietary models are used, effects on peer review. Recommendations for researchers, societies, funders, policymakers. Portegies presenting at ICM July 2026. Strong on-beat anchor — direct community response to the AI-disproved-conjectures thread (sum-product/Erdős coverage in 008+011). Primary source linked; non-paywall alternative to the NYT article.

- [Homogenizing effect of large language models (LLMs) on creative diversity: An empirical comparison of human and ChatGPT writing](https://www.sciencedirect.com/science/article/pii/S294988212500091X)
  Computers in Human Behavior: Artificial Humans (Elsevier, open-access), 2025. Empirical study finding LLM-assisted writing narrows creative diversity vs. human-only writing. Strong pair with Tang & Yang's "AI Research Agents Narrow Scientific Exploration" from edition 010 — same narrowing pattern surfacing on both the writing side (humans-with-LLMs) and the agent side (autonomous AI scientists). The monoculture concern is now empirically attested at two layers of the pipeline.

- [Building Scholar-Ready AI: A Conversation with Todd Toler](https://scholarlykitchen.sspnet.org/2026/06/10/building-scholar-ready-ai/)
  Hinchliffe interviewing Todd Toler (Scholarly Kitchen, June 10 2026). Toler joins Ithaka S+R as Practice Lead for AI in Scholarly Communication; argues the central problem is preserving a "trustworthy chain of custody for AI-mediated scholarly retrieval." When RAG systems chunk articles for retrieval, provenance, peer review status, and citation relationships get detached from the content. Recommendations: shared metadata standards that travel with retrieved chunks; extended PID infrastructure for authenticity verification; behavioral contracts between AI agents and sources; shared evaluation frameworks; aligning subscription-access incentives with scholarly integrity. Pairs directly with the Scholarly Kitchen AI-search metadata story (edition 010) — that piece named the gap, this one names the infrastructure work. Also pairs with Fable/Mythos: capability is rising, the retrieval infrastructure underneath isn't.

- [Claude Fable 5 and Claude Mythos 5](https://www.anthropic.com/news/claude-fable-5-mythos-5)
  Anthropic, June 9 2026. First **general-purpose** flagship model positioned as "also good for science" rather than as a science-specific product. Two prior frontier-lab research-capability releases this spring were both specialized: GPT-Rosalind (OpenAI, April 16) is a domain-specific life-sciences model for qualified enterprise customers; Gemini for Science (Google, May 19) is a research-tools suite on top of Gemini. Fable/Mythos's announcement bundles scientific research alongside coding, vision, and knowledge work as headline claims on the flagship release itself — a phase transition where research capability becomes a default-expected feature of any frontier model rather than a separately branded product. Specific Mythos 5 claims: "first model to consistently produce novel, compelling scientific hypotheses"; ~80% researcher preference vs. Opus-class baseline in molecular biology; one E. coli protein-mechanism hypothesis **corroborated by an independent lab**; ~10× speedup in drug design; week-long autonomous genomics across 138 species with a custom ML model **beating a Science-published baseline at 100× smaller**. Fable 5 is the public version. Pair with the Leiden Declaration (this inbox) and the Tang-Yang/AutoScientists governance threads (010) for a "capability is now default; now what" arc in edition 012.

- [We Can Create the Future of Science Right Now](https://goodscience.substack.com/p/we-can-create-the-future-of-science)
  Paul Litvak (Robyn Dawes Institute, UC Berkeley), guest article on Good Science (Stuart Buck), June 8 2026. Inventories existing AI tools across six layers of a hypothetical "living evidence synthesis" system that would replace PDF-based publishing: document understanding (GROBID, Docling, Mistral, Gemini), hypothesis extraction (Trialstreamer, RobotReviewer LIVE, PaperQA2, OpenEval), forensic audit (Proofig, ImageTwin, GRIM, SPRITE), methodological review (Refine.ink, Reviewer3, Q.E.D. Science, ReviewerZero.ai), reproducibility checks (Institute for Replication, CORE-Bench, PaperBench), and synthesis (OpenAlex, Retraction Watch, Scite, Living Evidence Network). OpenEval reports 81% agreement with human peer review across 2,487 papers using Claude Sonnet 4.5. Proposes a behavioral RCT replication-prediction pilot. Funder list: Sloan, Coefficient Giving, Astera, Institute for Progress, NIH ORR.
