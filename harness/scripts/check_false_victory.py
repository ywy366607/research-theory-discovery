#!/usr/bin/env python3
"""Check that every 'confirmed' node in research_tree.json has closed its
false-win checklist against the canonical path list in
references/output-schema.md.

This is stricter than validate_tree.py's generic check: it additionally
flags nodes whose false_win_checklist is present but only covers a subset
of the canonical paths, so a node can't sneak past by listing two easy
paths and omitting the rest.

Exit codes:
  0  every confirmed node's checklist is closed and covers all canonical paths
  1  at least one confirmed node has an open or missing path
  2  usage error
"""
import argparse
import json
import sys

# Canonical list, kept in sync with references/output-schema.md "False-Win Checklist".
CANONICAL_PATHS = [
    "Extra capacity / training budget",
    "Optimization change",
    "Data leakage",
    "Metric averaging",
    "Hidden recurrence / extra passes",
    "Implementation asymmetry",
    "Baseline bypass",
    "Reachability mistaken for discovery",
    "Serialization mistaken for generation",
    "Handwritten scaffold substitution",
    "Teacher or oracle leakage",
    "Vocabulary / codebook leakage",
    "Search-budget mismatch",
    "Macro prior not charged",
    "Offline corpus contamination",
    "Lineage discontinuity",
]


def check_node(node, require_all_paths):
    node_id = node.get("id", "<unknown>")
    problems = []
    checklist = node.get("false_win_checklist") or []
    by_path = {c.get("path"): c for c in checklist if isinstance(c, dict)}

    paths_to_check = CANONICAL_PATHS if require_all_paths else list(by_path.keys())
    if not paths_to_check:
        problems.append("false_win_checklist is empty")
        return node_id, problems

    for path in paths_to_check:
        entry = by_path.get(path)
        if entry is None:
            problems.append(f"canonical path not addressed: '{path}'")
            continue
        if entry.get("closed") is not True:
            problems.append(f"path not closed: '{path}' (residual_risk={entry.get('residual_risk')!r})")
        elif not entry.get("evidence"):
            problems.append(f"path marked closed but has no evidence: '{path}'")

    return node_id, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="path to research_tree.json")
    ap.add_argument("--require-all-paths", action="store_true",
                     help="require every canonical false-win path to be explicitly addressed, "
                          "not just the ones the author chose to list")
    args = ap.parse_args()

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            tree = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"FATAL: cannot read {args.path}: {e}", file=sys.stderr)
        sys.exit(2)

    nodes = tree.get("nodes", [])
    confirmed = [n for n in nodes if isinstance(n, dict) and n.get("status") == "confirmed"]

    if not confirmed:
        print("no 'confirmed' nodes to check", file=sys.stderr)
        sys.exit(0)

    failed = False
    for node in confirmed:
        node_id, problems = check_node(node, args.require_all_paths)
        if problems:
            failed = True
            print(f"FAIL [{node_id}]", file=sys.stderr)
            for p in problems:
                print(f"  - {p}", file=sys.stderr)
        else:
            print(f"OK   [{node_id}]", file=sys.stderr)

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
