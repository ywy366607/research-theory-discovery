#!/usr/bin/env python3
"""Deterministic tests for the ascent-descent layer contract in validate_tree.py.

Run: python harness/scripts/test_validate_layers.py
"""
import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_tree as vt  # noqa: E402


def base_node(nid, layer, **extra):
    node = {"id": nid, "parent": None, "title": nid, "status": "active", "motivation": "m",
            "action": "a", "conclusion": "", "invalidation": "i", "confidence": "D", "layer": layer}
    node.update(extra)
    return node


GOOD = {"title": "t", "nodes": [
    base_node("A1", "axiom", direction="ascent",
              lean={"decl": "X.conserved", "status": "audited", "independence_witness": "X.ring3",
                    "consistency_model": "X.toy"}),
    base_node("C1", "extension_axiom", direction="ascent", data_source="dataset v1",
              holdout="group 3", validity_range="below 0.5 um untested"),
    base_node("T1", "theorem", direction="descent", axioms_used=["A1", "C1"],
              lean={"decl": "X.t1", "status": "audited"}),
    base_node("G1", "algorithm", direction="descent", axioms_used=["A1"], implements=["T1"]),
]}


def run(tree):
    report = vt.Report()
    vt.validate(tree, report)
    return [m for _, m in report.errors]


passed = 0


def test(name, fn):
    global passed
    fn()
    passed += 1
    print(f"PASS {name}")


def t_good():
    assert run(GOOD) == [], run(GOOD)


def t_extension_needs_provenance():
    tree = copy.deepcopy(GOOD)
    del tree["nodes"][1]["data_source"]
    assert any("data_source" in e for e in run(tree))


def t_hypothesis_cannot_enter_theorem():
    tree = copy.deepcopy(GOOD)
    tree["nodes"].append(base_node("H1", "hypothesis"))
    tree["nodes"][2]["axioms_used"] = ["A1", "H1"]
    assert any("hypotheses may not enter" in e for e in run(tree))


def t_pruned_axiom_breaks_dependents():
    tree = copy.deepcopy(GOOD)
    tree["nodes"][0]["status"] = "superseded"
    tree["nodes"][0]["pruning_record"] = {"reason": "r", "pruning_commit": "abc", "recovery_note": "n"}
    errors = run(tree)
    assert sum("re-derive or prune" in e for e in errors) == 2, errors


def t_confirmed_theorem_needs_lean_audit():
    tree = copy.deepcopy(GOOD)
    t = tree["nodes"][2]
    t["status"] = "confirmed"
    t["lean"]["status"] = "paper"
    assert any("lean.status='audited'" in e for e in run(tree))


def t_axiom_revision_needs_no_go_in_order():
    tree = copy.deepcopy(GOOD)
    new = base_node("A2", "axiom", revises="A1",
                    no_go={"statement": "impossible under A1", "diagnosis_order": ["extension_axiom"]})
    tree["nodes"].append(new)
    assert any("diagnosis_order" in e for e in run(tree))
    new["no_go"]["diagnosis_order"] = ["algorithm", "extension_axiom", "derivation"]
    assert run(tree) == [], run(tree)


def t_confirmed_axiom_needs_independence():
    tree = copy.deepcopy(GOOD)
    tree["nodes"][0]["status"] = "confirmed"
    tree["nodes"][0]["lean"].pop("independence_witness")
    tree["nodes"][0].update({"prediction": {"registered_before_result": True, "falsifying_observation": "f"},
                             "false_win_checklist": [{"path": "p", "closed": True}],
                             "review": {"conclusion_reviewer": {"status": "approved", "reviewer": "r2"}}})
    assert any("independence_witness" in e for e in run(tree))


def t_algorithm_must_implement_theorem():
    tree = copy.deepcopy(GOOD)
    tree["nodes"][3]["implements"] = ["C1"]
    assert any("not a theorem node" in e for e in run(tree))


def t_legacy_nodes_unaffected():
    tree = {"title": "t", "nodes": [{k: v for k, v in base_node("N1", "x").items() if k != "layer"}]}
    assert run(tree) == []


for name, fn in [("good layered tree passes", t_good),
                 ("extension axiom needs provenance", t_extension_needs_provenance),
                 ("hypothesis cannot enter a theorem chain", t_hypothesis_cannot_enter_theorem),
                 ("pruned axiom breaks dependent theorem and algorithm", t_pruned_axiom_breaks_dependents),
                 ("confirmed theorem needs Lean audit", t_confirmed_theorem_needs_lean_audit),
                 ("axiom revision needs no-go after full diagnosis order", t_axiom_revision_needs_no_go_in_order),
                 ("confirmed axiom needs independence witness", t_confirmed_axiom_needs_independence),
                 ("algorithm must implement a theorem", t_algorithm_must_implement_theorem),
                 ("nodes without layer keep the old contract", t_legacy_nodes_unaffected)]:
    test(name, fn)
print(f"{passed} layer-contract tests passed")
