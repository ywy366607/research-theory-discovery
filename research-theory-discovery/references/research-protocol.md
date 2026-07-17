# Expanded Research Protocol

## Contents

A. Evidence Classes -- B. Blind Reconstruction -- C. Novelty-Style Hypothesis Search --
D. Theory Strength Ladder -- E. Independent Review Surfaces -- F. Necessity / Mathematical-Closure
Search -- G. Self-Binding Predictions -- H. Prediction Quality -- I. Crucial-Experiment Matrix --
J. Minimum-Experiment / Maximum-Information Constraint -- K. False-Win Path Check --
L. Theory-Package Conflict Decomposition -- M. Research Memory

## Purpose

This reference expands the `research-theory-discovery` workflow for long research sessions. Read it when the problem has multiple experiments, several competing theories, or an evolving research program.

## A. Evidence Classes

Use the following labels:

- **O - Observation:** directly measured or supplied result.
- **K - Established knowledge:** externally supported result or accepted mathematical fact.
- **D - Deduction:** follows from stated premises.
- **A - Auxiliary assumption:** needed to connect theory to experiment.
- **I - Implementation assumption:** claim about what the code or architecture realizes.
- **M - Measurement assumption:** claim that a metric detects the relevant phenomenon.
- **S - Speculation:** plausible but not yet derived or observed.

A research answer should not allow S or A to quietly masquerade as O or D.

## B. Blind Reconstruction

When the user provides a favored mechanism:

1. Restate the observations without mechanism language.
2. List the functional and mathematical constraints.
3. Generate alternatives from at least three different conceptual families.
4. Only then compare the favored mechanism.

This reduces conversational anchoring. It cannot erase knowledge already present in context, so label the process as a debiasing procedure, not a truly blind experiment.

## C. Novelty-Style Hypothesis Search

Hypothesis-space exploration should work like novelty search, not like listing similar explanations.

Independent hypotheses should be as orthogonal as possible at the underlying-structure level. Prefer differences in:

- state variables;
- causal direction;
- state-space geometry;
- time scale or update frequency;
- optimization dynamics;
- information-flow path;
- measurement target;
- the role of representation, retrieval, compression, or control.

If several explanations share the same underlying mechanism, merge them into one hypothesis family and search for genuinely different families.

Common hypothesis families include:

- the user's mechanism;
- a simpler mechanism;
- measurement artifact;
- optimization failure;
- implementation not realizing the theoretical object;
- baseline possessing an alternate route;
- ill-posed problem definition;
- a different mathematical formalization.

## D. Theory Strength Ladder

### Design intuition

A component may help and has a plausible analogy.

### Mechanism hypothesis

A specified internal process is claimed to cause an observable effect.

### Restricted theory

The mechanism yields derived predictions under explicit assumptions and within a stated domain.

### Strong theory

The mechanism compresses multiple observations, excludes alternatives, and survives novel discriminating tests.

Do not jump levels based only on benchmark improvement.

## E. Independent Review Surfaces

Do not let the same reasoning pass invent, approve, and validate a high-impact research claim.

Use independent review surfaces when available:

1. **Collaborator review for core hypotheses.** The reviewer should be charitable to the hypothesis, check whether it was stated in its strongest coherent form, add missing supportive mechanisms, and identify what would make it worth testing. This role is not a hostile critic.
2. **Approval-committee review for experiment plans.** The reviewer should judge whether the experiment is sufficient, necessary, minimal, information-rich, and motivated enough to spend compute or time. It should reject redundant, low-information, or structurally mis-specified experiments.
3. **Reviewer audit for conclusions.** The reviewer should receive the evidence, protocol, and proposed conclusion, then check whether the conclusion follows, whether false-win paths remain, and whether the research tree dependencies invalidate any part of the claim.

If independent agents are unavailable, perform the same checks internally but label the result as **unreviewed** and lower confidence. Do not present internally self-approved conclusions as independently reviewed.

## F. Necessity / Mathematical-Closure Search

Necessity search is not ordinary brainstorming. It searches for what must be added so facts, formulas, and experimental setup can coexist.

Use these questions:

1. Which known facts cannot coexist without extra structure?
2. What variable, object, symmetry, state, or coupling is forced by consistency?
3. Which constants should become dynamical variables?
4. Which external training operation may belong inside the model dynamics?
5. Which repeated patches suggest a missing common mechanism?
6. Which limiting case exposes a contradiction?
7. Which cross-domain equivalence or first-principles argument requires a mechanism to work?

Distinguish:

- **Possible:** compatible with current constraints.
- **Useful:** likely to improve an objective.
- **Necessary:** without it, the stated facts, formulas, or experimental structure cannot coexist.

Never promote possible or useful to necessary without a derivation.

## G. Self-Binding Predictions

A strong prediction is not "the model should be better." It is the theory taking risk.

When mathematical consistency, physical analogy, information theory, dynamical systems, or another domain suggests that a mechanism should work, state:

- which premises must hold;
- which metrics must improve;
- where the advantage must disappear;
- what result would show the equivalence was not implemented;
- if it fails, where conflict should first be localized in the theory package.

Example: if the update rule `R <- R + beta * (v - Rk) k^T` is interpreted as online LoRA/BRA writing, then mathematically it is one gradient-descent step on `||v - Rk||^2`. This predicts that, when key/value alignment, step size, capacity, and readout path are adequate, repeated writes of the same content should reduce local reconstruction or prediction error. If the experiment is not equivalent or performance gets worse, first inspect step size, normalization, key space, write gates, readout path, optimization, and measurement before declaring the online-LoRA theory false.

## H. Prediction Quality

A strong prediction is:

- made before the decisive result;
- specific enough to be wrong;
- different from the strongest alternative;
- robust to reasonable implementation choices;
- accompanied by a measurement procedure;
- tied to a derivation.

A weak prediction merely says that a proposed model will perform better.

## I. Crucial-Experiment Matrix

For each experiment, compare expected outcomes under all live hypotheses.

| Experiment | H1 | H2 | H3 | Main confound | Decision rule |
|---|---|---|---|---|---|

Prefer experiments whose outcome patterns differ across hypotheses.

## J. Minimum-Experiment / Maximum-Information Constraint

Experiment design should maximize information per run. Compression is intelligence: a good research plan extracts the most decision-relevant information from the fewest experiments.

Use these rules:

1. State the decision the experiment is supposed to change.
2. Check whether the optimized objective is actually inside the experiment's search space.
3. Prefer richer measurements over more runs when one run can expose several mechanism variables.
4. If all plausible outcomes would leave the same decision unchanged, the experiment has low information value.
5. If the setup is structurally unable to test the claim, stop early and redesign instead of paying sunk cost.
6. Treat blind hyperparameter tuning as inappropriate when the failure mode is structural.

Examples:

- If a memory mechanism is claimed to help cross-block transfer, measure normal/zero/shuffle state, per-source loss, state rank, write/read gates, and baseline bypasses in the same small run before launching long training.
- If the target behavior cannot be expressed by any path in the current architecture, no amount of tuning can validate the mechanism; the search space is wrong.
- If two experiments differ only by redundant metrics or cosmetic variants, merge them or drop one.

## K. False-Win Path Check

Experiment design must actively close paths where the result improves but the proposed mechanism did not win.

Common false wins include:

