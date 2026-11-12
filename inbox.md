# Inbox

Drop links here throughout the week. The agent will include all of them in the next edition.

Format:
```
- [Title](https://url)
  Optional note about why it matters.
```

---

- [AlphaGenome 2: deciphering how cells read DNA to better understand disease](https://deepmind.google/blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/)
  Google DeepMind released AlphaGenome 2, a model whose inputs are a 1-Mb DNA sequence and a target tissue, cell type or cell state, and whose outputs are predictions of gene regulation and variant effects in that setting. It was trained on human and mouse single-cell atlases and bulk functional genomics data, and it can be applied to new single-cell datasets without fine-tuning. It also predicts DNA methylation. The preprint (Gayoso, Mottram, Karollus and colleagues, with Hassabis, Kohli and Avsec as senior authors: https://storage.googleapis.com/deepmind-media/DeepMind.com/Blog/alphagenome-2-deciphering-how-cells-read-dna-to-better-understand-disease/alphagenome-2.pdf) reports that it doubles recall of causal single-cell eQTLs at 90 percent precision compared with earlier models. It also comes with a precomputed atlas of enhancer-gene links and scores for 7 million common variants. Access is through an API for non-commercial research. Found through a LinkedIn post by Amanda Stafford (https://www.linkedin.com/posts/amanda-stafford-phd-059325152_today-we-are-excited-to-launch-alphagenome-share-7526304596818837504-W9Ny/). For the beat, the angle is how researchers get access to it: a closed model behind a non-commercial API with a precomputed atlas, and AlphaGenome is one of the databases in the Antigravity science plugin covered in No. 032. Curation agent to judge whether it fits the beat or is a model release better left to biology outlets, and to confirm the release date and the "30 percent vs 16 percent" causal variant figure from the post against the preprint.

- [PaperRaven: a machine assistant for generating topic-bounded, verified samples of the scientific literature](https://aaronclauset.github.io/paperraven/)
  Aaron Clauset released PaperRaven (v0.2.0, BSD 3-Clause), a literature survey tool run with Claude Code (announcement thread: https://bsky.app/profile/aaronclauset.bsky.social/post/3n24tfuhgbc2i). The researcher describes a topic and picks a few seed papers, and the tool drafts inclusion and exclusion criteria that the researcher refines. In each round Claude proposes papers, ordinary code checks each one against OpenAlex and Crossref and refuses any it cannot find, and a separate model judges each paper against the criteria and writes down why. It searches from the model's recall and the web first, then backward through what the corpus cites, then forward through what cites it. The output is a bibliography, an audit trail of every decision and who made it, and an interactive citation network. In his example (culture and social learning in whales and dolphins), 197 papers were proposed, 5 refused as unfindable, and 158 kept after 42 rounds. For the beat, the angle is the design: the model proposes, deterministic code verifies against a public record, and every decision keeps its reason, which is a concrete answer to hallucinated references. Curation agent to confirm the version, licence and example-run numbers against the project page.
