---
name: research-theory-discovery
description: Run open-ended scientific and technical research as novelty-style hypothesis search, necessity/mathematical-closure search, falsifiable prediction, and theory-package conflict diagnosis. Use for unclear research problems, first-principles architecture invention, mechanism claims, scientific prediction, unexpected experimental results, or theory-experiment conflicts. Do not use for routine implementation, ordinary debugging, simple literature summaries, or tasks with a fixed specification.
disable-model-invocation: true
---

# Research Theory Discovery

Treat the task as open-ended research, not as specification completion. The goal is to discover the real problem, orthogonal competing explanations, necessary missing theory structure, and decisive experiments before optimizing an implementation.

## Core Contract

1. Do not treat the user's proposed mechanism as the target answer.
2. Separate information by confidence and role:
   - results already observed in experiments, logs, or code inspection;
   - conclusions forced by formulas, definitions, or constraints;
   - extra conditions assumed so the theory can explain the experiment;
   - assumptions about whether the code really implements a mechanism;
   - interpretations of results;
   - guesses without supporting evidence.
3. Generate predictions before seeing or optimizing against the decisive experiment.
4. Treat experiments as testing a whole theory package, not the core theory alone:

```text
core theory + auxiliary assumptions + implementation + optimization + measurement -> observation
```

5. Do not use implementation success alone as proof of the mechanism, and do not treat one bad result as automatic death of the core theory.
6. Do not self-approve important claims. When independent agents or reviewers are available, route hypothesis support, experiment plans, and conclusion review to separate review surfaces. If independent review is unavailable, label the claim as unreviewed.

## When the User Already Has a Proposal

Temporarily quarantine the proposal.

First reconstruct the problem from observations and constraints. Generate alternatives that do not rely on the user's preferred mechanism. Then reintroduce the user's proposal as one candidate and compare it under the same criteria.

## Workflow

### 1. Build an evidence ledger

Label observations, constraints, equations, invariants, failed experiments, metrics, convenience assumptions, the current hypothesis, and unknowns. Flag claims that need external verification.

For long-running research, maintain a research tree rather than only a linear log. Each major assumption, implementation change, experiment family, or conclusion should attach to a parent node so that later invalidation can prune an entire subtree of dependent conclusions.

Store the research tree as a git-tracked structured file, such as `research_tree.json`. Keep the working tree as the latest research state; use git history for reversible pruning, rollback, and comparison of old subtrees.

### 2. Reconstruct the problem

Produce at least three materially different formulations. Differences must come from state variables, state-space geometry, causal direction, temporal scale, symmetry, observables, optimization dynamics, representation/retrieval relations, or measurement artifacts.

### 3. Run novelty-style hypothesis search

Generate 3-7 competing hypotheses. They should be as independent or orthogonal as possible at the mechanism level, not paraphrases of the same explanation.

Prefer hypotheses that differ in state variables, causal direction, geometry, time scale, optimization dynamics, information-flow path, measurement target, or the role of representation, retrieval, compression, or control.

If several explanations share the same underlying mechanism, merge them into one hypothesis family.

### 4. Run necessity / mathematical-closure search

Look for the object or condition that must be added for the facts, formulas, and experimental setup to coexist.

Ask:

- Which facts cannot coexist without extra structure?
- Which variable, state, symmetry, coupling, or scale is forced by consistency?
- Which constants should become dynamical variables?
- Which external training operation may belong inside the model dynamics?
- Which repeated patches suggest a missing common mechanism?
- Which limiting case exposes a contradiction?

Separate three strengths: **possible**, **useful**, and **necessary**. Never promote possible or useful to necessary without a derivation.

### 5. Derive self-binding predictions

When mathematics, physical analogy, information theory, dynamical systems, or cross-domain consistency suggests that a mechanism should work, do not state only the conclusion. State the conditions that bind the theory:

