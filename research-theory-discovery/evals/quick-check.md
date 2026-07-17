# Quick Check (day-to-day use)

Use this for spot-checking a single response. It's pass/fail, not scored — if something fails,
say what's missing and move on. Don't run the full `rubric.md` for routine use; that one is for
skill-iteration sessions, not per-response grading (see its header).

Pick only the checks relevant to what the request actually needed. A one-off epistemic-labeling
question doesn't need a false-win checklist; a mechanism claim usually needs most of these.

- [ ] **Not anchored** -- if the user proposed a mechanism, the response reconstructed the problem
  and generated real alternatives before treating that mechanism as favored.
- [ ] **Orthogonal, not padded** -- hypotheses differ in underlying structure, not just wording;
  near-duplicates were merged into one family.
- [ ] **Necessity isn't inflated** -- nothing is called "necessary" without a derivation showing
  what breaks without it. "Possible" and "useful" are used when that's all that's earned.
- [ ] **Predictions came before results** -- if the response makes a prediction, it's falsifiable
  and stated as binding *before* the decisive result, not fitted after seeing it.
- [ ] **False-win paths addressed** -- for any claimed positive result, at least the paths relevant
  to that kind of claim (capacity/budget, leakage, baseline bypass, implementation asymmetry, ...)
  were checked, not just asserted away.
- [ ] **Conclusion isn't self-approved** -- for a costly or high-stakes claim, review status is
  stated (and marked unreviewed if no independent surface was actually used).
- [ ] **Ends with a decision** -- a concrete next action, decision rule, and stopping condition, not
  just more discussion.

If the session is long-running: also confirm `research_tree.json` was actually updated (not just
described) for any node-worthy conclusion. Skip this in a repo where the harness (see
`harness/README.md`) already enforces it via hooks -- that's the point of automating it.

## When to escalate to the full rubric

Run `rubric.md` instead of this checklist when: you're revising the skill itself and need to
compare before/after quality, you're debugging a repeated failure mode across many runs, or you're
validating a new prompt family in `prompts.csv`. Not for grading a single ordinary response.
