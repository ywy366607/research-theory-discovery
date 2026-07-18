#!/usr/bin/env python3
"""Validate a research_tree.json file against the research-theory-discovery
harness invariants.

Pure stdlib, no third-party dependencies, so it can run from a git hook,
a Claude Code PostToolUse hook, or plain CI without an install step.

Exit codes:
  0  no errors (warnings are allowed unless --strict)
  1  structural or invariant errors found
  2  usage error (bad path, unparseable JSON)

Usage:
  python validate_tree.py path/to/research_tree.json [--strict] [--json]
"""
import argparse
import json
import re
import sys

# Any short, stable, unique identifier works (N001, L0, R-14, ...) -- the
# earlier ^N[0-9]{3,}$ pattern was copied from one example in the docs and
# rejected every other reasonable convention, including L0/L1/... trees that
# real usage of this harness has already produced. All that actually matters
# is: starts with a letter, no whitespace/slashes, reasonably short.
NODE_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,31}$")
PREDICTION_ID_RE = re.compile(r"^P-[0-9]{8}-[0-9]{2}$")

STATUS_VALUES = {
    "active", "confirmed", "pruned", "noisy", "superseded", "partially_reusable",
}
CONFIDENCE_VALUES = {"O", "K", "D", "A", "I", "M", "S"}
PRUNED_LIKE = {"pruned", "noisy", "superseded"}
REVIEW_ACCEPT_VALUES = {"accepted", "approved"}

REQUIRED_NODE_FIELDS = ["id", "parent", "title", "status", "motivation", "action", "invalidation"]


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, node_id, msg):
        self.errors.append((node_id, msg))

    def warn(self, node_id, msg):
        self.warnings.append((node_id, msg))

    def ok(self, strict):
        if self.errors:
            return False
        if strict and self.warnings:
            return False
        return True


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"FATAL: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(2)


def validate(tree, report):
    if not isinstance(tree, dict):
        report.error(None, "root of research_tree.json must be an object")
        return
    nodes = tree.get("nodes")
    if not isinstance(nodes, list):
        report.error(None, "research_tree.json must have a top-level 'nodes' array")
        return
    if len(nodes) == 0:
        report.warn(None, "tree has zero nodes")
        return

    seen_ids = {}
    for i, node in enumerate(nodes):
        label = f"nodes[{i}]"
        if not isinstance(node, dict):
            report.error(label, "node is not an object")
            continue

        node_id = node.get("id")
        label = node_id or label

        for field in REQUIRED_NODE_FIELDS:
            if field not in node:
                report.error(label, f"missing required field '{field}'")
            elif field != "parent" and (node.get(field) is None or str(node.get(field)).strip() == ""):
                report.error(label, f"field '{field}' is present but empty")

        if node_id is not None:
            if not NODE_ID_RE.match(str(node_id)):
                report.error(label, f"id '{node_id}' does not match {NODE_ID_RE.pattern} "
                                     f"(must start with a letter; letters/digits/_/./- only)")
            if node_id in seen_ids:
                report.error(label, f"duplicate node id '{node_id}' (also at nodes[{seen_ids[node_id]}])")
            else:
                seen_ids[node_id] = i

        status = node.get("status")
        if status is not None and status not in STATUS_VALUES:
            report.error(label, f"status '{status}' not in {sorted(STATUS_VALUES)}")

        confidence = node.get("confidence")
        if confidence is not None and confidence not in CONFIDENCE_VALUES:
            report.error(label, f"confidence '{confidence}' not in {sorted(CONFIDENCE_VALUES)}")
        elif confidence is None:
            report.warn(label, "no 'confidence' evidence class set (O/K/D/A/I/M/S)")

        if not node.get("invalidation") or not str(node.get("invalidation")).strip():
            report.error(label, "node has no invalidation condition -- every claim must state what would kill it")

        # --- Hard gate: a node cannot claim 'confirmed' without pre-registration,
        #     a closed false-win checklist, and independent conclusion review.
        if status == "confirmed":
            prediction = node.get("prediction") or {}
            if not prediction:
                report.error(label, "status=confirmed but no 'prediction' block (predictions must be pre-registered)")
            else:
                if prediction.get("registered_before_result") is not True:
                    report.error(label, "status=confirmed but prediction.registered_before_result is not true")
                pid = prediction.get("id")
                if pid and not PREDICTION_ID_RE.match(str(pid)):
                    report.error(label, f"prediction.id '{pid}' does not match ^P-YYYYMMDD-NN$")
                if not prediction.get("falsifying_observation"):
                    report.warn(label, "prediction has no falsifying_observation stated")

            checklist = node.get("false_win_checklist")
            if not checklist:
                report.error(label, "status=confirmed but no false_win_checklist present")
            else:
                open_paths = [c.get("path") for c in checklist if c.get("closed") is not True]
                if open_paths:
                    report.error(label, f"status=confirmed but false-win paths still open: {open_paths}")

            review = node.get("review") or {}
            conclusion_review = review.get("conclusion_reviewer") or {}
            rstatus = conclusion_review.get("status")
            if rstatus not in REVIEW_ACCEPT_VALUES:
                report.error(
                    label,
                    f"status=confirmed but review.conclusion_reviewer.status='{rstatus}' "
                    f"(must be one of {sorted(REVIEW_ACCEPT_VALUES)} -- no self-approved confirmations)",
                )
            elif conclusion_review.get("reviewer") in (None, "", "self", "same-session"):
                report.error(label, "conclusion_reviewer.reviewer is missing/self -- review must be an independent surface")

        # --- Hard gate: pruned/noisy/superseded nodes need a recoverable record.
        if status in PRUNED_LIKE:
            pruning = node.get("pruning_record") or {}
            for f in ("reason", "pruning_commit", "recovery_note"):
                if not pruning.get(f):
                    report.error(label, f"status='{status}' but pruning_record.{f} is missing")

        # --- Parent linkage sanity (soft -- root nodes may predate the tree).
        parent = node.get("parent")
        if parent is not None and parent not in seen_ids and not any(
            n.get("id") == parent for n in nodes
        ):
            report.warn(label, f"parent '{parent}' not found among nodes (forward reference or missing ancestor)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="path to research_tree.json")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON report instead of text")
    args = ap.parse_args()

    tree = load(args.path)
    report = Report()
    validate(tree, report)
    passed = report.ok(args.strict)

    if args.json:
        print(json.dumps({
            "path": args.path,
            "passed": passed,
            "errors": [{"node": n, "message": m} for n, m in report.errors],
            "warnings": [{"node": n, "message": m} for n, m in report.warnings],
        }, indent=2))
    else:
        for n, m in report.errors:
            print(f"ERROR  [{n}] {m}", file=sys.stderr)
        for n, m in report.warnings:
            print(f"WARN   [{n}] {m}", file=sys.stderr)
        status_word = "PASS" if passed else "FAIL"
        print(f"{status_word}: {args.path} "
              f"({len(report.errors)} errors, {len(report.warnings)} warnings)", file=sys.stderr)

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