- where performance or mechanism metrics must improve;
- where the advantage must weaken, disappear, or reverse;
- what observation would show that the mathematical equivalence was not implemented;
- where conflict should be localized if the experiment fails.

If no prediction distinguishes the hypothesis from competitors, state that the idea is currently a design intuition, not a theory.

### 6. Design crucial experiments

Prefer experiments that separate hypotheses over experiments that merely seek improvement.

Use the minimum-experiment / maximum-information constraint: choose the smallest experiment set that can produce the largest decision-relevant information. If the objective being optimized is not in the experiment's search space, treat it as a structural design problem, not a tuning problem. If the initial setup cannot produce an informative conclusion, stop early and redesign instead of paying sunk cost.

Priority: analytical proof or counterexample, minimal system with known ground truth, mechanism probe, controlled ablation, scaling/extrapolation test, broad benchmark.

Close false-win paths: verify that the result is not explained by extra parameters, longer training budget, easier optimization, data leakage, metric averaging, hidden recurrence, deeper networks or extra passes, post-hoc selection, implementation asymmetry, or a baseline taking another shortcut.
For open-ended systems, also verify that reachability is not being reported as discovery, serialization as generation, handwritten scaffolds as learned mechanisms, vocabulary/codebook leakage as abstraction, or external search/manual patching as autonomous lineage.

Concrete checks:

- scan/recurrent implementations must not let the current token write and then read itself;
- full-site active models must not be compared as equivalent to ln_f-only active models;
- aggregate CE must not replace task/user/self/modality breakdowns;
- if a baseline can identify modality from token distribution, modality accuracy is not evidence that Wmeta worked;
- if the gain comes from more parameters or longer training, do not attribute it directly to the new mechanism.

### 7. Diagnose theory-experiment conflict

When prediction and observation disagree, decompose the theory package:

- Was the mathematical derivation wrong?
- Is the theory outside its domain?
- Is an auxiliary assumption false?
- Did the implementation realize the proposed object?
- Did optimization reach the relevant regime?
- Did the metric observe the predicted quantity?
- Did the baseline possess an alternate mechanism?
- Is this statistical or measurement error?
- Is the core theory false?

Treat stable, reproducible contradiction as a theory-discovery entry point. A minimal theory extension should locate the missing link in the theory package and explain both the original prediction and the anomalous result.

### 8. Decide the next action

End with one action: proceed to minimal implementation, run a mechanism probe first, derive a missing result, collect a different measurement, compare against an alternative hypothesis, narrow the theory domain, or abandon the hypothesis. Give a decision rule and stopping condition.

Before committing to costly work or strong conclusions, record review status: collaborator review for hypotheses, approval-style review for experiment plans, and reviewer-style audit for evidence-to-conclusion inference.

## Read When Needed

- For long sessions, complex theory conflicts, or examples, read `references/research-protocol.md`.
- For stable output formats, read `references/output-schema.md`.
- To visualize a research tree, write the tree as JSON and run `../harness/scripts/render_research_tree.py input.json output.html`.
- To enforce this protocol instead of relying on it being followed, see `../harness/README.md`. It
  adds git hooks that block an invalid `research_tree.json` or an unrecorded pruning, Claude Code
  hooks that re-validate the tree on every edit and block ending a turn while it's invalid, and a
  `Workflow` script (`../harness/workflows/research-cycle.js`) that runs hypothesize/necessity/predict
  and audit/review as deterministic multi-agent control flow rather than optional steps. The harness
  is shared across the English and Chinese skill versions -- it's language-neutral code and hooks,
  not translated prose.

## Default Output

Use these sections unless the user asks for another format:

1. **Research state**
2. **Problem reconstructions**
3. **Competing hypotheses**
4. **Necessity analysis**
5. **Pre-registered predictions**
6. **Crucial experiments**
7. **Conflict and cheating paths**
8. **Decision and stopping condition**

For long-running research, also include **Research tree update**. For costly experiments or strong conclusions, also include **Review status**.
