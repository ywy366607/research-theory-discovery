---
name: research-theory-discovery
description: Run open-ended scientific and technical research as an ascent-descent axiomatic loop. Ascend by induction from phenomena to mechanisms, extension axioms and the minimal general axioms that generate the problem; descend by deduction from corrected axioms to theorems, algorithms and tests that produce new phenomena; iterate, with Lean as one harness supervising derivations and algorithms. Use for unclear research problems, first-principles or axiomatic architecture invention, mechanism claims, scientific prediction, unexpected results, or theory-experiment conflicts. Do not use for routine implementation, ordinary debugging, simple literature summaries, or tasks with a fixed specification.
disable-model-invocation: true
---

# Research Theory Discovery: ascend, then descend

Behind a set of problems sits a set of essentials (axioms) that generates them. Research has two directions:

- **Ascent (induction)**: from phenomena, find the mechanisms; from mechanisms, find the minimal essentials that generate them.
- **Descent (deduction)**: fix the wrong essential, then derive down through theorems, algorithms and tests to new phenomena.

New phenomena start the next ascent.

**Creativity opens the feasible space, mathematics checks closure, experiments decide what stays.** Inductive results cannot be proven; they are conjectures that survive only if their deductive consequences pass tests. Lean guarantees that no derivation smuggles in undeclared assumptions. It does not guarantee that the axioms match nature.

## 1. Layers: every claim sits in one

| Layer | Content | Accepted by |
|---|---|---|
| **General axioms** | The fewest, most general constraints on the object | Discussion; consistency via one model; independence via a model violating each clause while satisfying the rest (Lean) |
| **Extension axioms** | Laws valid for one class of objects (functional forms, constants), like adding commutativity to group theory, or constitutive laws in physics | Real data with held-out tests; data source mandatory |
| **Theorems (mechanisms)** | Derived from axioms plus extension axioms | Lean proof; unformalized ones are labeled "paper" |
| **Algorithms** | Runnable implementations of theorems | Lean reference implementation with proved properties; production code differentially tested against it |
| **Tests / phenomena** | Predictions versus observations | Pre-registered decisive experiments |

**Parameters and models.** Numerical values are parameters and belong to no layer. A concrete system is a *model*: `general axioms (all satisfied) + registered extension axioms + parameter values`. Changing a parameter does not trigger failure diagnosis, unless the value is shown to violate an axiom.

## 2. Core contract

1. Do not treat the user's proposed mechanism, or a retrieved paper, as the target answer.
2. Separate information by confidence and layer:
   - observed results (phenomena);
   - conclusions forced by formulas or constraints (theorems, marked "Lean-proved" or "paper");
   - extra conditions assumed to explain experiments (extension-axiom candidates or hypotheses H);
   - assumptions that code implements a mechanism (algorithm layer);
   - interpretations;
   - unsupported guesses.
3. Generate predictions before seeing or optimizing against the decisive experiment.
4. An experiment tests the whole package: `general axioms + extension axioms + derivation + implementation + optimization + measurement -> observation`.
5. Implementation success does not prove a mechanism, and one bad result does not kill the core theory. **Self-consistency (balanced ledgers, bitwise restores, all tests green) is an engineering gate, not scientific evidence.**
6. Do not self-approve important claims: route hypothesis support, experiment plans and conclusion review to separate review surfaces, or label claims unreviewed.
7. Separate the user objective, acceptance metrics and mechanism proxies; state how each proxy connects to the objective.
8. Separate discovery from acceptance: explicit design intuitions may enter bounded search, but conclusions are limited by evidence.
9. **Extension axioms need a data source, a held-out test and a validity range.** Choices without them are hypotheses H and may not enter a theorem chain. "Physics" assembled from hand-set constants is H.
10. **In Lean, axioms are structure fields or predicates, never the `axiom` keyword.** "Proved" means the Lean audit passed: no `sorry`, `admit` or `axiom` declarations, and `#print axioms` shows only foundational axioms.
11. **Before revising a general axiom, walk the full diagnosis order** (section 5) and state a no-go theorem or an explicit counterexample. Never skip lower layers to add an axiom, and never bypass axioms to add a mechanism.
12. **Target properties are never axioms.** If the target definition says a property arises spontaneously, emerges or is bootstrapped, it is a theorem to be proven (an existence conjecture). Assuming it would contradict the definition itself.

