#!/usr/bin/env python3
"""Install the research-theory-discovery harness (Layer C: git-level
enforcement) into a target research repository.

What it does:
  1. Copies validate_tree.py, check_false_victory.py, detect_new_pruning.py,
     and research_tree.schema.json into <target>/.research-harness/
     (this is what the git hooks call, so they keep working even if the
     skill package itself isn't installed in that repo).
  2. Copies hooks/pre-commit and hooks/commit-msg into <target>/.git/hooks/,
     chaining onto any existing hook of the same name instead of clobbering it.
  3. Prints (does not write) the settings.json snippet for Layer B, and the
     workflow/agent file list for Layer A, so you can review before adding
     them.

This script only touches .git/hooks/ and a new .research-harness/ directory.
It never edits your source files or research_tree.json itself.

Usage:
  python install_harness.py /path/to/target/repo
"""
import argparse
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HARNESS_ROOT = Path(__file__).resolve().parent.parent
TREE_NAME_PATTERN = re.compile(r"research_tree(?!\.schema\.json$).*\.json$", re.IGNORECASE)

HARNESS_FILES = [
    "scripts/validate_tree.py",
    "scripts/check_false_victory.py",
    "scripts/detect_new_pruning.py",
    "scripts/research_tree.schema.json",
    "lean/lean_audit.py",
]

CLAUDE_HOOK_FILES = [
    "hooks/claude/validate_tree_hook.py",
    "hooks/claude/check_tree_updated.py",
    "hooks/claude/block_unreviewed_stop.py",
]

GIT_HOOKS = ["pre-commit", "commit-msg"]


def make_executable(path):
    st = path.stat()
    path.chmod(st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def install_harness_dir(target):
    dest_dir = target / ".research-harness"
    dest_dir.mkdir(exist_ok=True)
    for rel in HARNESS_FILES:
        src = HARNESS_ROOT / rel
        dst = dest_dir / Path(rel).name
        shutil.copy2(src, dst)
        print(f"  copied {rel} -> {dst.relative_to(target)}")
    return dest_dir


def install_claude_hooks(target):
    dest_dir = target / ".research-harness" / "hooks"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for rel in CLAUDE_HOOK_FILES:
        src = HARNESS_ROOT / rel
        dst = dest_dir / Path(rel).name
        shutil.copy2(src, dst)
        print(f"  copied {rel} -> {dst.relative_to(target)}")


def install_git_hook(target, hook_name):
    git_hooks_dir = target / ".git" / "hooks"
    if not git_hooks_dir.exists():
        print(f"WARNING: {git_hooks_dir} does not exist -- is {target} a git repo? Skipping hooks.",
              file=sys.stderr)
        return False

    src = HARNESS_ROOT / "hooks" / hook_name
    dst = git_hooks_dir / hook_name

    if dst.exists():
        existing = dst.read_text(encoding="utf-8", errors="ignore")
        if "research-theory-discovery harness" in existing:
            shutil.copy2(src, dst)
            make_executable(dst)
            print(f"  updated existing harness hook: {dst.relative_to(target)}")
            return True
        # A foreign hook already exists -- chain to it instead of overwriting.
        chained_name = f"{hook_name}.pre-harness"
        chained_dst = git_hooks_dir / chained_name
        if not chained_dst.exists():
            shutil.copy2(dst, chained_dst)
            make_executable(chained_dst)
        new_content = src.read_text(encoding="utf-8")
        new_content = new_content.replace(
            "set -e\n",
            f'set -e\nif [ -x "$(dirname "$0")/{chained_name}" ]; then\n'
            f'  "$(dirname "$0")/{chained_name}" "$@" || exit $?\nfi\n',
            1,
        )
        dst.write_text(new_content, encoding="utf-8")
        make_executable(dst)
        print(f"  installed harness hook, chained onto pre-existing {hook_name} "
              f"(saved as {chained_name})")
        return True

    shutil.copy2(src, dst)
    make_executable(dst)
    print(f"  installed {dst.relative_to(target)}")
    return True


def find_existing_tree_files(target):
    r = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=target, capture_output=True, text=True,
    )
    if r.returncode != 0:
        return [p for p in target.rglob("*.json") if TREE_NAME_PATTERN.search(p.name)]
    return [target / line for line in r.stdout.splitlines() if TREE_NAME_PATTERN.search(Path(line).name)]


def check_existing_trees(target, validator_path):
    """The pre-commit/Stop hooks only fire the moment someone next commits or
    ends a turn -- if a non-conformant tree already exists, that first
    encounter is a surprise mid-task block with no warning it was coming.
    Check now, at install time, and say so up front instead."""
    found = find_existing_tree_files(target)
    if not found:
        return
    print(f"\n--- Pre-existing research-tree file(s) found ({len(found)}) ---")
    for path in found:
        rel = path.relative_to(target) if path.is_absolute() else path
        result = subprocess.run(
            [sys.executable, str(validator_path), str(path), "--strict"],
            capture_output=True, text=True,
        )
        if result.returncode == 0:
            print(f"  OK      {rel}")
        else:
            print(f"  WARNING {rel} does not currently pass strict validation.")
            print(f"          The pre-commit/Stop hooks just installed WILL BLOCK the next")
            print(f"          commit or turn-end that touches this file until it's fixed.")
            print(f"          Run: python {validator_path.relative_to(target) if validator_path.is_absolute() else validator_path} \"{rel}\" --strict")
            print(f"          to see the exact errors before you hit this mid-task.")


def print_next_steps(target):
    print("\n--- Layer B (Claude Code hooks) ---")
    print("Hook scripts installed to .research-harness/hooks/. Registration is not")
    print("auto-installed: settings.json is user-owned. Review and merge:")
    print(f"  {HARNESS_ROOT / 'hooks' / 'settings.snippet.json'}")
    print(f"into {target / '.claude' / 'settings.json'} (create the file if absent).")
    print("If 'python' does not resolve to a working interpreter in your shell,")
    print("edit the command strings in the snippet to 'python3' or 'py' accordingly.")

    print("\n--- Layer A (Workflow + subagents) ---")
    print("Copy these into the target repo if you want the deterministic")
    print("multi-agent research cycle available as a workflow:")
    print(f"  {HARNESS_ROOT / 'workflows' / 'research-cycle.js'} -> {target / '.claude' / 'workflows' / 'research-cycle.js'}")
    print(f"  {HARNESS_ROOT / 'agents' / 'claude'} -> {target / '.claude' / 'agents'} (merge contents)")
    print("The workflow works standalone without this copy step -- it embeds each subagent's role")
    print("instructions inline by default. Only copy agents/claude/ if you want to pass")
    print("args.useAgentTypes=true for real per-role tool restrictions (see harness/README.md).")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="path to the target research repository")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"FATAL: {target} does not exist", file=sys.stderr)
        sys.exit(2)

    print(f"Installing research-theory-discovery harness (Layer C + B hook scripts) into {target}")
    dest_dir = install_harness_dir(target)
    install_claude_hooks(target)
    for hook in GIT_HOOKS:
        install_git_hook(target, hook)
    check_existing_trees(target, dest_dir / "validate_tree.py")
    print_next_steps(target)


if __name__ == "__main__":
    main()