- **Extra capacity:** the new model has more parameters, and the gain comes from capacity rather than mechanism.
- **Training budget:** the new model trains longer or sees more data.
- **Optimization change:** the new module makes optimization easier, but the mechanism itself is not used.
- **Data leakage:** for example, a scan/recurrent implementation lets the current token write and then immediately read itself.
- **Metric averaging:** aggregate CE hides opposite changes across task/user/self/modality.
- **Hidden recurrence:** one model has extra loops, state, or passes that the baseline lacks.
- **Depth or ensemble effect:** the improvement is just a deeper network or multiple paths voting.
- **Post-hoc selection:** many configurations are run and only the best is reported.
- **Implementation asymmetry:** for example, full-site active and ln_f-only active are treated as the same configuration.
- **Baseline bypass:** the baseline solves the task through token distribution, source ID, local window, or prompt template.
- **Reachability mistaken for discovery:** showing that the search space can represent a structure, theorem, or architecture is reported as evidence that the system learned to find or create it.
- **Serialization mistaken for generation:** a model that can encode, decode, import, or replay an object is described as having autonomously invented that object.
- **Handwritten scaffold substitution:** the claimed learned mechanism is replaced by manually written builders, templates, curricula, rules, or privileged repair logic.
- **Teacher or oracle leakage:** the controller sees target builders, architecture names, benchmark labels, hidden-test summaries, oracle edits, or post-hoc traces that should be outside its causal context.
- **Vocabulary leakage:** learned tokens, macros, or codebook entries smuggle benchmark identities, source families, task labels, or human architecture names instead of reusable mechanisms.
- **Search-budget mismatch:** one method receives more candidates, verifier calls, retries, beam width, mutation attempts, compile failures, or human interventions than its baseline.
- **Macro prior not charged:** a method gets a pretrained vocabulary, architecture library, compiler intrinsic, fused kernel, or sidecar parameter payload without counting its description length, build cost, or provenance.
- **Compiler/kernel shortcut:** improvement comes from a privileged fused implementation, library routine, numerical backend, or hidden state unavailable to the compared representation.
- **Compression mistaken for expressivity:** shorter descriptions, BPE/MDL gains, or codebook reuse are reported as stronger function expressivity without a separating construction or held-out functional test.
- **Offline corpus contamination:** architectures, trajectories, performance labels, or repair traces used for pretraining reappear in the "autonomous" evaluation under different names or near-isomorphic forms.
- **Lineage discontinuity:** a descendant is selected from an external search or manually patched artifact instead of arising through the declared causal edit/commit loop.
- **Product metric overclaim:** a useful application result is reported as evidence for the full proposed mechanism even though a simpler baseline, fixed architecture, or conventional training route could explain it.

The conclusion must state which false-win paths were closed and which remain residual risks.

## L. Theory-Package Conflict Decomposition

When prediction and observation disagree, do not ask only "theory or experiment?" Check:

1. Was the theorem or derivation stated correctly?
2. Did the experiment instantiate its premises?
3. Did the implementation realize the proposed object?
4. Did optimization access the relevant solution?
5. Did the metric observe the predicted quantity?
6. Did the baseline possess an alternate route?
7. Was the effect too small relative to noise?
8. Is the theory valid only in another scale or limit?
9. Is the core theory false?

Each branch needs a discriminating test and a cost estimate.

Bad results test the whole theory package, not the core theory alone:

```text
core theory + auxiliary assumptions + implementation + optimization + measurement + baseline relation -> observation
```

Treat stable, reproducible contradiction as a theory-discovery entry point. A minimal theory extension should locate the missing link in the theory package and explain both the original prediction and the anomalous result.

## M. Research Memory

Maintain a research tree, not only a linear ledger. Research programs branch: one early assumption, code path, measurement choice, or dataset construction can become the root of many later experiments. If that root is later found wrong, the dependent subtree should be marked invalid or noisy as a group.

Use progressive disclosure: the tree should be compact at the top level, with details stored on nodes only when they carry decision-relevant information. Follow the minimum-description / maximum-information principle.

Store the research tree in a git-tracked structured file. Recommended default: `research_tree.json` near the research ledger or project reports. The checked-out file should represent the latest live research state. Git history is the reversible archive: pruning a subtree, marking it noisy, or replacing a branch should be committed so older versions remain recoverable.

Use git for:

- rollback when a later discovery invalidates a foundational node;
- comparing a pruned subtree against the replacement branch;
- linking node changes to commits, runs, or reports;
- auditing when a conclusion entered or left the admissible research state.

Each node should record at least:

- time or commit/run reference;
- motivation;
- what changed or was tested;
- conclusion;
- unresolved issues;
- parent node;
- dependent child nodes;
- invalidation condition.

Maintain a ledger containing:

- hypotheses and versions;
- predictions with timestamps or commit references;
- completed tests;
- killed hypotheses;
- unresolved anomalies;
- changes to auxiliary assumptions;
- reasons for each research decision.

When a node is invalidated, do not silently delete its descendants. Mark the node and dependent subtree as pruned, noisy, superseded, or still partially reusable. State which conclusions are no longer admissible and which measurements remain valid.

If deleting a subtree from the current tree improves clarity, do it only after recording the pruning reason and committing the change. Deletion is acceptable because git makes it reversible; untracked deletion is not.

Do not rewrite old predictions after observing results. Add amendments instead.
