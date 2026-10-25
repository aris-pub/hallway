# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---

- [Why choose Google Antigravity for science](https://antigravity.google/use-cases/science/)
  Google product page for Antigravity, its agent-based coding environment, pitched at scientists. The concrete parts: free access to the top usage tier and the Gemini 4 Argon model for 10,000 scientists (by application), a Science plugin with skills, subagents and hooks for querying more than 30 life-science databases (UniProt, PubChem, ChEMBL, the AlphaGenome Atlas), and direct access to AlphaGenome and the AlphaFold Database. The customizations are open source in the google-deepmind/science-skills GitHub repository. The page is mostly marketing, with no named labs, measured results or dates. Fits with Google's Deep Review in No. 030 as part of Google pushing research tools directly to scientists. Curation agent to find the launch date and, if possible, an announcement or news coverage to link alongside or instead of the product page, and to confirm the 10,000-scientist offer and its terms.

- [Citing Less Critically: LLMs Reshape the Rhetoric and Reach of Scientific Citation](https://arxiv.org/abs/2609.01432v1)
  Liu, Chen, Liu, Lu and Murray, arXiv cs.DL, submitted September 1 2026, accepted at EMNLP 2026 main conference per the comments field. Six LLMs were asked to fill in masked citation contexts from 1,746 top NLP conference papers (63k+ contexts, 132k+ citations) and compared against the human citations. The LLMs cite less critically, favor popular and older papers (more so for contrasting citations, where humans pick recent niche work), and draw on authors socially distant from the citing scholar, where humans cite within their coauthor network. Relevant as more writing gets drafted with AI. Note the submission date is older than the usual one-week window, so the curation agent should check whether a newer version or coverage makes it current. Link is to v1 specifically, confirm whether to link the unversioned abstract instead.

- [Major Revision, Minor Accountability: LLMs as Reviewers of Published Articles in Top-Tier Journals](https://arxiv.org/abs/2610.31414)
  Le Guellec, Kim, Bentegeac and Hamroun, arXiv cs.DL, October 22 2026. Four LLMs (two proprietary, two open-weight) reviewed 200 CC BY articles published in 2026 in 20 journals including Nature, Science and Cell. 605 of 800 reviews (75.6%) recommended major revision or rejection for papers that had already been accepted, with individual models ranging from 17.5% to 100%. When one field-specific methodological or statistical flaw was planted in each paper, detection ranged from 17.0% to 60.5% across models. The authors call the output an uneven, framing- and model-dependent signal. Direct counterpoint to Google's Deep Review in No. 030, which reported high error detection on a small benchmark.

- [Distributed AI agents enable comprehensive discovery of biological insights at scale](https://www.biorxiv.org/content/10.64898/2026.10.15.759436v1)
  Sun, Park, DeTomaso and 11 others, bioRxiv, October 16 2026. Thousands of parallel agents each analyze one part of a whole-brain Perturb-seq atlas and their findings are combined into study-wide interpretations, in minutes versus an estimated months of human analysis. Without seeing the source manuscript, the agents reportedly recovered its conclusions and predicted effects of held-out perturbations, and human experts preferred their interpretations in a blinded comparison. Fits the agent-driven analysis thread (TasteVal in No. 030). Curation agent to confirm author affiliations and how the blinded expert comparison was set up before repeating its result.

- [Rewriting Scientific Software with Agents](https://aiatuva.substack.com/p/rewriting-scientific-software-with-agents)
  Stephen D. Turner (UVA School of Data Science), guest post on AI Exchange @ UVA, October 23 2026. Surveys coding agents being used to rewrite scientific tools, mostly bioinformatics into Rust (RustQC, fgumi, fastVEP, FastQC), and describes Claude Code's code-modernization plugin, which checks old and new versions against each other on the same inputs. The RustQC runtime drop from 15 hours to 15 minutes on one dataset is quoted second-hand from an OpenAI field report, so cite it as such. He links Heng Li's "The AI Rewrite Dilemma" on how maintainers feel about rewrites of their tools, which may be worth linking too. Turner was featured in No. 030 (Paired Ends), so check the edition does not lean on him twice in a row without reason.

- [Academic Paper Formatting Skills for Claude](https://github.com/JYU-412/Academic-paper-formatting-skill)
  GitHub repo by user JYU-412, created October 21 2026, MIT license, about 20 stars at the time of inboxing. Three free Claude skills that prepare a manuscript for submission to JAMA Network journals, Gerontological Society of America journals, or 20 sociology and demography journals (ASR, AJS, Demography and others). They check word counts against each journal's own counting rules, check tables and page layout, map the paper to reporting guidelines like STROBE and CONSORT, draft abstracts and statements from the manuscript text (with placeholders instead of invented numbers), run a mock peer review, and draft a response-to-reviewers table. An example of researchers building and sharing their own AI tooling for the submission process, outside publishers and vendors. Relates to the LLM-as-reviewer paper also in this inbox. Curation agent to find who is behind the account (the README does not name the author) and avoid presenting it as more established than a new small repo.
