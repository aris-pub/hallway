# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---

- [A Claude skill for pre-submission peer review](https://blog.stephenturner.us/p/claude-skill-peer-review-consensus)
  Stephen Turner (bioinformatician, blog post June 30 2026): a DIY Claude Code skill that runs structured pre-submission peer review by issuing targeted searches against Consensus (AI-search-over-papers) and producing a Word-doc report covering background accuracy, missing citations, methods assessment, and recommendations. Cites only published peer-reviewed literature; every search query is logged as an audit trail. Tested on the author's own 2024 PLoS ONE paper. The framing is researcher-side and open-source: "all the resources it cites during a mock peer review come from actual published and peer-reviewed literature... keeping the ecosystem contained means I have fewer third party companies' TOS I need to keep track of." Sharp pair with Google's Paper Assistant Tool (this inbox, arXiv 2606.28277) — same task, different scale and politics: Google's institutional STOC/ICML pilot vs. one bioinformatician building his own with Claude skills and Consensus. Also pairs with Wei et al. (edition 013), Reviewer3 (013), Sakana End-to-End (014), and the AAAI-26 AI review pilot (006). The audit-trail-against-hallucinated-citations angle answers directly to the Wikipedia retraction-lag lead (013) and the Carpenter NISO vocabulary piece on attribution/provenance (013).

- [Towards Automating Scientific Review with Google's Paper Assistant Tool](https://arxiv.org/abs/2606.28277)
  Jayaram, Tyler, Woodruff, Cortes, Matias, Mirrokni, Cohen-Addad (Google, arXiv June 26 2026). Introduces the Paper Assistant Tool (PAT), an agentic framework for deep scientific review and verification that examines manuscripts for theoretical soundness and experimental validity. Reports a 34% improvement over zero-shot recall on mathematical errors via inference scaling, with pilot deployments at STOC and ICML. Frames AI as augmenting not replacing human review. Pairs strongly with Wei et al. ICML peer-review position paper (edition 013), Reviewer3 on bioRxiv (013), Sakana End-to-End paper that cleared the first round of ML workshop peer review (014), and the AAAI-26 AI review pilot (006). Notable that it targets MATHEMATICAL ERRORS specifically — math is the field the NASEM ICOR convening on June 29 conspicuously skipped, so the Google-on-math-review move is filling a coordination gap the institutional reformers are not.
