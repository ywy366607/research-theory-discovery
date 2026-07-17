# research-theory-discovery

An explicit-invocation Claude Code / Codex skill for open-ended scientific and technical research
-- novelty-style hypothesis search, necessity/mathematical-closure search, self-binding falsifiable
predictions, false-win auditing, and theory-experiment conflict diagnosis -- plus an optional
enforcement harness so the protocol is checked, not just described.

- [`research-theory-discovery/`](research-theory-discovery/) -- English skill
- [`research-theory-discovery-zh/`](research-theory-discovery-zh/) -- 中文版
- [`harness/`](harness/) -- shared enforcement harness (git hooks, Claude Code hooks, a
  deterministic multi-agent `Workflow`); language-neutral, used by both versions above

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
8. Maintains a git-tracked research tree (`research_tree.json`) instead of a flat log, so an
   invalidated root can prune a whole dependent subtree without losing history.

The optional `harness/` turns (4)-(8) from instructions a model can skip into things that are
actually gated: git hooks that block an invalid tree or an unrecorded pruning, Claude Code hooks
that re-validate on every edit and block ending a turn in an invalid state, and a `Workflow` script
that runs the hypothesize/predict and audit/review pipeline as deterministic control flow instead of
optional steps a model has to remember to take.

## License

MIT -- see [`LICENSE`](LICENSE).
