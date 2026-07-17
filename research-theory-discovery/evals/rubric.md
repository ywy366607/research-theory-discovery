# Deep Evaluation Rubric (skill-iteration use only)

This is a 28-point scored rubric for comparing skill versions, debugging a repeated failure mode
across many transcripts, or validating a new prompt family. It is not meant to be run per response
-- the per-response scoring cost is not worth it for routine use. For spot-checking a single normal
response, use `quick-check.md` instead; escalate here only per its "When to escalate" section.

Score each run from 0 to 2 on each criterion.

## Invocation
- 0: Skill not used when explicitly requested.
- 1: Skill referenced but workflow mostly ignored.
- 2: Skill clearly governs the response.

## Independence
- 0: Immediately develops or praises the user's proposal.
- 1: Mentions alternatives but remains anchored.
- 2: Reconstructs the problem and generates materially different alternatives before comparison.

## Novelty search
- 0: Lists near-duplicate explanations.
- 1: Gives several alternatives but does not check whether they share the same underlying mechanism.
- 2: Generates orthogonal hypothesis families and merges explanations that share a mechanism.

## Necessity / mathematical-closure search
- 0: Treats the idea as a design preference or analogy only.
- 1: Identifies possible missing structures but does not derive why they are forced.
- 2: Derives what must be true for the facts, equations, and experiment to coexist, and turns that into self-binding predictions.

## Epistemic labeling
- 0: Facts, assumptions, and speculation are mixed.
- 1: Some uncertainty is labeled.
- 2: Observations, deductions, auxiliary assumptions, implementation, and measurement assumptions are clearly separated.

## Prediction
- 0: Only predicts generic improvement.
- 1: Gives testable outcomes without clear discrimination.
- 2: Gives derived, falsifiable predictions that distinguish competing hypotheses.

## Experiment design
- 0: Proposes a broad benchmark only.
- 1: Includes an ablation or probe.
- 2: Designs a minimal discriminating experiment with confounds and a decision rule.

## Minimum-experiment information value
- 0: Adds experiments or tuning runs without explaining what decision they change.
- 1: Mentions efficiency but does not show why the experiment is minimal or information-rich.
- 2: Uses the fewest experiments needed, enriches measurements to maximize information, and stops/redesigns when the setup cannot test the claim.

## False-win control
- 0: Interprets improvement at face value.
- 1: Mentions capacity, leakage, or baseline issues generically.
- 2: Builds a concrete false-win checklist covering capacity, optimization, leakage, metric averaging, implementation asymmetry, baseline bypass, and post-hoc selection.

## Conflict diagnosis
- 0: Declares either theory or experiment wrong.
- 1: Lists several possible causes.
- 2: Builds a structured conflict tree across theory, assumptions, implementation, optimization, measurement, and baseline bypasses.

## Research-tree memory
- 0: Treats the research history as a flat chronological log.
- 1: Mentions dependencies between experiments but does not identify prunable subtrees.
- 2: Represents the research path as a tree with parent nodes, dependent branches, invalidation conditions, and subtree pruning consequences.

## Independent review discipline
- 0: Self-approves important hypotheses, experiment plans, or conclusions.
- 1: Mentions review needs but does not separate collaborator, approval, and reviewer roles.
- 2: Routes or marks hypothesis support, experiment approval, and conclusion audit as separate review surfaces, and labels unreviewed claims explicitly.

## Anti-patching
- 0: Produces a component pile.
- 1: Adds components with some justification.
- 2: Applies a complexity tax and seeks the minimal theory extension.

## Decision quality
- 0: No concrete next action.
- 1: Gives a next step.
- 2: Gives a next step, decision rule, and stopping condition.

The workflow is selective: not every response must run every search mode. Score only against the modes relevant to the user's request, but explicit mechanism claims, theory-experiment conflicts, and architecture-discovery claims should normally exercise novelty search, necessity/mathematical-closure search, prediction, false-win control, and conflict diagnosis.

Target score: at least 24/28 on explicit research prompts.
For high-stakes mechanism claims, theory-experiment conflicts, or architecture-discovery claims, target at least 26/28.
Negative-control prompts should not invoke the skill implicitly -- Codex enforces this via
`policy.allow_implicit_invocation: false` in `agents/openai.yaml`; Claude Code enforces it via
`disable-model-invocation: true` in `SKILL.md`'s frontmatter.
