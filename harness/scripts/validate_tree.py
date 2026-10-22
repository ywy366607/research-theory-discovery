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

# Ascent-descent layer contract (optional `layer` field; enforced only when present).
LAYER_VALUES = {
    "phenomenon", "mechanism", "extension_axiom", "axiom", "theorem",
    "algorithm", "test", "parameter", "hypothesis",
}
DIRECTION_VALUES = {"ascent", "descent"}
AXIOM_LAYERS = {"axiom", "extension_axiom"}
LEAN_STATUS_VALUES = {"paper", "stated", "proved", "audited"}
DIAGNOSIS_LAYERS = ["algorithm", "extension_axiom", "derivation"]


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

        validate_layer(node, label, nodes, report)

        # --- Parent linkage sanity (soft -- root nodes may predate the tree).
        parent = node.get("parent")
        if parent is not None and parent not in seen_ids and not any(
            n.get("id") == parent for n in nodes
        ):
            report.warn(label, f"parent '{parent}' not found among nodes (forward reference or missing ancestor)")


def _nonempty(value):
    return value is not None and str(value).strip() != ""


def validate_layer(node, label, nodes, report):
    """Ascent-descent contract: every claim sits in one layer, and each layer has its
    own acceptance. Nodes without `layer` keep the original (pre-layer) contract."""
    layer = node.get("layer")
    if layer is None:
        return
    if layer not in LAYER_VALUES:
        report.error(label, f"layer '{layer}' not in {sorted(LAYER_VALUES)}")
        return
    direction = node.get("direction")
    if direction is not None and direction not in DIRECTION_VALUES:
        report.error(label, f"direction '{direction}' not in {sorted(DIRECTION_VALUES)}")
    status = node.get("status")
    live = status not in PRUNED_LIKE
    by_id = {n.get("id"): n for n in nodes if isinstance(n, dict)}
    lean = node.get("lean") or {}
    if lean and lean.get("status") is not None and lean.get("status") not in LEAN_STATUS_VALUES:
        report.error(label, f"lean.status '{lean.get('status')}' not in {sorted(LEAN_STATUS_VALUES)}")

    if layer == "extension_axiom":
        for field in ("data_source", "holdout", "validity_range"):
            if not _nonempty(node.get(field)):
                report.error(label, f"extension_axiom needs '{field}' -- without data provenance it is a "
                                    f"hypothesis (layer 'hypothesis') and may not enter a theorem chain")

    if layer == "axiom" and status == "confirmed":
        if not _nonempty(lean.get("independence_witness")):
            report.error(label, "confirmed axiom needs lean.independence_witness (a model violating it "
                                "while satisfying the others)")
        if not _nonempty(lean.get("consistency_model")):
            report.warn(label, "axiom has no lean.consistency_model recorded")

    if layer in AXIOM_LAYERS and _nonempty(node.get("revises")):
        no_go = node.get("no_go") or {}
        order = no_go.get("diagnosis_order") or []
        if layer == "axiom":
            if not _nonempty(no_go.get("statement")):
                report.error(label, "revising a general axiom needs no_go.statement (why the phenomenon is "
                                    "impossible under the old axioms)")
            if order != DIAGNOSIS_LAYERS:
                report.error(label, f"revising a general axiom needs no_go.diagnosis_order == {DIAGNOSIS_LAYERS} "
                                    f"(algorithm, extension axioms and derivation ruled out first)")
        elif order[:1] != ["algorithm"]:
            report.error(label, "revising an extension axiom needs no_go.diagnosis_order to start with "
                                "'algorithm' (implementation ruled out first)")

    if layer in ("theorem", "algorithm"):
        used = node.get("axioms_used")
        if layer == "theorem" and not used:
            report.error(label, "theorem needs 'axioms_used' (ids of axiom/extension_axiom nodes)")
        for ref in used or []:
            target = by_id.get(ref)
            if target is None:
                report.error(label, f"axioms_used references unknown node '{ref}'")
            elif target.get("layer") not in AXIOM_LAYERS:
                report.error(label, f"axioms_used '{ref}' is layer '{target.get('layer')}', not an axiom "
                                    f"or extension_axiom (hypotheses may not enter a theorem chain)")
            elif live and target.get("status") in PRUNED_LIKE:
                report.error(label, f"depends on pruned/superseded '{ref}' -- re-derive or prune this node")
        if layer == "theorem" and status == "confirmed" and lean.get("status") != "audited":
            report.error(label, "confirmed theorem needs lean.status='audited' (paper derivations stay active)")

    if layer == "algorithm":
        impl = node.get("implements")
        if not impl:
            report.error(label, "algorithm needs 'implements' (ids of theorem nodes)")
        for ref in impl or []:
            target = by_id.get(ref)
            if target is None or target.get("layer") != "theorem":
                report.error(label, f"implements '{ref}' is not a theorem node")
            elif live and target.get("status") in PRUNED_LIKE:
                report.error(label, f"implements pruned/superseded theorem '{ref}'")


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
