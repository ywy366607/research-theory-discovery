#!/usr/bin/env python3
"""Claude Code PostToolUse hook (Layer B).

Fires after every Edit/Write. If the touched file is research_tree.json,
re-validates it immediately and reports failures back to the model via
exit code 2. PostToolUse cannot undo the edit that already happened, but
the nonzero exit surfaces the validator's error text to Claude as tool
feedback, which in practice makes it fix the tree in the same turn instead
of drifting away with an invalid tree.

Reads the PostToolUse payload from stdin:
  {"cwd": "...", "tool_name": "Edit", "tool_input": {"file_path": "..."}, ...}

Expects the target repo to have been set up with install_harness.py, which
places validate_tree.py at <repo_root>/.research-harness/validate_tree.py.
"""
import json
import subprocess
import sys
from pathlib import Path


def find_repo_root(cwd):
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=cwd, capture_output=True, text=True
    )
    if r.returncode != 0:
        return None
    return Path(r.stdout.strip())


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)  # malformed input -- fail open, don't block on our own bug

    if payload.get("tool_name") not in ("Edit", "Write"):
        sys.exit(0)

    file_path = (payload.get("tool_input") or {}).get("file_path", "")
    if not file_path or Path(file_path).name != "research_tree.json":
        sys.exit(0)

    cwd = payload.get("cwd") or "."
    repo_root = find_repo_root(cwd)
    if repo_root is None:
        sys.exit(0)

    validator = repo_root / ".research-harness" / "validate_tree.py"
    if not validator.exists():
        sys.exit(0)  # harness not installed in this repo -- nothing to enforce

    result = subprocess.run(
        [sys.executable, str(validator), file_path, "--strict"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.stderr.write(
            "\nresearch_tree.json fails validation (see errors above). "
            "Fix it now before continuing.\n"
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
