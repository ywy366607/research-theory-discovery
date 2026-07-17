# Reusable Output Schemas

## Contents

Compact Research Map -- Prediction Registration -- Theory-Package Ledger -- False-Win Checklist --
Conflict Tree -- Research Tree Node (+ Subtree Pruning Record)

## Compact Research Map

### Research State

- Observations:
- Constraints:
- Current hypothesis:
- Unknowns:
- Measurement risks:

### Competing Hypotheses

| ID | Core claim | Hidden assumptions | Unique prediction | Cheapest falsifier |
|---|---|---|---|---|

### Novelty Hypothesis Matrix

| ID | Hypothesis family | State variables | Causal direction | Geometry/scale | Information-flow path | Shares underlying mechanism with others? |
|---|---|---|---|---|---|---|

### Necessity Analysis

- Merely possible:
- Appears useful:
- Mathematically or empirically forced:
- Missing derivation:

### Next Action

- Experiment:
- Information gained:
- Decision rule:
- Stopping condition:
- Review status:

### Minimum-experiment check

- Decision this experiment can change:
- Why fewer experiments are insufficient:
- Why this experiment is not redundant:
- Measurements to add for maximum information:
- Structural search-space risk:
- Stop/redesign trigger:

### Independent review status

| Review surface | Reviewer / agent | Status | Main concerns | Decision |
|---|---|---|---|---|
| Hypothesis collaborator |  | unreviewed / reviewed |  |  |
| Experiment approval committee |  | unreviewed / approved / rejected |  |  |
| Conclusion reviewer |  | unreviewed / accepted / weakened / rejected |  |  |

## Prediction Registration

### Prediction ID

`P-YYYYMMDD-NN`

### Theory and Version

- Hypothesis:
- Commit or document version:
- Domain:

### Derivation

1.
2.
3.

### Auxiliary Assumptions

-

### Measurement

-

### Expected Observation

-

### Falsifying Observation

-

### Ambiguous Outcomes

-

### Strongest Alternative Explanation

-

## Theory-Package Ledger

### Tested Claim

```text
core theory + auxiliary assumptions + implementation + optimization + measurement + baseline relation -> observation
```

### Package Decomposition

| Link | Current claim | Evidence class | Possible failure mode | Cheapest check |
|---|---|---|---|---|
| Core theory |  |  |  |  |
| Auxiliary assumptions |  |  |  |  |
| Implementation |  |  |  |  |
| Optimization |  |  |  |  |
| Measurement |  |  |  |  |
| Baseline relation |  |  |  |  |

## False-Win Checklist

| Path | Closed? | Evidence | Residual risk |
|---|---|---|---|
| Extra capacity / training budget |  |  |  |
| Optimization change |  |  |  |
| Data leakage |  |  |  |
| Metric averaging |  |  |  |
| Hidden recurrence / extra passes |  |  |  |
| Implementation asymmetry |  |  |  |
| Baseline bypass |  |  |  |
| Reachability mistaken for discovery |  |  |  |
| Serialization mistaken for generation |  |  |  |
| Handwritten scaffold substitution |  |  |  |
| Teacher or oracle leakage |  |  |  |
| Vocabulary / codebook leakage |  |  |  |
| Search-budget mismatch |  |  |  |
| Macro prior not charged |  |  |  |
| Offline corpus contamination |  |  |  |
| Lineage discontinuity |  |  |  |

## Conflict Tree

### Conflict

- Predicted:
- Observed:
- Difference magnitude:
- Uncertainty:

| Branch | Failure location | Evidence for | Evidence against | Discriminating test | Cost |
|---|---|---|---|---|---|

### Resolution Status

- Core theory:
- Auxiliary assumptions:
- Implementation:
- Optimization:
- Measurement:
- Baseline bypass:

## Research Tree Node

### JSON input for visualization

```json
{
  "title": "Research Tree",
  "nodes": [
    {
      "id": "N001",
      "parent": null,
      "title": "Initial hypothesis",
      "status": "active",
      "time": "2026-07-17 / commit abc123",
      "motivation": "Why this node exists",
      "action": "What changed or was tested",
      "conclusion": "What was learned",
      "issues": ["Open issue"],
      "invalidation": "What would invalidate this node"
    }
  ]
}
```

Render with:

```bash
python scripts/render_research_tree.py tree.json tree.html
```

### Node

- Tree file:
- Node ID:
- Parent ID:
- Time / commit / run:
- Motivation:
- What changed or was tested:
- Conclusion:
- Unresolved issues:
- Child nodes:
- Invalidation condition:
- Status: active / pruned / noisy / superseded / partially reusable
- Last tree commit:

### Subtree Pruning Record

- Tree file:
- Invalidated node:
- Reason:
- Dependent subtree:
- Conclusions no longer admissible:
- Measurements still valid:
- Replacement branch or next node:
- Pruning commit:
- Recovery note:
