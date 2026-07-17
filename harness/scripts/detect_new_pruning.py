#!/usr/bin/env python3
"""Compare the staged version of research_tree.json against HEAD's version
and print the ids of nodes whose status newly transitioned into
pruned/noisy/superseded in this commit. Empty output = no new pruning.

Used by hooks/commit-msg. Safe to call standalone:
  python detect_new_pruning.py path/to/research_tree.json
"""
import json
import subprocess
import sys

PRUNED_LIKE = {"pruned", "noisy", "superseded"}


def load_json_bytes(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def statuses_by_id(tree):
    if not isinstance(tree, dict):
        return {}
    return {
        n.get("id"): n.get("status")
        for n in tree.get("nodes", [])
        if isinstance(n, dict) and n.get("id")
    }


def main():
    if len(sys.argv) != 2:
        print("usage: detect_new_pruning.py path/to/research_tree.json", file=sys.stderr)
        sys.exit(2)

    rel_path = sys.argv[1]

    staged_raw = subprocess.run(
        ["git", "show", f":{rel_path}"], capture_output=True, text=True
    )
    new_tree = load_json_bytes(staged_raw.stdout) if staged_raw.returncode == 0 else None

    head_raw = subprocess.run(
        ["git", "show", f"HEAD:{rel_path}"], capture_output=True, text=True
    )
    old_tree = load_json_bytes(head_raw.stdout) if head_raw.returncode == 0 else None

    new_status = statuses_by_id(new_tree)
    old_status = statuses_by_id(old_tree)

    newly_pruned = [
        node_id
        for node_id, status in new_status.items()
        if status in PRUNED_LIKE and old_status.get(node_id) not in PRUNED_LIKE
    ]

    if newly_pruned:
        print(" ".join(sorted(newly_pruned)))


if __name__ == "__main__":
    main()