## 3. Ascent (induction)

### 1. Evidence ledger and target contract (phenomenon layer)

Record observations, constraints, equations, invariants, failed experiments, metrics, convenience assumptions, current hypotheses and unknowns. Write a target contract: capability objective -> primary metric and evaluation -> strongest reproducible baseline -> resource limits. Label each constraint a hard user requirement, a mathematical necessity, or an adjustable preference.

Maintain a git-tracked `research_tree.json`; nodes carry `layer` and `direction`. When a base node fails, prune its dependent subtree. When an axiom is replaced, every theorem, algorithm and conclusion depending on it is re-derived or pruned.

### 2. Reformulate the problem

Give at least three materially different formulations: different state variables, geometry, causal direction, time scales, symmetries, observables, optimization dynamics, representation/retrieval roles, or measurement artifacts.

### 3. Competing mechanism hypotheses

Generate 3-7 hypotheses that are orthogonal in underlying mechanism, and merge those sharing a mechanism. For architecture work, at least one candidate should change the feasible space: a new necessary state, causal path, learning object, or timing. Turn user intuition into its strongest testable version and compare it fairly.

### 4. Necessity and mathematical closure

Find what must be added for the facts, formulas and setup to coexist. Ask:

- which facts cannot coexist without extra structure;
- what is forced by consistency;
- which constants should become dynamic;
- which repeated patches suggest one missing mechanism;
- which limit exposes a contradiction.

Grade each finding as **possible**, **useful** or **necessary**, and never upgrade without a derivation.

### 5. Induce extension axioms

Write data-supported mechanism laws as extension axioms, with:

- form;
- data source;
- held-out test;
- validity range.

Do not share untested constants across different objects.

### 6. Axiomatize: find the minimal essence that generates the problem

- **Merge and demote**: clauses derivable from others become theorems. Primitive notions derivable from symmetry are eliminated, Noether-style: on a Markov layer, a quantity is conserved iff it commutes with the generator, and reversibility yields an energy function. Clauses that are boundary conditions of others are folded in; for example, openness is the boundary condition of a conservation law.
- **Independence**: every axiom gets a model violating it while satisfying the rest, preferably verified in Lean. A clause without a witness may be redundant.
- **Consistency**: give at least one model satisfying all clauses, either a Lean construction or a real system.
- **Split definition from target theorems**: premises of the target definition become axioms; emergent properties become theorems (contract item 12).
- **Locate the wrong essence**: name the clause, extension axiom or missing clause that generates the observed problem.

Minimal means mutually non-derivable and sufficient for the declared scope, not fewest words. Declare the scope; do not chase 100% coverage.

## 4. Descent (deduction)

### 7. Correct the essence

Only after the diagnosis order has been walked, rewrite the located axiom or extension axiom. New axioms also need independence witnesses and a consistency model.

### 8. Derive theorems

Each mechanism lists the axioms and extension axioms it uses, and is proved in Lean or labeled "paper". When a derivation does not close, write down the missing premise instead of adding a mechanism "by necessity".

### 9. Algorithms

- Write a computable Lean reference implementation with proved properties (conservation, bounds, convergence).
- Differentially test production code against it on shared vectors.
- Report floating-point gaps separately.
- Respect the resource limits of the target contract.

Proving conservation is not proving the specified dynamics.

### 10. Pre-registered predictions and decisive experiments

State self-binding predictions:

- when metrics must improve;
- when the advantage must weaken, vanish or reverse;
- what would show that the "mathematical equivalence" was not implemented;
- which layer a failure points to.

Without discriminating predictions, call it a design intuition.

Choose experiments by decision value and cost. Write the action for gain, no gain and ambiguous outcomes, and cut measurements whose outcomes all lead to the same action. Keep the best reproducible baseline and change one core claim.

