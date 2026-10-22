# Research-Theory-Discovery Harness

The `research-theory-discovery` skill is prompt-level: it tells a model to maintain a research
tree, pre-register predictions, close false-win paths, and route conclusions through independent
review. Nothing stops a model from skipping any of that. This harness adds three enforcement
layers on top of a target research repository so the protocol is checked, not just described.

## Layers

### Layer C -- git hooks (`hooks/pre-commit`, `hooks/commit-msg`)

Pure POSIX sh + stdlib Python, installed into `<repo>/.git/hooks/` by `scripts/install_harness.py`.
Independent of any particular coding agent -- a human, Claude Code, Codex, or a CI job all go
through the same gate.

- `pre-commit`: if `research_tree.json` is staged, validates the **staged** content (not the
  working tree) against `scripts/validate_tree.py --strict` and blocks the commit on failure.
- `commit-msg`: if this commit newly transitions a node's status into `pruned`/`noisy`/
  `superseded` (diffed against `HEAD`'s version of the tree via `scripts/detect_new_pruning.py`),
  requires `Pruning:` and `Recovery:` lines in the commit message.

Verified: blocks a structurally invalid tree, blocks a pruning commit missing the required
trailers, allows a valid commit with proper trailers, and doesn't false-positive on commits that
don't touch the tree. See "What was tested" below for the actual commands run.

**Limitation:** only fires on `git commit`. A tree edited but never committed, or committed with
`--no-verify`, is not caught by this layer.

### Layer B -- Claude Code hooks (`hooks/claude/*.py`, `hooks/settings.snippet.json`)

Claude-Code-specific. Registered via `PostToolUse`/`Stop` entries merged into the target project's
`.claude/settings.json` (not auto-merged -- settings.json is user-owned; `install_harness.py`
copies the hook scripts and prints the snippet to review).

- `validate_tree_hook.py` (`PostToolUse`, matches `Edit|Write`): if the touched file is
  `research_tree.json`, re-validates it immediately and exits 2 (blocking, reported back to the
  model as tool feedback) on failure.
- `check_tree_updated.py` (`PostToolUse`, matches `Edit|Write`): if the touched file looks like a
  conclusion/report artifact (filename matches `report|conclusion|finding|result|summary`) and
  `research_tree.json` has no uncommitted changes, nags the model to update the tree. Advisory, not
  a hard block -- `PostToolUse` fires after the write already happened and cannot undo it.
- `block_unreviewed_stop.py` (`Stop`): re-validates `research_tree.json` before the turn is allowed
  to end; blocks (with the circuit-breaker `stop_hook_active` check so it can't loop forever) if the
  tree has an invalid state -- e.g. a `confirmed` node with no independent review, or an open
  false-win path.

Verified: all three scripts tested directly with synthetic stdin payloads matching the documented
`PreToolUse`/`PostToolUse`/`Stop` JSON contract (`cwd`, `tool_name`, `tool_input.file_path`,
`stop_hook_active`), covering pass/block/ignore/circuit-breaker cases for each. See "What was
tested" below.

**Limitation:** `PostToolUse` cannot undo an action that already happened -- it can only make the
model's next turn start with an error to react to. If the model ignores the error and moves on
anyway, nothing below this layer stops it except Layer C at commit time. The interpreter invoked by
the `command` in `settings.snippet.json` is hardcoded to `python`; if that doesn't resolve on your
PATH, edit the snippet to `python3` or `py`.

### Layer A -- deterministic workflow (`workflows/research-cycle.js`, `agents/claude/*.md`)

The only layer that removes the choice to skip a step, rather than catching it after the fact.
Instead of asking a model to remember to route hypotheses/predictions/conclusions through separate
review surfaces, the protocol is control flow in a `Workflow` script:

- `args.stage === 'explore'`: `problem` -> hypothesis-generator -> (parallel) necessity-auditor per
  hypothesis -> (pipeline) predictor per hypothesis. The predictor stage structurally cannot see an
  experiment result, because `explore` never accepts one as input -- prediction and result are two
  different call graphs, not just an instruction not to peek.
- `args.stage === 'confirm'`: `claim` + `evidence` + the earlier `prediction` -> false-victory-
  auditor -> independent-reviewer -> a `research_tree.json`-shaped node object, with
  `status: 'confirmed'` only if every false-win path closed **and** the reviewer approved.

- `args.stage === 'plan'`: `objective` + selected `hypothesis` + earlier `prediction` + proposed
  `experiment` -> independent experiment-planner -> deterministic decision-contract checks.
  The plan states the retained baseline, feasibility, claim scope, target/proxy relationship,
  budget/evaluation, stopping condition, and gain/no-gain/ambiguous criteria and actions.
  Redundant measurements are rejected, with a reasoned exception for necessary acceptance.
  Returns `approved_to_register`; `execution_authorized` is always false. Existing human
  authorization and resource constraints govern execution separately.

The discovery role now asks for candidates that open a new feasible space, or a reason to retain
the existing space. Bounded design-intuition exploration is allowed without invented numerical
predictions. Use optional `targetContract` in explore for objective, metric/evaluation, baseline,
and constraints; older calls default the objective to `problem`. Confirm additionally requires
`prediction.registered_before_result === true` and affirmative evidence for each closed path.
These checks enforce declared contracts; scientific sufficiency still needs independent judgment.

Subagent role instructions (`agents/claude/*.md`) are also embedded inline in the workflow script
by default (see `ROLE_*` constants), so the pipeline runs without depending on the target project
having separately registered those files as subagent types -- this was a real finding from testing
(below), not a hypothetical. Pass `args.useAgentTypes: true` to use the registered `agentType`
instead once `agents/claude/*.md` are actually installed and picked up; that mode gets you real
per-role tool restrictions (e.g. `independent-reviewer` has no `Edit`/`Write` access and cannot
alter the tree itself, only return a verdict), which the inline-prompt default cannot enforce -- in
inline mode every call is the same underlying agent with a role prompt, not a permission boundary.

The workflow returns data; it does not write `research_tree.json` itself. The caller writes the
returned node into the tree, which Layers B/C then validate.

## What was tested

The original installation tests below preceded the decision-contract extension:

The extension has deterministic contract tests in `scripts/test_research_cycle.mjs`:
`node scripts/test_research_cycle.mjs`. They execute the workflow with mocked agent/runtime
responses, exercising explore/plan/confirm routing and approval gates. They test control flow,
not real agent reasoning or a live Claude Workflow run. Re-test the live runtime when installing
the extension in a target project.

- Layer C: a scratch git repo with the hooks installed via `install_harness.py`. Confirmed: a
  structurally invalid tree is blocked at `pre-commit`; a valid tree with an unannounced pruning is
  blocked at `commit-msg`; the same tree with `Pruning:`/`Recovery:` trailers commits cleanly; a
  regression re-check of the invalid tree still blocks after a portability fix (see below).
- Layer B: all three hook scripts invoked directly with synthetic JSON payloads matching the
  `PostToolUse`/`Stop` stdin contract -- 9 cases covering pass, block, ignore-irrelevant-file, and
  the `stop_hook_active` circuit breaker.
- Layer A: run via the `Workflow` tool against a real (small) research problem.

Two real bugs were found and fixed by this testing, not by inspection:

1. **`python3` on Windows can be a Microsoft Store alias stub that exits nonzero without running
   anything**, even though `command -v python3` finds it. The git hooks now probe
   `python3`/`python`/`py` at run time and use whichever actually executes, instead of hardcoding
   `python3`.
2. **`Workflow`'s `args` parameter arrived inside the script as a JSON string, not a parsed object**,
   even though it was passed as a real object in the tool call. `research-cycle.js` now defensively
   parses `args` if it's a string before reading any field off it.
3. Custom subagent types placed in `~/.claude/agents/*.md` were not resolved as valid `agentType`
   values for `Workflow`'s `agent()` calls in the tested session, even after a fresh (non-resumed)
   workflow run. This is why Layer A defaults to inline role prompts instead of `agentType` -- see
   above.

## Installing into a target research repo

See [`../GETTING-STARTED.md`](../GETTING-STARTED.md) for a full step-by-step walkthrough (all three
layers, plus commands to verify the gate actually blocks a bad commit). Short version:

```bash
python scripts/install_harness.py /path/to/target/repo
```

Copies the Layer C/B scripts into `<repo>/.research-harness/`, installs the git hooks (chaining
onto any pre-existing hook of the same name), and prints what's left to do manually: merge
`hooks/settings.snippet.json` into `<repo>/.claude/settings.json`, and copy
`workflows/research-cycle.js` + `agents/claude/*.md` into `<repo>/.claude/workflows/` and
`<repo>/.claude/agents/` if you want Layer A available as a workflow there.

## Portability: Claude Code vs. Codex

Layer C is git-level and works under any agent, including Codex -- a git hook fires on `git commit`
regardless of what produced the commit. Layers A and B are Claude-Code-specific: they depend on
Claude Code's `PostToolUse`/`Stop` hook contract (exit-code blocking, JSON-over-stdin) and the
`Workflow` tool's deterministic `agent()`/`pipeline()`/`parallel()` orchestration. Whether Codex CLI
has equivalent primitives (a hook system with blocking semantics, a scripted multi-agent
orchestration mode) was not verified here and changes quickly -- check Codex's current docs before
assuming parity. If it doesn't, the fallback for a Codex-driven repo is `AGENTS.md` instructions
plus Layer C as the hard backstop, which is a weaker guarantee than Layer A/B's before-the-fact
enforcement.
