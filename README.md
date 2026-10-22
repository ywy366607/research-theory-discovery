# research-theory-discovery

An explicit-invocation Claude Code / Codex skill for open-ended scientific and technical research,
organized as an **ascent-descent loop**: ascend by induction from phenomena to mechanisms, extension
axioms and the minimal general axioms that generate the problem; descend by deduction from corrected
axioms to theorems, algorithms and tests that produce new phenomena; iterate. Novelty-style
hypothesis search, necessity/mathematical-closure search, self-binding falsifiable predictions,
false-win auditing and layer-by-layer conflict diagnosis live inside that loop -- plus an
enforcement harness, including Lean, so the protocol is checked, not just described.

- [`research-theory-discovery/`](research-theory-discovery/) -- English skill
- [`research-theory-discovery-zh/`](research-theory-discovery-zh/) -- 中文版
- [`harness/`](harness/) -- shared enforcement harness (git hooks, Claude Code hooks, a
  deterministic multi-agent `Workflow`, and a Lean audit layer); language-neutral, used by both
  versions above

Start with whichever language directory's `README.md` matches you; both link into `harness/` for
the enforcement layer. `harness/README.md` documents the harness design and what was actually
tested (not just designed) and its known limitations.

**New to this repo? Read [`GETTING-STARTED.md`](GETTING-STARTED.md)** -- it's a step-by-step
walkthrough of activating all three harness layers in a real research project, including the exact
commands to verify the git hook actually blocks a bad commit.

## Why this exists

Most "research assistant" prompting either rubber-stamps whatever mechanism the user proposes, or
produces generic praise for any positive-looking result. This skill instead:

1. Quarantines the user's proposed mechanism and reconstructs the problem independently first.
2. Runs novelty-style hypothesis search for orthogonal (not paraphrased) competing explanations.
3. Separates *possible*, *useful*, and *necessary* -- and refuses to promote a claim to necessary
   without a derivation.
4. Requires predictions to be pre-registered before results, and falsifiable.
5. Runs a canonical false-win checklist (capacity, budget, leakage, baseline bypass,
   reachability-vs-discovery, and more) before crediting a positive result to a mechanism.
6. Treats theory-experiment conflicts as testing a whole theory package (core theory + auxiliary
   assumptions + implementation + optimization + measurement + baseline relation), not just "was
   the idea right or wrong."
7. Routes hypothesis support, experiment approval, and conclusion review through separate,
   non-self-approving review surfaces.
8. Puts every claim in a layer (general axiom, extension axiom, theorem, algorithm, test),
   accepts each layer by its own standard (discussion + independence/consistency, held-out data,
   Lean proof, reference implementation, pre-registered test), and diagnoses failures bottom-up:
   algorithm -> extension axiom -> derivation -> general axiom (only with a no-go theorem).
9. Maintains a git-tracked research tree (`research_tree.json`) instead of a flat log, so an
   invalidated root can prune a whole dependent subtree without losing history.

The optional `harness/` turns (4)-(8) from instructions a model can skip into things that are
actually gated: git hooks that block an invalid tree or an unrecorded pruning, Claude Code hooks
that re-validate on every edit and block ending a turn in an invalid state, and a `Workflow` script
that runs the hypothesize/predict and audit/review pipeline as deterministic control flow instead of
optional steps a model has to remember to take.

## License

MIT -- see [`LICENSE`](LICENSE).
