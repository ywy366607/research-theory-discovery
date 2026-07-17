# Getting Started

This walks through activating all three harness layers in a **new research project** -- a
different repo from wherever you installed the skill itself. The skill (`SKILL.md`) and the
harness (`harness/`) are two separate installs on purpose: the skill goes into Claude Code's/
Codex's skills directory once; the harness goes into *each* research repo you want it enforcing
in, because it's git hooks and settings scoped to that repo.

If you haven't installed the skill yet, do that first -- see the "Install" section in
[`research-theory-discovery/README.md`](research-theory-discovery/README.md) (English) or
[`research-theory-discovery-zh/README.zh.md`](research-theory-discovery-zh/README.zh.md) (中文).
Everything below assumes the skill is already installed and this repo is cloned somewhere on disk
(call that path `$HARNESS_SRC`, e.g. `~/research-theory-discovery`).

## 1. Layer C -- git hooks (does the actual work; do this first)

In your research project (must already be a git repo -- `git init` if it isn't):

```bash
python $HARNESS_SRC/harness/scripts/install_harness.py /path/to/your/research/repo
```

This alone gets you a real, working gate: a commit that stages a structurally invalid
`research_tree.json`, or one that prunes a node without `Pruning:`/`Recovery:` trailers in the
commit message, will be rejected. Nothing else below is required for Layer C to work -- Layers A
and B are optional strengthening on top of it.

Verify it's live:

```bash
cd /path/to/your/research/repo
ls .git/hooks/pre-commit .git/hooks/commit-msg   # should exist and be executable
ls .research-harness/                             # validate_tree.py etc. should be here
```

## 2. Layer B -- Claude Code hooks (optional, Claude-Code-specific)

Step 1 already copied the hook scripts to `.research-harness/hooks/*.py`. What's left is
registering them in Claude Code's settings so they actually fire on `Edit`/`Write`/`Stop`.

Open (or create) `.claude/settings.json` in your research repo and merge in the contents of
`$HARNESS_SRC/harness/hooks/settings.snippet.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "python .research-harness/hooks/validate_tree_hook.py", "timeout": 15}]},
      {"matcher": "Edit|Write", "hooks": [{"type": "command", "command": "python .research-harness/hooks/check_tree_updated.py", "timeout": 15}]}
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "python .research-harness/hooks/block_unreviewed_stop.py", "timeout": 15}]}
    ]
  }
}
```

If `.claude/settings.json` already has other `hooks` entries (from other skills/tooling), merge
arrays -- don't overwrite the file. If your PATH doesn't resolve `python` to a working interpreter
(Windows machines sometimes only have `python3` or `py`), edit the `command` strings accordingly.

Restart the Claude Code session in that project for the settings change to take effect.

## 3. Layer A -- the deterministic Workflow (optional, biggest lift)

Only worth doing if you actually want to invoke the hypothesize/predict/audit/review pipeline as a
`Workflow` rather than freeform conversation. Copy:

```bash
mkdir -p /path/to/your/research/repo/.claude/workflows
cp $HARNESS_SRC/harness/workflows/research-cycle.js /path/to/your/research/repo/.claude/workflows/

# optional -- only needed for args.useAgentTypes: true (real per-role tool restriction)
mkdir -p /path/to/your/research/repo/.claude/agents
cp $HARNESS_SRC/harness/agents/claude/*.md /path/to/your/research/repo/.claude/agents/
```

Then, in a Claude Code session in that project, invoke it via the `Workflow` tool with
`scriptPath` pointing at `.claude/workflows/research-cycle.js`, or by name once discovery picks it
up. Two stages:

```jsonc
// stage "explore": problem -> hypotheses -> necessity classification -> pre-registered predictions
{"stage": "explore", "problem": "<your research question>", "hypothesisCount": 3}

// stage "confirm": claim + evidence + earlier prediction -> false-win audit -> independent review -> tree node
{"stage": "confirm", "claim": "...", "evidence": "...", "prediction": {"id": "P-...", "registered_before_result": true, "expected_observation": "...", "falsifying_observation": "..."}}
```

`confirm` returns a node object (with `status: 'confirmed'` only if every false-win path closed
**and** the reviewer approved); you write that node into `research_tree.json` yourself, which Layer
B/C then validate.

## 4. Create your first `research_tree.json`

Put this at the root of your research repo (or wherever your reports live -- Layer B's
`check_tree_updated.py` also checks a `research/` subdirectory):

```json
{
  "title": "My Research Tree",
  "nodes": [
    {
      "id": "N001",
      "parent": null,
      "title": "Initial hypothesis",
      "status": "active",
      "motivation": "Why this node exists",
      "action": "What changed or was tested",
      "conclusion": "What was learned so far",
      "invalidation": "What observation would kill this node",
      "confidence": "D"
    }
  ]
}
```

`../harness/scripts/validate_tree.py` will reject nodes missing required fields, and will refuse
`status: "confirmed"` unless the node has a pre-registered prediction, a fully-closed false-win
checklist, and an independent (non-self) `review.conclusion_reviewer.status` of `accepted` or
`approved`. See `research-theory-discovery/references/output-schema.md` for the full node schema
and `harness/scripts/research_tree.schema.json` for the machine-readable version.

## 5. Sanity-check the install

```bash
cd /path/to/your/research/repo
git add research_tree.json
git commit -m "add initial research tree"   # should succeed -- status: active has no gates
```

Then try breaking it on purpose to confirm the gate is real:

```bash
python -c "
import json
d = json.load(open('research_tree.json'))
d['nodes'][0]['status'] = 'confirmed'   # no prediction/audit/review -- should get rejected
json.dump(d, open('research_tree.json', 'w'))
"
git add research_tree.json
git commit -m "should be blocked"   # expect: pre-commit rejects this
```

If that commit is rejected with a validation error, Layer C is working. Revert the test edit
(`git checkout -- research_tree.json`) before doing real work.

## Troubleshooting

- **Hook doesn't fire on commit**: confirm `.git/hooks/pre-commit` is executable
  (`chmod +x .git/hooks/pre-commit` on Linux/macOS; not usually needed on Windows/Git Bash).
- **`python: command not found` inside the hook**: the git hooks auto-probe
  `python3`/`python`/`py` and use whichever works, but Layer B's `settings.snippet.json` commands
  don't -- edit those manually if `python` isn't on your PATH.
- **Claude Code hooks don't seem to run**: check `.claude/settings.json` is valid JSON and that you
  restarted the session after editing it.
- **Workflow says the custom `agentType` isn't found**: this is expected with the default (inline
  role prompts) mode -- see `harness/README.md`'s "What was tested" section, point 3. Don't set
  `useAgentTypes: true` unless you've actually copied `agents/claude/*.md` into that project's
  `.claude/agents/` and confirmed Claude Code picked them up.
