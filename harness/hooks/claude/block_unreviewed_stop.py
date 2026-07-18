#!/usr/bin/env python3
"""Claude Code Stop hook (Layer B).

Fires when Claude is about to end its turn. Re-validates every research-tree
file in the repo (basename containing "research_tree" and ending in .json --
matches both the literal research_tree.json and descriptive names like
<topic>_research_tree_<date>.json) in --strict mode; if any fails, blocks the
stop (exit 2) so the model must fix the tree -- close open false-win paths,
get independent review on any node marked 'confirmed', or complete a
pruning_record -- before the turn can end.

Respects stop_hook_active to avoid looping: if this hook already forced a
continuation once this turn, it exits 0 on the second pass rather than
fighting Claude Code's own circuit breaker.

Reads the Stop payload from stdin:
  {"cwd": "...", "stop_hook_active": bool, ...}
"""
import json
import re
import subprocess
import sys
from pathlib import Path

TREE_NAME_PATTERN = re.compile(r"research_tree(?!\.schema\.json$).*\.json$", re.IGNORECASE)


def find_repo_root(cwd):
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True
    )
    if r.returncode != 0:
        return None
    return Path(r.stdout.strip())


def find_tree_files(repo_root):
    r = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return [p for p in repo_root.rglob("*.json") if TREE_NAME_PATTERN.search(p.name)]
    return [repo_root / line for line in r.stdout.splitlines() if TREE_NAME_PATTERN.search(Path(line).name)]


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    if payload.get("stop_hook_active"):
        sys.exit(0)

    cwd = payload.get("cwd") or "."
    repo_root = find_repo_root(cwd)
    if repo_root is None:
        sys.exit(0)

    tree_paths = find_tree_files(repo_root)
    if not tree_paths:
        sys.exit(0)  # no tree in this repo -- nothing to enforce

    validator = repo_root / ".research-harness" / "validate_tree.py"
    if not validator.exists():
        sys.exit(0)

    failed = False
    for tree_path in tree_paths:
        if not tree_path.exists():
            continue
        result = subprocess.run(
            [sys.executable, str(validator), str(tree_path), "--strict"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            failed = True
            sys.stderr.write(f"\n--- {tree_path} ---\n")
            sys.stderr.write(result.stderr)

    if failed:
        sys.stderr.write(
            "\nOne or more research-tree files are not in a valid state (see errors above). "
            "Fix them -- close open false-win paths, get independent review on any 'confirmed' "
            "node, or record a proper pruning_record for pruned/noisy/superseded nodes -- "
            "before ending this turn.\n"
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