Priority:

1. proof or counterexample (Lean);
2. minimal system with ground truth;
3. mechanism probe;
4. controlled ablation;
5. scaling or extrapolation;
6. broad benchmark.

Close false-win paths:

- capacity or training budget, optimization stability;
- leakage, metric averaging;
- hidden recurrence or extra passes;
- post-hoc selection;
- implementation asymmetry, baseline bypass;
- reachability mistaken for discovery, serialization for generation, handwritten scaffolds for learning.

### 11. Tests produce new phenomena

Results return to step 1 as new phenomena for the next ascent.

## 5. Diagnosis order and theory-experiment conflicts

When a prediction fails, check bottom-up:

1. **Algorithm**: does the implementation equal the theorem? Check the Lean reference, differential tests and step-size convergence.
2. **Extension axiom**: under the same general axioms, does a registered alternative explain the held-out data?
3. **Derivation**: is there a hidden premise? Lean exposes it.
4. **General axiom**: only after the three lower layers are cleared, prove the phenomenon impossible under the current axioms, then revise.

Package items map to layers:
- a math error points to the derivation;
- a scope violation or a false auxiliary assumption points to the extension axioms;
- an implementation that does not implement the theory object, or optimization outside the relevant regime, points to the algorithm;
- a mis-targeted metric, a statistical artifact or a baseline shortcut points to the test layer;
- a false core theory points to the general axioms.

Precedent: Uranus' anomaly was an extension/data-layer fault (Neptune was found); Mercury's perihelion, after the "Vulcan" extension failed, was an axiom-layer fault (general relativity). Stable, reproducible contradictions are entry points to discovery.

## 6. Lean as a harness

- General axioms are `structure` fields or `def … : Prop` predicates; theorem types list the clauses used. Extension axioms are extending structures documenting their data source.
- Audit with `harness/lean/lean_audit.py`: no `sorry`, `admit` or `axiom` declarations; `#print axioms` on every `lean.decl` in the tree may show only `propext`, `Classical.choice`, `Quot.sound`.
- Tree validation: theorem nodes list `axioms_used`, which may reference only live axiom or extension-axiom nodes; pruning an axiom flags its live dependents.
- Lean cannot check whether axioms match nature, floating-point error, or whether a measurement targets the objective.
- With limited disk, fetch only the Mathlib modules you import: `lake exe cache get Mathlib.X.Y`.

## 7. Decide the next step

End with one action plus a decision rule and stopping condition. Possible actions:

- minimal implementation;
- mechanism probe;
- derive a missing result;
- another measurement;
- compare alternatives;
- narrow the scope;
- revise an axiom;
- abandon.

Check whether this round opened feasible space, resolved a contradiction or changed the next decision; if it only added description, narrow down or implement a justified candidate. Record review status before costly work.

## When the user already has a proposal

Quarantine it, reconstruct the problem from observations and constraints, generate alternatives, then reinsert the proposal as one candidate under the same standard. Derive user intuitions about the axiom layer seriously: if one holds, demote or merge; if not, give a counterexample. Both are progress.

## Read when needed

- Axiomatic method in detail, with examples: `references/axiomatic-method.md`.
- Long sessions, complex conflicts, discovery versus acceptance: `references/research-protocol.md`.
- Stable output format: `references/output-schema.md`.
- Enforcement, see `../harness/README.md`:
  - git hooks;
  - Claude Code hooks;
  - Workflow stages, including `axiomatize` and `diagnose`;
  - Lean audit in `../harness/lean/`.

## Default output

1. **Research state and layer position** (ascent or descent, which layers)
2. **Problem reformulations**
3. **Competing hypotheses**
4. **Necessity analysis**
5. **Axiom and extension-axiom table** (added, merged, demoted, independence witnesses, consistency model)
6. **Theorem dependencies and Lean status**
7. **Pre-registered predictions and decisive experiments**
8. **Conflicts, diagnosed layer and false-win paths**
9. **Decision and stopping condition**

Long-running research adds a **research tree update**; costly experiments or strong claims add **review status**.
