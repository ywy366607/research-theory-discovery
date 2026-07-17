# Research Theory Discovery Skill

An explicit-invocation skill for open-ended scientific and technical research, plus an optional
enforcement harness so the protocol isn't just prose a model can choose to skip.

This directory is one half of a repo pair: `research-theory-discovery/` (this one, English) and
`research-theory-discovery-zh/` (Chinese). Both share a single `../harness/` directory one level up
-- the harness is language-neutral code and hooks, not translated prose, so it isn't duplicated per
language. If you only cloned this folder in isolation, grab `../harness/` too; the "Read When
Needed" section of `SKILL.md` links into it with relative paths that assume it's a sibling.

## Install (skill only, prompt-level)

Codex:

Copy this folder to one of:

- Repository scope: `.agents/skills/research-theory-discovery/`
- User scope: `~/.agents/skills/research-theory-discovery/`

Restart Codex if it does not appear.

Claude Code:

Copy **both** this folder and `../harness/` as siblings into `~/.claude/skills/` (personal, all
projects) or `<project>/.claude/skills/` (project scope):

```text
~/.claude/skills/research-theory-discovery/   <- this folder
~/.claude/skills/harness/                     <- ../harness/, so SKILL.md's ../harness/... links resolve
```

`harness/` has no `SKILL.md` of its own, so Claude Code won't treat it as a separate skill --
copying it alongside is just what makes the relative references in `SKILL.md` work after install.
Restart the session afterward.

## Invoke

```text
Use the $research-theory-discovery skill to analyze this research problem: ...
```

or choose it through `/skills`. The skill intentionally disables implicit invocation --
`disable-model-invocation: true` in `SKILL.md`'s frontmatter for Claude Code, and
`policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex -- so it does not
interfere with routine coding and debugging.

## Install the harness (optional, enforces the protocol instead of just describing it)

The plain skill is prompt-level: nothing stops a model from skipping subagent review or forgetting
to update the research tree. `../harness/` (see `../harness/README.md`) adds three enforcement
layers on top of a target *research* repository (the repo where you're actually doing the research
this skill guides -- separate from wherever you installed the skill itself):

- **Layer C -- git hooks.** `pre-commit` blocks a commit that stages an invalid `research_tree.json`.
  `commit-msg` blocks pruning a node without `Pruning:`/`Recovery:` trailers in the message. Pure
  stdlib Python + POSIX sh, works with any agent, not Claude-Code-specific.
- **Layer B -- Claude Code hooks.** `PostToolUse` hooks re-validate `research_tree.json` the moment
  it's edited, and nag when a conclusion/report file is written without a corresponding tree change.
  A `Stop` hook blocks ending the turn while the tree is in an invalid state (unreviewed
  "confirmed" nodes, open false-win paths, missing pruning records).
- **Layer A -- a `Workflow` script.** `workflows/research-cycle.js` encodes hypothesize -> necessity
  -> pre-register-prediction (stage `explore`) and audit -> independent-review -> tree-node (stage
  `confirm`) as deterministic multi-agent control flow, so subagent review isn't something the model
  can decide to skip -- the script calls it.

Install into a target research repo:

```bash
python ../harness/scripts/install_harness.py /path/to/target/repo
```

This copies the validators into `<repo>/.research-harness/`, installs the git hooks (chaining onto
any pre-existing hook of the same name rather than clobbering it), and prints the remaining manual
steps: merging `harness/hooks/settings.snippet.json` into the target's `.claude/settings.json`, and
copying `harness/workflows/research-cycle.js` + `harness/agents/claude/*.md` if you want Layer A
available as a workflow there.
Settings.json and the workflow/agent registry aren't touched automatically because they're
user-owned files outside git-hook reach.

See `../harness/README.md` for the full design rationale, what each layer can and can't actually
enforce, and known limitations.

## Contents (this directory)

- `SKILL.md`: core workflow and output contract
- `references/research-protocol.md`: expanded scientific method
- `references/output-schema.md`: reusable ledgers and templates
- `evals/prompts.csv`: trigger and behavior test prompts
- `evals/quick-check.md`: pass/fail checklist for day-to-day spot-checking a single response
- `evals/rubric.md`: 28-point scored rubric for skill-iteration sessions (not per-response use)
- `agents/openai.yaml`: Codex UI metadata and explicit-only policy

## Contents (`../harness/`, shared with the Chinese version)

- `README.md`: harness design rationale, what was tested, known limitations
- `scripts/validate_tree.py`, `check_false_victory.py`, `detect_new_pruning.py`,
  `install_harness.py`, `render_research_tree.py`: harness scripts (Layer C + installer + visualizer)
- `hooks/pre-commit`, `hooks/commit-msg`: git hooks (Layer C)
- `hooks/claude/*.py`, `hooks/settings.snippet.json`: Claude Code hooks (Layer B)
- `workflows/research-cycle.js`: deterministic multi-agent research pipeline (Layer A)
- `agents/claude/*.md`: Claude Code subagent definitions used by the Layer A workflow
