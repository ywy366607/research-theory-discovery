#!/usr/bin/env python3
"""Claude Code PostToolUse hook (Layer B).

Fires after every Edit/Write. If the touched file looks like a research
conclusion/report artifact (filename matches report|conclusion|findings|
results|summary) and the repo has a research_tree.json that shows no
uncommitted changes, nags the model to update the tree before moving on.

This is advisory, not a hard block: PostToolUse cannot undo the write that
already happened. Its value is interrupting the model's turn with an error
it must respond to, rather than silently letting a conclusion get written
with no corresponding tree update. The filename heuristic is intentionally
loose -- false positives just cost a no-op check, false negatives are the
real risk, so lean toward firing.

Reads the PostToolUse payload from stdin (see validate_tree_hook.py for shape).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

CONCLUSION_PATTERN = re.compile(r"(report|conclusion|finding|result|summary)", re.IGNORECASE)
TREE_BASENAME = "research_tree.json"
TREE_SEARCH_DIRS = [".", "research"]


def find_tree_file(cwd):
    for sub in TREE_SEARCH_DIRS:
        candidate = Path(cwd) / sub / TREE_BASENAME
        if candidate.exists():
            return candidate
    return None


def is_git_repo(cwd):
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd, capture_output=True, text=True
    )
    return r.returncode == 0 and r.stdout.strip() == "true"


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if payload.get("tool_name") not in ("Edit", "Write"):
        sys.exit(0)

    file_path = (payload.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    base = Path(file_path).name
    if base == TREE_BASENAME:
        sys.exit(0)  # the tree edit itself -- validate_tree_hook.py covers this
    if not CONCLUSION_PATTERN.search(base):
        sys.exit(0)  # doesn't look like a conclusion artifact

    cwd = payload.get("cwd") or "."
    if not is_git_repo(cwd):
        sys.exit(0)

    tree_path = find_tree_file(cwd)
    if tree_path is None:
        sys.exit(0)  # no tree in this repo -- nothing to enforce

    status = subprocess.run(
        ["git", "status", "--porcelain", "--", str(tree_path)],
        cwd=cwd, capture_output=True, text=True,
    )
    if status.returncode != 0:
        sys.exit(0)
    if status.stdout.strip():
        sys.exit(0)  # tree already has pending changes -- assume it's being maintained this turn

    print(
        f"NOTE: you just wrote '{file_path}', which looks like a research conclusion or "
        f"report artifact, but '{tree_path}' has no uncommitted changes. If this write "
        f"records a research conclusion, add or update the corresponding research-tree "
        f"node (with prediction, false-win checklist, and review status if it's being "
        f"marked confirmed) before moving on.",
        file=sys.stderr,
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
