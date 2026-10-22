# Layer D -- Lean as a harness

The ascent-descent protocol puts every claim in a layer (general axiom, extension axiom,
theorem, algorithm, test). Lean supervises the two layers where mathematics decides:
**derivations** (theorems may use only declared clauses) and **algorithms** (reference
implementations with proved properties).

## Rules

1. **Axiom clauses are predicates or structure fields, never Lean `axiom`s.** A global
   `axiom` can make the whole environment inconsistent and hides dependencies. Written as
   predicates, every theorem's type lists exactly the clauses it uses:

   ```lean
   def Conserved (P : JumpProcess S) (Q : S → ℝ) : Prop := ∀ x y, 0 < P.rate x y → Q x = Q y
   theorem noether [Fintype S] (P : JumpProcess S) (Q : S → ℝ) : (…) ↔ P.Conserved Q
   ```

2. **Extension axioms are extending structures** whose docstring names the data source.
3. **"Proved" means audited**: no `sorry` / `admit` / `axiom` in project sources, and
   `#print axioms` lists only `propext`, `Classical.choice`, `Quot.sound`.
4. **Independence**: each general axiom gets a witness -- a model violating it while
   satisfying the rest (e.g. `ring3_not_reversible`: a one-way 3-cycle conserves particles
   yet is not reversible, so time-reversal symmetry is independent of conservation).
5. **Consistency**: at least one model satisfying all clauses.
6. **Algorithms**: a computable reference definition plus proved properties (conservation,
   bounds); production code is differentially tested against it. Proving conservation does
   not prove the specified dynamics; floating-point gaps are reported separately.
7. **What Lean cannot check**: whether axioms and extension axioms match nature (data layer),
   and whether a measurement targets the objective (test layer).

## `lean_audit.py`

```bash
python harness/lean/lean_audit.py --project path/to/lean/project --root MyLib \
    --tree research_tree.json --update-tree
```

- scans project sources (excluding `.lake`) for `sorry`, `admit`, `axiom` declarations;
- runs `#print axioms` on every `lean.decl`, `lean.independence_witness` and
  `lean.consistency_model` of non-pruned tree nodes (plus any `--decl`);
- fails on non-foundational axioms or unknown declarations;
- `--update-tree` writes `lean.status = "audited"` (or downgrades to `"stated"`), which
  `validate_tree.py` requires before a theorem node may become `confirmed`.

Tested: passes on the example project; fails with exit 1 on an injected `sorry`, an injected
`axiom`, and an unknown declaration; updates and re-validates the example tree.

## Example project (`example/`)

A finite-state Markov-jump language plus the first theorems of a worked example:
`expect_const_iff`, `noether` (Baez–Fong Noether correspondence), `energy_of_reversible`
(energy derived from time-reversal symmetry) and `ring3_not_reversible` (independence witness).
`research_tree.example.json` shows the matching layered tree nodes.

## Setup notes (Windows-tested)

```bash
# toolchain manager; ELAN_HOME may point to a roomy drive
elan-init -y --default-toolchain none
lake +leanprover-community/mathlib4:lean-toolchain new MyLib math
cd MyLib
MATHLIB_NO_CACHE_ON_UPDATE=1 lake update          # sources only, no 5+ GB cache
lake exe cache get Mathlib.Analysis.SpecialFunctions.Log.Basic   # only what you import
lake build
```

- `lake exe cache get` takes **module names**, not file paths.
- With little disk, point `.lake` at another drive (a directory junction or symlink) and
  set `MATHLIB_CACHE_DIR`. Importing only needed modules kept the example at about 2 GB of
  Mathlib build files instead of a full cache.
- Transient TLS failures while fetching dependencies are common; rerun `lake update`.
