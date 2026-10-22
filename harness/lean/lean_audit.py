#!/usr/bin/env python3
"""Lean audit for the ascent-descent protocol.

Checks, in a Lean 4 project:
  1. no `sorry` / `admit` and no `axiom` declarations in the project's own sources
     (axiom clauses must be predicates or structure fields, so every theorem lists the
     clauses it uses as hypotheses);
  2. every audited declaration depends only on Lean's foundational axioms
     (`propext`, `Classical.choice`, `Quot.sound`) per `#print axioms`.

Declarations come from `--decl` and/or from `research_tree.json` nodes carrying
`lean.decl` (pruned/noisy/superseded nodes are skipped). With `--update-tree`,
passing nodes get `lean.status = "audited"` and failing ones are downgraded to "stated".

Pure stdlib. Exit 0 on pass, 1 on audit failure, 2 on usage/build error.

Usage:
  python lean_audit.py --project path/to/lean/project --root MyLib \\
      [--tree research_tree.json] [--decl My.theorem ...] [--update-tree] [--json]
"""
import argparse
import json
import os
import re
import subprocess
import sys

FOUNDATIONAL = {"propext", "Classical.choice", "Quot.sound"}
PRUNED_LIKE = {"pruned", "noisy", "superseded"}
FORBIDDEN = [
    (re.compile(r"\bsorry\b"), "sorry"),
    (re.compile(r"\badmit\b"), "admit"),
    (re.compile(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*axiom\s", re.M), "axiom"),
]
DEPENDS_RE = re.compile(r"'([^']+)' depends on axioms: \[([^\]]*)\]")
NO_DEPS_RE = re.compile(r"'([^']+)' does not depend on any axioms")


def strip_comments(text):
    text = re.sub(r"/-.*?-/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    return re.sub(r"--[^\n]*", "", text)


def scan_sources(project):
    findings = []
    for root, dirs, files in os.walk(project):
        dirs[:] = [d for d in dirs if d not in (".lake", ".git", "build")]
        for name in files:
            if not name.endswith(".lean") or name.startswith("_lean_audit"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as f:
                code = strip_comments(f.read())
            for pattern, label in FORBIDDEN:
                for m in pattern.finditer(code):
                    line = code.count("\n", 0, m.start()) + 1
                    findings.append({"file": os.path.relpath(path, project), "line": line, "kind": label})
    return findings


def tree_decls(tree):
    out = []
    for node in tree.get("nodes", []):
        lean = node.get("lean") or {}
        if node.get("status") in PRUNED_LIKE:
            continue
        for key in ("decl", "independence_witness", "consistency_model"):
            if lean.get(key):
                out.append((lean[key], node.get("id")))
    return out


def print_axioms(project, root, decls, lake):
    tmp = os.path.join(project, "_lean_audit_tmp.lean")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(f"import {root}\n" + "".join(f"#print axioms {d}\n" for d in decls))
    try:
        proc = subprocess.run([lake, "env", "lean", tmp], cwd=project, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    finally:
        os.remove(tmp)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--root", required=True, help="module to import, e.g. the library root")
    ap.add_argument("--tree")
    ap.add_argument("--decl", action="append", default=[])
    ap.add_argument("--lake", default="lake")
    ap.add_argument("--update-tree", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    tree = None
    if args.tree:
        with open(args.tree, encoding="utf-8") as f:
            tree = json.load(f)
    pairs = [(d, None) for d in args.decl] + (tree_decls(tree) if tree else [])
    decls = list(dict.fromkeys(d for d, _ in pairs))

    forbidden = scan_sources(args.project)
    results, build_error = {}, None
    if decls:
        code, out = print_axioms(args.project, args.root, decls, args.lake)
        for name, axioms in DEPENDS_RE.findall(out):
            used = {a.strip() for a in axioms.split(",") if a.strip()}
            results[name] = sorted(used - FOUNDATIONAL)
        for name in NO_DEPS_RE.findall(out):
            results[name] = []
        if code != 0 and not results:
            build_error = out.strip()[-4000:]
    missing = [d for d in decls if d not in results]
    bad = {d: extra for d, extra in results.items() if extra}
    passed = not forbidden and not missing and not bad and build_error is None

    if args.update_tree and tree is not None:
        for node in tree.get("nodes", []):
            lean = node.get("lean") or {}
            d = lean.get("decl")
            if d in results:
                lean["status"] = "audited" if (not forbidden and not results[d]) else "stated"
            elif d in missing:
                lean["status"] = "stated"
        with open(args.tree, "w", encoding="utf-8") as f:
            json.dump(tree, f, indent=2, ensure_ascii=False)
            f.write("\n")

    report = {"passed": passed, "forbidden": forbidden, "audited": results,
              "non_foundational": bad, "missing_or_unknown": missing, "build_error": build_error}
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        for item in forbidden:
            print(f"FORBIDDEN {item['kind']}: {item['file']}:{item['line']}", file=sys.stderr)
        for d, extra in sorted(results.items()):
            print(f"{'OK ' if not extra else 'BAD'} {d}" + (f"  extra axioms: {extra}" if extra else ""))
        for d in missing:
            print(f"MISSING {d} (unknown declaration or build failure)", file=sys.stderr)
        if build_error:
            print(build_error, file=sys.stderr)
        print("AUDIT OK" if passed else "AUDIT FAILED", file=sys.stderr)
    sys.exit(0 if passed else (2 if build_error else 1))


if __name__ == "__main__":
    main()
